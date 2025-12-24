from typing import List
from neoxin_core.schemas import PluginConfigItem

# 附件模块配置项
"""
配置字段说明：
- default_storage_backend: 默认存储后端类型（local/s3/oss等）
- max_file_size_mb: 默认最大文件大小（MB）
- allowed_mime_types: 允许的MIME类型（逗号分隔，为空表示不限制）
- enable_access_log: 是否启用访问日志记录
- log_retention_days: 访问日志保留天数
- enable_permission_check: 是否启用权限检查

"""

MODULE_CONFIGS: List[PluginConfigItem] = [
    PluginConfigItem(
        key="default_storage_backend",
        default="local",
        description="默认存储后端类型（local/s3/oss等）",
        validation_rule={
            "type": "string",
            "enum": ["local", "s3", "oss", "cos"],
            "description": "存储后端类型",
        },
    ),
    PluginConfigItem(
        key="max_file_size_mb",
        default=100,
        description="默认最大文件大小（MB）",
        validation_rule={
            "type": "integer",
            "minimum": 1,
            "maximum": 1024,
            "default": 100,
        },
    ),
    PluginConfigItem(
        key="allowed_mime_types",
        default="",
        description="允许的MIME类型（逗号分隔，为空表示不限制）",
        validation_rule={
            "type": "string",
            "description": "MIME类型列表，如：image/jpeg,image/png,application/pdf",
        },
    ),
    PluginConfigItem(
        key="enable_access_log",
        default=True,
        description="是否启用访问日志记录",
        validation_rule={"type": "boolean"},
    ),
    PluginConfigItem(
        key="log_retention_days",
        default=90,
        description="访问日志保留天数",
        validation_rule={
            "type": "integer",
            "minimum": 1,
            "maximum": 365,
            "default": 90,
        },
    ),
    PluginConfigItem(
        key="enable_permission_check",
        default=True,
        description="是否启用权限检查",
        validation_rule={"type": "boolean"},
    ),
    PluginConfigItem(
        key="init_sql_files",
        default=[],
        description="初始化SQL文件列表",
        validation_rule={
            "type": "array",
            "description": "初始化SQL文件列表，用于初始化数据库表",
        },
    ),
    PluginConfigItem(
        key="storage_type",
        default="local",
        description="存储类型, local, qiniu, aliyun, tencent",
        validation_rule={
            "type": "string",
            "enum": ["local", "qiniu", "aliyun", "tencent"],
            "description": "存储类型",
        },
    ),
    PluginConfigItem(
        key="qiniu_access_key",
        default="",
        description="七牛云AccessKey",
        validation_rule={
            "type": "string",
            "description": "七牛云AccessKey",
        },
    ),
    PluginConfigItem(
        key="qiniu_secret_key",
        default="",
        description="七牛云SecretKey",
        validation_rule={
            "type": "string",
            "description": "七牛云SecretKey",
        },
    ),
    PluginConfigItem(
        key="qiniu_bucket_name",
        default="",
        description="七牛云Bucket名称",
        validation_rule={
            "type": "string",
            "description": "七牛云Bucket名称",
        },
    ),
    PluginConfigItem(
        key="qiniu_domain",
        default="",
        description="七牛云Domain",
        validation_rule={
            "type": "string",
            "description": "七牛云Domain",
        },
    ),
    PluginConfigItem(
        key="qiniu_region",
        default="",
        description="七牛云Region",
        validation_rule={
            "type": "string",
            "description": "七牛云Region",
        },
    ),
    PluginConfigItem(
        key="aliyun_access_key_id",
        default="",
        description="阿里云AccessKey ID",
        validation_rule={
            "type": "string",
            "description": "阿里云AccessKey ID",
        },
    ),
    PluginConfigItem(
        key="aliyun_access_key_secret",
        default="",
        description="阿里云AccessKey Secret",
        validation_rule={
            "type": "string",
            "description": "阿里云AccessKey Secret",
        },
    ),
    PluginConfigItem(
        key="aliyun_bucket_name",
        default="",
        description="阿里云Bucket名称",
        validation_rule={
            "type": "string",
            "description": "阿里云Bucket名称",
        },
    ),
    PluginConfigItem(
        key="aliyun_domain",
        default="",
        description="阿里云Domain",
        validation_rule={
            "type": "string",
            "description": "阿里云Domain",
        },
    ),
    PluginConfigItem(
        key="aliyun_region",
        default="",
        description="阿里云Region",
        validation_rule={
            "type": "string",
            "description": "阿里云Region",
        },
    ),
    PluginConfigItem(
        key="aliyun_endpoint",
        default="",
        description="阿里云Endpoint",
        validation_rule={
            "type": "string",
            "description": "阿里云Endpoint",
        },
    ),
    PluginConfigItem(
        key="tencent_secret_id",
        default="",
        description="腾讯云SecretID",
        validation_rule={
            "type": "string",
            "description": "腾讯云SecretID",
        },
    ),
    PluginConfigItem(
        key="tencent_secret_key",
        default="",
        description="腾讯云SecretKey",
        validation_rule={
            "type": "string",
            "description": "腾讯云SecretKey",
        },
    ),
    PluginConfigItem(
        key="tencent_bucket_name",
        default="",
        description="腾讯云Bucket名称",
        validation_rule={
            "type": "string",
            "description": "腾讯云Bucket名称",
        },
    ),
    PluginConfigItem(
        key="tencent_domain",
        default="",
        description="腾讯云Domain",
        validation_rule={
            "type": "string",
            "description": "腾讯云Domain",
        },
    ),
    PluginConfigItem(
        key="tencent_region",
        default="",
        description="腾讯云Region",
        validation_rule={
            "type": "string",
            "description": "腾讯云Region",
        },
    ),
    PluginConfigItem(
        key="base_dir",
        default="./data/attachments",
        description="本地存储路径",
        validation_rule={
            "type": "string",
            "description": "本地存储路径",
        },
    ),
    PluginConfigItem(
        key="base_url",
        default="/files",
        description="访问路径前缀",
        validation_rule={
            "type": "string",
            "description": "访问路径前缀",
        },
    ),
    PluginConfigItem(
        key="base_prefix",
        default="",
        description="路由服务访问路径前缀",
        validation_rule={
            "type": "string",
            "description": "路由服务访问路径前缀",
        },
    ),
]


def get_default_config():
    """获取默认配置"""
    return {config.key: config.default for config in MODULE_CONFIGS}
