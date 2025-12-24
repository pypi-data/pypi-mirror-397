"""
附件模型

定义附件的数据库模型。
"""

from sqlalchemy import String, Integer, BigInteger, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from neoxin_core.db import Base


class Attachment(Base):
    """附件实体"""

    __tablename__ = "attachments"

    filename: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="文件名"
    )
    content_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="内容类型"
    )
    size: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="文件大小（字节）"
    )
    path: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="存储路径/Key"
    )
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="描述"
    )
    uploader_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="上传者ID"
    )
    storage: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="存储类型"
    )
    storage_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="存储配置ID（可选）"
    )


class RoleAttachmentConfig(Base):
    """角色附件配置实体 - 控制不同角色的附件上传权限"""

    __tablename__ = "role_attachment_configs"

    role_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="角色ID"
    )
    max_file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=104857600,
        comment="最大文件大小（字节），默认100MB",
    )
    allowed_mime_types: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="允许的MIME类型，逗号分隔，为空表示不限制"
    )
    max_daily_uploads: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="每日最大上传次数，为空表示不限制"
    )
    max_daily_size: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, comment="每日最大上传总大小（字节），为空表示不限制"
    )
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否启用")
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="配置描述"
    )


class AttachmentAccessLog(Base):
    """附件访问日志实体 - 记录不同客户端类型的访问信息"""

    __tablename__ = "attachment_access_logs"

    attachment_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="附件ID"
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True, comment="用户ID，未登录为NULL"
    )
    user_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="用户唯一标识（如设备ID、会话ID等）",
    )
    client_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="客户端类型：web、app、h5、wechat_miniprogram等",
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="操作类型：upload、download、delete、view等"
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="IP地址"
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="User-Agent信息"
    )
    file_size: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="操作的文件大小（字节）"
    )
    endpoint: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="访问的接口地址"
    )
    extra_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="额外数据（JSON格式）"
    )
