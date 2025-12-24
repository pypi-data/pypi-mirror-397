"""
附件路由

提供附件管理的API接口，包括上传、下载、删除、查看等功能。
支持基于角色的权限控制和访问日志记录。
"""

from typing import Dict, Optional
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Query,
    Response,
    Depends,
    Request,
)
from neoxin_core.http import success_response, error_response
from neoxin_core.dependencies import require_authenticated
from .dependencies import (
    AttachmentServiceDep,
    ClientInfoDep,
    get_client_info,
    require_attach_permission,
    check_upload_permission,
)
from .schemas import (
    AttachmentRead,
    RoleAttachmentConfigRead,
    RoleAttachmentConfigCreate,
    RoleAttachmentConfigUpdate,
    AttachmentAccessLogRead,
    AttachmentAccessLogQuery,
)

router = APIRouter(
    prefix="/attachments",
    tags=["附件管理"],
)


@router.post("/upload")
async def upload_file(
    service: AttachmentServiceDep,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    storage_name: Optional[str] = None,
    path_prefix: Optional[str] = None,
    auth_info: Dict = Depends(require_attach_permission),
):
    """
    上传文件

    支持不同客户端类型的权限控制：
    - Web端：必须登录，最大100MB
    - 其他端：根据角色配置进行限制

    - **file**: 上传的文件
    - **description**: 文件描述（可选）
    - **storage_name**: 指定存储后端名称（可选，默认使用默认后端）
    - **path_prefix**: 存储路径前缀（可选）
    """
    try:
        user_dict = auth_info.get("user_dict")
        client_info = auth_info

        # 读取文件数据
        data = await file.read()
        file_size = len(data)
        content_type = file.content_type or "application/octet-stream"

        # 检查上传权限 (在 dependencies.py 中已经封装了逻辑)
        upload_perm = await check_upload_permission(
            file_size=file_size,
            content_type=content_type,
            service=service,
            client_info=client_info,
            user_dict=user_dict,
        )

        user_id = upload_perm.get("user_id")

        # 上传文件
        attachment = await service.upload(
            file_data=data,
            filename=file.filename or "unknown",
            content_type=content_type,
            description=description,
            uploader_id=user_id,
            storage_name=storage_name,
            path_prefix=path_prefix,
        )

        # 记录访问日志 (require_attach_permission 已经记录了一次通用的 access，这里记录具体 upload 动作)
        service.log_access(
            {
                "attachment_id": attachment.id,
                "user_id": user_id,
                "user_identifier": user_dict.get("username") if user_dict else None,
                "client_type": client_info["client_type"],
                "action": "upload",
                "ip_address": client_info["ip_address"],
                "user_agent": client_info["user_agent"],
                "file_size": file_size,
                "endpoint": client_info["endpoint"],
            }
        )

        return success_response(AttachmentRead.model_validate(attachment).model_dump())
    except HTTPException:
        raise
    except Exception as e:
        return error_response(str(e))


@router.get("/{attachment_id}")
async def get_attachment(
    service: AttachmentServiceDep,
    attachment_id: int,
    include_url: bool = Query(True, description="是否包含访问URL"),
    url_expires: int = Query(3600, description="URL过期时间（秒）"),
    auth_info: Dict = Depends(require_attach_permission),
):
    """
    获取附件信息

    - **attachment_id**: 附件ID
    - **include_url**: 是否包含访问URL
    - **url_expires**: URL过期时间（秒）
    """
    try:
        user_dict = auth_info.get("user_dict")
        client_info = auth_info

        attachment = service.get(attachment_id)
        if not attachment:
            return error_response("附件不存在", code=404)

        data = AttachmentRead.model_validate(attachment).model_dump()

        if include_url:
            try:
                url = await service.get_url(attachment_id, expires=url_expires)
                data["url"] = url
            except Exception as e:
                data["url"] = None
                data["url_error"] = str(e)

        # 记录查看日志
        service.log_access(
            {
                "attachment_id": attachment_id,
                "user_id": user_dict.get("id") if user_dict else None,
                "user_identifier": user_dict.get("username") if user_dict else None,
                "client_type": client_info["client_type"],
                "action": "view",
                "ip_address": client_info["ip_address"],
                "user_agent": client_info["user_agent"],
                "file_size": attachment.size,
                "endpoint": client_info["endpoint"],
            }
        )

        return success_response(data)
    except HTTPException:
        raise
    except Exception as e:
        return error_response(str(e))


@router.get("/{attachment_id}/download")
async def download_file(
    attachment_id: int,
    service: AttachmentServiceDep,
    auth_info: Dict = Depends(require_attach_permission),
):
    """
    下载文件

    - **attachment_id**: 附件ID
    """
    try:
        user_dict = auth_info.get("user_dict")
        client_info = auth_info

        attachment = service.get(attachment_id)
        if not attachment:
            raise HTTPException(status_code=404, detail="附件不存在")

        data = await service.download(attachment_id)

        # 记录下载日志
        service.log_access(
            {
                "attachment_id": attachment_id,
                "user_id": user_dict.get("id") if user_dict else None,
                "user_identifier": user_dict.get("username") if user_dict else None,
                "client_type": client_info["client_type"],
                "action": "download",
                "ip_address": client_info["ip_address"],
                "user_agent": client_info["user_agent"],
                "file_size": attachment.size,
                "endpoint": client_info["endpoint"],
            }
        )

        return Response(
            content=data,
            media_type=attachment.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{attachment.filename}"'
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/")
async def list_attachments(
    service: AttachmentServiceDep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    uploader_id: Optional[int] = Query(None, description="上传者ID过滤"),
    storage: Optional[str] = Query(None, description="存储类型过滤"),
    auth_info: Dict = Depends(require_attach_permission),
):
    """
    列出附件

    - **page**: 页码
    - **size**: 每页数量
    - **uploader_id**: 上传者ID过滤（可选）
    - **storage**: 存储类型过滤（可选）
    """
    try:
        items, total = service.list(
            page=page,
            size=size,
            uploader_id=uploader_id,
            storage=storage,
        )

        return success_response(
            {
                "items": [AttachmentRead.model_validate(i).model_dump() for i in items],
                "pagination": {
                    "total": total,
                    "page": page,
                    "size": size,
                    "pages": (total + size - 1) // size,
                },
            }
        )
    except Exception as e:
        return error_response(str(e))


@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    service: AttachmentServiceDep,
    delete_file: bool = Query(True, description="是否同时删除文件"),
    auth_info: Dict = Depends(require_attach_permission),
):
    """
    删除附件

    - **attachment_id**: 附件ID
    - **delete_file**: 是否同时删除文件
    """
    try:
        user_dict = auth_info.get("user_dict")
        client_info = auth_info

        attachment = service.get(attachment_id)
        if not attachment:
            return error_response("附件不存在", code=404)

        success = await service.delete(attachment_id, delete_file=delete_file)
        if not success:
            return error_response("附件删除失败", code=500)

        # 记录删除日志
        service.log_access(
            {
                "attachment_id": attachment_id,
                "user_id": user_dict.get("id") if user_dict else None,
                "user_identifier": user_dict.get("username") if user_dict else None,
                "client_type": client_info["client_type"],
                "action": "delete",
                "ip_address": client_info["ip_address"],
                "user_agent": client_info["user_agent"],
                "file_size": attachment.size,
                "endpoint": client_info["endpoint"],
            }
        )

        return success_response({"deleted": True})
    except HTTPException:
        raise
    except Exception as e:
        return error_response(str(e))


@router.get("/{attachment_id}/exists")
async def check_file_exists(
    attachment_id: int,
    service: AttachmentServiceDep,
):
    """
    检查附件文件是否存在

    - **attachment_id**: 附件ID
    """
    try:
        exists = await service.exists(attachment_id)
        return success_response({"exists": exists})
    except Exception as e:
        return error_response(str(e))


# ==================== 角色附件配置管理接口 ====================


@router.get("/config/roles", dependencies=[Depends(require_authenticated)])
async def list_role_configs(
    service: AttachmentServiceDep,
    is_active: Optional[bool] = Query(None, description="是否只返回激活的配置"),
):
    """
    获取所有角色附件配置列表

    - **is_active**: 是否只返回激活的配置
    """
    try:
        configs = service.list_role_configs(is_active=is_active)
        return success_response(
            {
                "items": [
                    RoleAttachmentConfigRead.model_validate(c).model_dump()
                    for c in configs
                ]
            }
        )
    except Exception as e:
        return error_response(str(e))


@router.get("/config/roles/{role_id}", dependencies=[Depends(require_authenticated)])
async def get_role_config(
    role_id: int,
    service: AttachmentServiceDep,
):
    """
    获取指定角色的附件配置

    - **role_id**: 角色ID
    """
    try:
        config = service.get_role_config(role_id)
        if not config:
            return error_response("角色配置不存在", code=404)
        return success_response(
            RoleAttachmentConfigRead.model_validate(config).model_dump()
        )
    except Exception as e:
        return error_response(str(e))


@router.post("/config/roles", dependencies=[Depends(require_authenticated)])
async def create_role_config(
    config_data: RoleAttachmentConfigCreate,
    service: AttachmentServiceDep,
):
    """
    创建角色附件配置

    需要管理员权限
    """
    try:
        config = service.create_role_config(config_data.model_dump())
        return success_response(
            RoleAttachmentConfigRead.model_validate(config).model_dump()
        )
    except Exception as e:
        return error_response(str(e))


@router.put("/config/roles/{config_id}", dependencies=[Depends(require_authenticated)])
async def update_role_config(
    config_id: int,
    update_data: RoleAttachmentConfigUpdate,
    service: AttachmentServiceDep,
):
    """
    更新角色附件配置

    需要管理员权限

    - **config_id**: 配置ID
    """
    try:
        config = service.update_role_config(
            config_id, update_data.model_dump(exclude_unset=True)
        )
        if not config:
            return error_response("配置不存在", code=404)
        return success_response(
            RoleAttachmentConfigRead.model_validate(config).model_dump()
        )
    except Exception as e:
        return error_response(str(e))


@router.delete(
    "/config/roles/{config_id}", dependencies=[Depends(require_authenticated)]
)
async def delete_role_config(
    config_id: int,
    service: AttachmentServiceDep,
):
    """
    删除角色附件配置

    需要管理员权限

    - **config_id**: 配置ID
    """
    try:
        success = service.delete_role_config(config_id)
        if not success:
            return error_response("配置不存在", code=404)
        return success_response({"deleted": True})
    except Exception as e:
        return error_response(str(e))


# ==================== 访问日志查询接口 ====================


@router.get("/logs", dependencies=[Depends(require_authenticated)])
async def get_access_logs(
    service: AttachmentServiceDep,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    attachment_id: Optional[int] = Query(None, description="附件ID过滤"),
    user_id: Optional[int] = Query(None, description="用户ID过滤"),
    client_type: Optional[str] = Query(None, description="客户端类型过滤"),
    action: Optional[str] = Query(None, description="操作类型过滤"),
):
    """
    查询附件访问日志

    需要管理员或运维权限

    - **page**: 页码
    - **size**: 每页数量
    - **attachment_id**: 附件ID过滤（可选）
    - **user_id**: 用户ID过滤（可选）
    - **client_type**: 客户端类型过滤（可选）
    - **action**: 操作类型过滤（可选）
    """
    try:
        logs, total = service.get_access_logs(
            attachment_id=attachment_id,
            user_id=user_id,
            client_type=client_type,
            action=action,
            page=page,
            size=size,
        )

        return success_response(
            {
                "items": [
                    AttachmentAccessLogRead.model_validate(log).model_dump()
                    for log in logs
                ],
                "pagination": {
                    "total": total,
                    "page": page,
                    "size": size,
                    "pages": (total + size - 1) // size,
                },
            }
        )
    except Exception as e:
        return error_response(str(e))
