from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class AttachmentRead(BaseModel):
    """附件响应模型"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    filename: str
    content_type: str
    size: int
    path: str
    description: Optional[str] = None
    uploader_id: Optional[int] = None
    storage: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==================== 角色附件配置相关 Schema ====================


class RoleAttachmentConfigBase(BaseModel):
    """角色附件配置基础模型"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    role_id: int = Field(..., description="角色ID")
    max_file_size: int = Field(104857600, description="最大文件大小（字节），默认100MB")
    allowed_mime_types: Optional[str] = Field(
        None, description="允许的MIME类型，逗号分隔"
    )
    max_daily_uploads: Optional[int] = Field(None, description="每日最大上传次数")
    max_daily_size: Optional[int] = Field(
        None, description="每日最大上传总大小（字节）"
    )
    is_active: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="配置描述")


class RoleAttachmentConfigCreate(RoleAttachmentConfigBase):
    """角色附件配置创建模型"""

    pass


class RoleAttachmentConfigUpdate(BaseModel):
    """角色附件配置更新模型"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    max_file_size: Optional[int] = Field(None, description="最大文件大小（字节）")
    allowed_mime_types: Optional[str] = Field(
        None, description="允许的MIME类型，逗号分隔"
    )
    max_daily_uploads: Optional[int] = Field(None, description="每日最大上传次数")
    max_daily_size: Optional[int] = Field(
        None, description="每日最大上传总大小（字节）"
    )
    is_active: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="配置描述")


class RoleAttachmentConfigRead(RoleAttachmentConfigBase):
    """角色附件配置读取模型"""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==================== 附件访问日志相关 Schema ====================


class AttachmentAccessLogBase(BaseModel):
    """附件访问日志基础模型"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    attachment_id: int = Field(..., description="附件ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    user_identifier: Optional[str] = Field(None, description="用户唯一标识")
    client_type: str = Field(
        ..., description="客户端类型：web、app、h5、wechat_miniprogram等"
    )
    action: str = Field(..., description="操作类型：upload、download、delete、view等")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="User-Agent信息")
    file_size: Optional[int] = Field(None, description="操作的文件大小（字节）")
    endpoint: Optional[str] = Field(None, description="访问的接口地址")
    extra_data: Optional[dict[str, Any]] = Field(None, description="额外数据")


class AttachmentAccessLogCreate(AttachmentAccessLogBase):
    """附件访问日志创建模型"""

    pass


class AttachmentAccessLogRead(AttachmentAccessLogBase):
    """附件访问日志读取模型"""

    id: int
    created_at: Optional[datetime] = None


class AttachmentAccessLogQuery(BaseModel):
    """附件访问日志查询模型"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    attachment_id: Optional[int] = Field(None, description="附件ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    client_type: Optional[str] = Field(None, description="客户端类型")
    action: Optional[str] = Field(None, description="操作类型")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
