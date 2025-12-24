from typing import Any, Dict
from fastapi import FastAPI
from neoxin_core.module import init_common_models
from neoxin_core.plugin import Plugin
from neoxin_core.storage import StorageManager, get_storage_manager
from .models import Attachment, RoleAttachmentConfig, AttachmentAccessLog
from .instance import _instance
from .routers import router
from .config import MODULE_CONFIGS


def init_models(init_sql_files: List[str]):
    """
    用于初始化数据库表，初始化存储管理
    """
    _models = [
        Attachment,
        RoleAttachmentConfig,
        AttachmentAccessLog,
    ]
    # 初始化数据库表
    init_common_models(_models, init_sql_files)


def init_storage(config: Dict[str, Any]):
    """
    初始化存储管理，根据配置初始化存储管理器
    【从配置文件中读取，若配置文件不存在则读取默认配置，若配置发生改变数据库、配置文件同步更新】
    """
    storage_type = config.get("storage_type", "local")
    _config: Dict[str, Any] = {}

    if storage_type == "qiniu":
        _config = {
            "access_key": config.get("qiniu_access_key"),
            "secret_key": config.get("qiniu_secret_key"),
            "bucket_name": config.get("qiniu_bucket_name"),
            "domain": config.get("qiniu_domain"),
            "region": config.get("qiniu_region"),
        }
    elif storage_type == "aliyun":
        _config = {
            "access_key_id": config.get("aliyun_access_key_id"),
            "access_key_secret": config.get("aliyun_access_key_secret"),
            "bucket_name": config.get("aliyun_bucket_name"),
            "domain": config.get("aliyun_domain"),
            "region": config.get("aliyun_region"),
            "endpoint": config.get("aliyun_endpoint"),
        }
    elif storage_type == "tencent":
        _config = {
            "secret_id": config.get("tencent_secret_id"),
            "secret_key": config.get("tencent_secret_key"),
            "bucket_name": config.get("tencent_bucket_name"),
            "domain": config.get("tencent_domain"),
            "region": config.get("tencent_region"),
        }
    elif storage_type == "local":
        _config = {
            "base_url": config.get("base_url"),
            "base_dir": config.get("base_dir"),
        }
    storage_manager = StorageManager()
    storage_manager.add_backend(
        name=storage_type,
        storage_type=storage_type,
        config=config,
        set_default=True,
    )


def attach(app: FastAPI, config: Dict[str, Any]):
    """
    用于加载服务，包括路由管理服务、存储管理服务的启动【系统类型插件默认自动启动，自定义的需要手动启动】
    """
    # 初始化存储管理
    init_storage(config)

    # 路由服务启动
    if hasattr(config, "base_prefix"):
        app.include_router(router, prefix=config["base_prefix"])
    else:
        app.include_router(router)


def init(
    app: FastAPI,
    config: Dict[str, Any],
) -> Plugin:
    """
    用于初始化服务，数据库表的初始化和数据配置的初始化

    :param app: FastAPI应用实例
    :param config: 配置字典
    """

    # 初始化数据结构
    init_models(config.get("init_sql_files", []))

    _instance = Plugin(
        app=app,
        config=config,
        attach=attach,
        module_configs=MODULE_CONFIGS,
    )

    return _instance
