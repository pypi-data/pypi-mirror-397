from __future__ import annotations

import inspect
from pathlib import Path
from typing import Optional
from omegaconf import OmegaConf

class SftConfig:
    CONFIG_ROOT = Path.home() / ".sft"
    
    # Configuration descriptions mapping
    CONFIG_DESCRIPTIONS = {
        "sft_file_root": "SFT file storage root directory",
        "service_center_address": "Service center address",
        "k8s_namespace": "Kubernetes namespace",
        "registry_address": "Registry address",
        "inject_http_port": "HTTP port for services",
        "inject_kafka_host": "Kafka host for services",
        "inject_kafka_port": "Kafka port for services",
        "inject_postgres_host": "Postgres host for services",
        "inject_postgres_port": "Postgres port for services",
        "inject_postgres_user": "Postgres user for services",
        "inject_postgres_password": "Postgres password for services",
        "deepseek_api_key": "DeepSeek API key",
        "deepseek_base_url": "DeepSeek base URL",
    }

    def __init__(
        self,
        sft_file_root: str = "/tmp/sft",
        service_center_address: str = "http://vps.shiweinan.com:37919/service_center",
        k8s_namespace: str = "secondbrain",
        registry_address: str = "crpi-cev6qq28wwgwwj0y.cn-beijing.personal.cr.aliyuncs.com/nexthci",

        inject_http_port: int = 8000,

        inject_kafka_host: str = "localhost",
        inject_kafka_port: int = 9092,

        inject_postgres_host: str = "second-brain-postgres-postgresql",
        inject_postgres_port: int = 5432,
        inject_postgres_user: str = "postgres",
        inject_postgres_password: str = "gnBGWg7aL4",

        inject_mongo_host: str = "mongo-mongodb",
        inject_mongo_port: int = 27017,
        inject_mongo_user: str = "secondbrain",
        inject_mongo_password: str = "secondbrain",
        inject_mongo_db: str = "secondbrain",

        inject_redis_host: str = "redis-master",
        inject_redis_port: int = 6379,
        inject_redis_password: str = "rDdM2Y2gX9",

        deepseek_api_key: str = "82c9df22-f6ed-411e-90d7-c5255376b7ca",
        deepseek_base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
    ):
        self.sft_file_root = sft_file_root
        self.service_center_address = service_center_address
        self.k8s_namespace = k8s_namespace
        self.registry_address = registry_address

        self.inject_http_port = inject_http_port

        self.inject_kafka_host = inject_kafka_host
        self.inject_kafka_port = inject_kafka_port

        self.inject_postgres_host = inject_postgres_host
        self.inject_postgres_port = inject_postgres_port
        self.inject_postgres_user = inject_postgres_user
        self.inject_postgres_password = inject_postgres_password

        self.inject_mongo_host = inject_mongo_host
        self.inject_mongo_port = inject_mongo_port
        self.inject_mongo_user = inject_mongo_user
        self.inject_mongo_password = inject_mongo_password
        self.inject_mongo_db = inject_mongo_db

        self.inject_redis_host = inject_redis_host
        self.inject_redis_port = inject_redis_port
        self.inject_redis_password = inject_redis_password

        self.deepseek_api_key = deepseek_api_key
        self.deepseek_base_url = deepseek_base_url

    @property
    def server_url(self) -> str:
        return self.service_center_address

    @property
    def upload_timeout(self) -> int:
        return 300  # 5 minutes default timeout

    @classmethod
    def get_config_keys(cls) -> list[str]:
        sig = inspect.signature(cls.__init__)
        return [param for param in sig.parameters.keys() if param != 'self']
    
    @property
    def config_file_path(self) -> Path:
        return self.CONFIG_ROOT / "config.yaml"
    
    def ensure_config_dir(self) -> None:
        self.CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> dict:
        config_keys = self.get_config_keys()
        return {key: getattr(self, key) for key in config_keys}
    
    def from_dict(self, data: dict) -> None:
        config_keys = self.get_config_keys()
        for key in config_keys:
            if key in data:
                setattr(self, key, data[key])
    
    def save(self) -> None:
        self.ensure_config_dir()
        config_dict = self.to_dict()
        OmegaConf.save(config_dict, self.config_file_path)
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return getattr(self, key, default)
    
    def set(self, key: str, value: str) -> None:
        if key in ["config_root"]:
            raise ValueError(f"{key} is read-only")
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise ValueError(f"Unknown config key: {key}")
    
    def update(self, updates: dict) -> None:
        for key, value in updates.items():
            self.set(key, value)


def load_config() -> SftConfig:
    # config = SftConfig()
    config = SftConfig()
    config_file = config.config_file_path
    
    if config_file.exists():
        try:
            data = OmegaConf.load(config_file)
            config = SftConfig(**OmegaConf.to_container(data, resolve=True))
        except Exception as e:
            ...

    config.save()
    
    return config

sft_config = load_config()