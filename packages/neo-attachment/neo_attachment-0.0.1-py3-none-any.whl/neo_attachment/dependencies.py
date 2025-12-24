from typing import Annotated, Optional, Dict, Any
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from .service import AttachmentService
from neoxin_core.storage.manager import get_storage_manager, StorageManager
from neoxin_core.dependencies import get_db

# 从 neo_account 导入依赖，需要确保 neo_account 在 Python 路径中
try:
    from neo_account.dependencies import get_current_user_optional
    from neo_account.models import User, Role
except ImportError:
    # 允许降级处理或 Mock
    get_current_user_optional = lambda: None
    User = None
    Role = None


def get_attachment_service(
    db: Session = Depends(get_db),
    storage_manager: StorageManager = Depends(get_storage_manager),
) -> AttachmentService:
    """
    获取附件服务实例（用于依赖注入）

    Args:
        db: 数据库会话
        storage_manager: 存储管理器

    Returns:
        AttachmentService: 附件服务实例
    """
    return AttachmentService(db=db, storage_manager=storage_manager)


# 类型注解，方便在路由中使用
AttachmentServiceDep = Annotated[AttachmentService, Depends(get_attachment_service)]


def detect_client_type(request: Request) -> str:
    """
    从User-Agent检测客户端类型

    Args:
        request: FastAPI请求对象

    Returns:
        str: 客户端类型 (web/app/h5/wechat_miniprogram)
    """
    user_agent = request.headers.get("user-agent", "").lower()

    # 微信小程序
    if "miniprogram" in user_agent or "micromessenger" in user_agent:
        if "miniprogram" in user_agent:
            return "wechat_miniprogram"
        return "wechat"

    # 移动端APP
    if any(keyword in user_agent for keyword in ["android", "iphone", "ipad"]):
        # 如果包含自定义APP标识
        if "app" in user_agent or "mobile" in user_agent:
            return "app"
        # H5页面
        return "h5"

    # 默认为Web端
    return "web"


def get_client_info(request: Request) -> Dict:
    """
    获取客户端信息

    Args:
        request: FastAPI请求对象

    Returns:
        Dict: 包含客户端类型、IP、User-Agent等信息
    """
    client_type = detect_client_type(request)

    # 获取真实IP（考虑代理）
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else None

    return {
        "client_type": client_type,
        "ip_address": ip_address,
        "user_agent": request.headers.get("user-agent"),
        "endpoint": str(request.url.path),
    }


ClientInfoDep = Annotated[Dict, Depends(get_client_info)]


async def require_attach_permission(
    request: Request,
    service: AttachmentServiceDep,
    user: Any = Depends(get_current_user_optional),
) -> Dict:
    """
    控制用户接口访问权限，通过user-agent判断用户类型进行分类控制：
    1、web端必须进行用户登录凭证验证
    2、记录所有客户端的访问信息到日志中

    Args:
        request: FastAPI请求对象
        service: 附件服务
        user: 当前用户（可选）

    Returns:
        Dict: 包含用户信息和客户端信息
    """
    client_info = get_client_info(request)

    # Web端必须登录 check
    if client_info["client_type"] == "web" and not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Web端需要登录"
        )

    # 转换 User 为 dict 方便后续使用
    user_dict = None
    if user:
        user_dict = {
            "id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
            "roles": (
                [r.id for r in getattr(user, "roles", [])]
                if hasattr(user, "roles")
                else []
            ),
        }

    user_id = user_dict["id"] if user_dict else None
    user_identifier = user_dict["username"] if user_dict else None

    # 获取路径参数中的 attachment_id (如果有)
    attachment_id = request.path_params.get("attachment_id")
    try:
        attachment_id = int(attachment_id) if attachment_id else None
    except ValueError:
        attachment_id = None

    # 记录通用访问日志 (非上下载的动作，如查看、列表等)
    # 对于 upload/download 路由内部会有更详细的针对性记录
    service.log_access(
        {
            "attachment_id": attachment_id or 0,
            "user_id": user_id,
            "user_identifier": user_identifier,
            "client_type": client_info["client_type"],
            "action": "access",  # 表示通用进入
            "ip_address": client_info["ip_address"],
            "user_agent": client_info["user_agent"],
            "endpoint": client_info["endpoint"],
        }
    )

    return {
        **client_info,
        "user_id": user_id,
        "user_identifier": user_identifier,
        "user_dict": user_dict,
    }


async def check_upload_permission(
    file_size: int,
    content_type: str,
    service: AttachmentServiceDep,
    client_info: Dict,
    user_dict: Optional[Dict] = None,
) -> Dict:
    """
    控制接口上传权限，通过user-agent判断用户类型进行分类控制：
    1、检测用户上传频率，防止恶意上传
    2、web端大小限制单个文件不超过 100M
    3、其他类型用户根据配置的角色与附件的管理表配置控制
    4、未登录用户则通过与访客角色[GUEST]的关联配置进行控制

    Args:
        file_size: 文件大小（字节）
        content_type: 文件MIME类型
        service: 附件服务
        client_info: 客户端信息
        user_dict: 用户信息字典

    Returns:
        Dict: 权限检查结果

    Raises:
        HTTPException: 权限检查失败时抛出
    """
    # Web端默认限制100MB
    if client_info["client_type"] == "web":
        if file_size > 104857600:  # 100MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Web端文件大小不能超过100MB",
            )

    # 获取用户角色ID，未登录使用访客角色
    role_id = None
    user_id = user_dict.get("id") if user_dict else None

    if user_dict and user_dict.get("roles"):
        # 如果有角色，使用第一个角色ID（可以根据业务逻辑调整为更复杂的选择逻辑）
        role_id = user_dict["roles"][0]
    else:
        # 获取访客角色ID（GUEST）
        if Role:
            guest_role = service.db.scalar(select(Role).where(Role.code == "GUEST"))
            if guest_role:
                role_id = guest_role.id

        # fallback
        if role_id is None:
            role_id = 3  # 默认兜底

    if role_id:
        # 检查上传权限（包含频率校验）
        allowed, error_msg = service.check_upload_permission(
            role_id=role_id,
            file_size=file_size,
            content_type=content_type,
            user_id=user_id,
            ip_address=client_info.get("ip_address"),
        )

        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)

    return {
        "allowed": True,
        "role_id": role_id,
        "user_id": user_id,
    }
