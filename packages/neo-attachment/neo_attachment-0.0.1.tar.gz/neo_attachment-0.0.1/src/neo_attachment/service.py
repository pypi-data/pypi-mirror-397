"""
附件服务

提供附件的存储与数据库操作。
"""

from typing import Optional, BinaryIO, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from neoxin_core.logging import get_logger
from .models import Attachment, RoleAttachmentConfig, AttachmentAccessLog
from neoxin_core.storage.base import StorageBackend, UploadResult
from neoxin_core.storage.manager import StorageManager


logger = get_logger("fastapi_attachment.service")


class AttachmentService:
    """附件服务类"""

    def __init__(self, db: Session, storage_manager: StorageManager):
        """
        初始化附件服务

        Args:
            db: 数据库会话
            storage_manager: 存储管理器
        """
        self.db = db
        self.storage_manager = storage_manager

    async def upload(
        self,
        file_data: bytes | BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        description: Optional[str] = None,
        uploader_id: Optional[int] = None,
        storage_name: Optional[str] = None,
        path_prefix: Optional[str] = None,
    ) -> Attachment:
        """
        上传文件

        Args:
            file_data: 文件数据
            filename: 文件名
            content_type: 内容类型
            description: 描述
            uploader_id: 上传者ID
            storage_name: 存储后端名称（None使用默认）
            path_prefix: 路径前缀

        Returns:
            Attachment: 附件实体
        """
        # 获取存储后端
        backend = self.storage_manager.get_backend(storage_name)

        # 上传到存储后端
        result: UploadResult = await backend.upload(
            file_data=file_data,
            filename=filename,
            content_type=content_type,
            path_prefix=path_prefix,
        )

        # 创建数据库记录
        attachment = Attachment(
            filename=filename,
            content_type=content_type or "application/octet-stream",
            size=result.size,
            path=result.path,
            description=description,
            uploader_id=uploader_id,
            storage=result.storage_type,
            storage_id=None,  # 可用于关联存储配置ID
        )

        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)

        logger.info(
            f"附件上传成功: id={attachment.id}, path={result.path}, storage={result.storage_type}"
        )

        return attachment

    async def download(self, attachment_id: int) -> bytes:
        """
        下载文件

        Args:
            attachment_id: 附件ID

        Returns:
            bytes: 文件数据
        """
        attachment = self.get(attachment_id)
        if not attachment:
            raise ValueError(f"附件不存在: {attachment_id}")

        # 获取存储后端
        backend = self._get_backend_for_attachment(attachment)

        # 从存储后端下载
        data = await backend.download(attachment.path)

        logger.info(f"附件下载成功: id={attachment_id}, size={len(data)}")

        return data

    async def get_url(
        self, attachment_id: int, expires: Optional[int] = 3600
    ) -> Optional[str]:
        """
        获取文件访问URL

        Args:
            attachment_id: 附件ID
            expires: 过期时间（秒）

        Returns:
            Optional[str]: 访问URL
        """
        attachment = self.get(attachment_id)
        if not attachment:
            raise ValueError(f"附件不存在: {attachment_id}")

        # 获取存储后端
        backend = self._get_backend_for_attachment(attachment)

        # 获取访问URL
        url = await backend.get_url(attachment.path, expires)

        return url

    def get(self, attachment_id: int) -> Optional[Attachment]:
        """
        获取附件

        Args:
            attachment_id: 附件ID

        Returns:
            Optional[Attachment]: 附件实体
        """
        return self.db.get(Attachment, attachment_id)

    def list(
        self,
        page: int = 1,
        size: int = 20,
        uploader_id: Optional[int] = None,
        storage: Optional[str] = None,
    ) -> Tuple[List[Attachment], int]:
        """
        列出附件

        Args:
            page: 页码
            size: 每页数量
            uploader_id: 上传者ID过滤
            storage: 存储类型过滤

        Returns:
            Tuple[List[Attachment], int]: (附件列表, 总数)
        """
        query = select(Attachment)

        # 应用过滤条件
        if uploader_id is not None:
            query = query.where(Attachment.uploader_id == uploader_id)
        if storage:
            query = query.where(Attachment.storage == storage)

        # 获取总数
        total = self.db.scalar(select(func.count()).select_from(query.subquery()))

        # 分页查询
        query = query.offset((page - 1) * size).limit(size)
        items = list(self.db.scalars(query).all())

        return items, total or 0

    async def delete(self, attachment_id: int, delete_file: bool = True) -> bool:
        """
        删除附件

        Args:
            attachment_id: 附件ID
            delete_file: 是否同时删除文件

        Returns:
            bool: 是否成功
        """
        attachment = self.get(attachment_id)
        if not attachment:
            return False

        # 删除文件
        if delete_file:
            try:
                backend = self._get_backend_for_attachment(attachment)
                await backend.delete(attachment.path)
                logger.info(
                    f"附件文件删除成功: id={attachment_id}, path={attachment.path}"
                )
            except Exception as e:
                logger.error(f"附件文件删除失败: id={attachment_id}, {e}")

        # 删除数据库记录
        self.db.delete(attachment)
        self.db.commit()

        logger.info(f"附件记录删除成功: id={attachment_id}")

        return True

    async def exists(self, attachment_id: int) -> bool:
        """
        检查附件文件是否存在

        Args:
            attachment_id: 附件ID

        Returns:
            bool: 是否存在
        """
        attachment = self.get(attachment_id)
        if not attachment:
            return False

        backend = self._get_backend_for_attachment(attachment)
        return await backend.exists(attachment.path)

    def _get_backend_for_attachment(self, attachment: Attachment) -> StorageBackend:
        """
        根据附件获取对应的存储后端

        Args:
            attachment: 附件实体

        Returns:
            StorageBackend: 存储后端
        """
        # 简单实现：使用默认后端
        # 可以扩展为根据 attachment.storage 或 attachment.storage_id 选择特定后端
        return self.storage_manager.get_backend()

    # ==================== 角色附件配置相关方法 ====================

    def get_role_config(self, role_id: int) -> Optional[RoleAttachmentConfig]:
        """
        获取角色的附件配置

        Args:
            role_id: 角色ID

        Returns:
            Optional[RoleAttachmentConfig]: 角色附件配置
        """
        query = select(RoleAttachmentConfig).where(
            and_(
                RoleAttachmentConfig.role_id == role_id,
                RoleAttachmentConfig.is_active == True,
            )
        )
        return self.db.scalar(query)

    def create_role_config(self, config_data: dict) -> RoleAttachmentConfig:
        """
        创建角色附件配置

        Args:
            config_data: 配置数据

        Returns:
            RoleAttachmentConfig: 创建的配置
        """
        config = RoleAttachmentConfig(**config_data)
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        logger.info(f"角色附件配置创建成功: role_id={config.role_id}, id={config.id}")
        return config

    def update_role_config(
        self, config_id: int, update_data: dict
    ) -> Optional[RoleAttachmentConfig]:
        """
        更新角色附件配置

        Args:
            config_id: 配置ID
            update_data: 更新数据

        Returns:
            Optional[RoleAttachmentConfig]: 更新后的配置
        """
        config = self.db.get(RoleAttachmentConfig, config_id)
        if not config:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)

        self.db.commit()
        self.db.refresh(config)
        logger.info(f"角色附件配置更新成功: id={config_id}")
        return config

    def delete_role_config(self, config_id: int) -> bool:
        """
        删除角色附件配置

        Args:
            config_id: 配置ID

        Returns:
            bool: 是否成功
        """
        config = self.db.get(RoleAttachmentConfig, config_id)
        if not config:
            return False

        self.db.delete(config)
        self.db.commit()
        logger.info(f"角色附件配置删除成功: id={config_id}")
        return True

    def list_role_configs(
        self, is_active: Optional[bool] = None
    ) -> List[RoleAttachmentConfig]:
        """
        列出所有角色附件配置

        Args:
            is_active: 是否只返回激活的配置

        Returns:
            List[RoleAttachmentConfig]: 配置列表
        """
        query = select(RoleAttachmentConfig)
        if is_active is not None:
            query = query.where(RoleAttachmentConfig.is_active == is_active)

        return list(self.db.scalars(query).all())

    def check_upload_frequency(
        self,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        seconds: int = 60,
        max_requests: int = 10,
    ) -> Tuple[bool, Optional[str]]:
        """
        检查上传频率（防止恶意上传）

        Args:
            user_id: 用户ID
            ip_address: IP地址
            seconds: 时间窗口（秒）
            max_requests: 窗口内允许的最大请求数

        Returns:
            Tuple[bool, Optional[str]]: (是否允许, 错误信息)
        """
        time_limit = datetime.now() - timedelta(seconds=seconds)

        # 构建查询条件：时间窗口内的上传记录
        conditions = [
            AttachmentAccessLog.action == "upload",
            AttachmentAccessLog.created_at >= time_limit,
        ]

        if user_id:
            conditions.append(AttachmentAccessLog.user_id == user_id)
        elif ip_address:
            conditions.append(AttachmentAccessLog.ip_address == ip_address)
        else:
            return True, None

        recent_count = self.db.scalar(
            select(func.count())
            .select_from(AttachmentAccessLog)
            .where(and_(*conditions))
        )

        if recent_count and recent_count >= max_requests:
            return False, f"上传过于频繁，请在 {seconds} 秒后重试"

        return True, None

    def check_upload_permission(
        self,
        role_id: int,
        file_size: int,
        content_type: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        检查上传权限

        Args:
            role_id: 角色ID
            file_size: 文件大小
            content_type: 文件MIME类型
            user_id: 用户ID（用于检查每日限制）
            ip_address: IP地址（用于频率限制）

        Returns:
            Tuple[bool, Optional[str]]: (是否允许, 错误信息)
        """
        # 1. 拦截检测：基础频率限制（例如：1分钟内最多10次上传）
        allowed_freq, error_freq = self.check_upload_frequency(
            user_id=user_id, ip_address=ip_address, seconds=60, max_requests=10
        )
        if not allowed_freq:
            return False, error_freq

        config = self.get_role_config(role_id)
        if not config:
            # 如果没有配置，使用默认限制（100MB）
            if file_size > 104857600:
                return False, "文件大小超过默认限制（100MB）"
            return True, None

        # 检查文件大小
        if file_size > config.max_file_size:
            return False, f"文件大小超过限制（{config.max_file_size / 1048576:.2f}MB）"

        # 检查MIME类型
        if config.allowed_mime_types:
            allowed_types = [t.strip() for t in config.allowed_mime_types.split(",")]
            if content_type not in allowed_types:
                return False, f"不允许的文件类型: {content_type}"

        # 检查每日上传次数限制
        if config.max_daily_uploads is not None and user_id is not None:
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_count = self.db.scalar(
                select(func.count())
                .select_from(AttachmentAccessLog)
                .where(
                    and_(
                        AttachmentAccessLog.user_id == user_id,
                        AttachmentAccessLog.action == "upload",
                        AttachmentAccessLog.created_at >= today_start,
                    )
                )
            )
            if today_count and today_count >= config.max_daily_uploads:
                return False, f"已达到每日上传次数限制（{config.max_daily_uploads}次）"

        # 检查每日上传总大小限制
        if config.max_daily_size is not None and user_id is not None:
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_size = (
                self.db.scalar(
                    select(func.sum(AttachmentAccessLog.file_size))
                    .select_from(AttachmentAccessLog)
                    .where(
                        and_(
                            AttachmentAccessLog.user_id == user_id,
                            AttachmentAccessLog.action == "upload",
                            AttachmentAccessLog.created_at >= today_start,
                        )
                    )
                )
                or 0
            )
            if today_size + file_size > config.max_daily_size:
                return (
                    False,
                    f"已达到每日上传总大小限制（{config.max_daily_size / 1048576:.2f}MB）",
                )

        return True, None

    # ==================== 访问日志相关方法 ====================

    def log_access(self, log_data: dict) -> AttachmentAccessLog:
        """
        记录附件访问日志

        Args:
            log_data: 日志数据

        Returns:
            AttachmentAccessLog: 创建的日志记录
        """
        log = AttachmentAccessLog(**log_data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_access_logs(
        self,
        attachment_id: Optional[int] = None,
        user_id: Optional[int] = None,
        client_type: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[AttachmentAccessLog], int]:
        """
        查询访问日志

        Args:
            attachment_id: 附件ID过滤
            user_id: 用户ID过滤
            client_type: 客户端类型过滤
            action: 操作类型过滤
            start_date: 开始时间
            end_date: 结束时间
            page: 页码
            size: 每页数量

        Returns:
            Tuple[List[AttachmentAccessLog], int]: (日志列表, 总数)
        """
        query = select(AttachmentAccessLog)

        # 应用过滤条件
        conditions = []
        if attachment_id is not None:
            conditions.append(AttachmentAccessLog.attachment_id == attachment_id)
        if user_id is not None:
            conditions.append(AttachmentAccessLog.user_id == user_id)
        if client_type:
            conditions.append(AttachmentAccessLog.client_type == client_type)
        if action:
            conditions.append(AttachmentAccessLog.action == action)
        if start_date:
            conditions.append(AttachmentAccessLog.created_at >= start_date)
        if end_date:
            conditions.append(AttachmentAccessLog.created_at <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        # 获取总数
        total = self.db.scalar(select(func.count()).select_from(query.subquery()))

        # 分页查询，按创建时间倒序
        query = (
            query.order_by(AttachmentAccessLog.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        items = list(self.db.scalars(query).all())

        return items, total or 0
