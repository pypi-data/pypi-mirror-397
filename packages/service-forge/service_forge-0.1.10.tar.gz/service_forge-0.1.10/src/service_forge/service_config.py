from __future__ import annotations

class ServiceDatabaseConfig:
    def __init__(
        self,
        name: str,

        postgres_user: str,
        postgres_password: str,
        postgres_host: str,
        postgres_port: int,
        postgres_db: str,

        mongo_host: str,
        mongo_port: int,
        mongo_user: str,
        mongo_password: str,
        mongo_db: str,

        redis_host: str,
        redis_port: int,
        redis_password: str,
    ) -> None:
        self.name = name

        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port
        self.postgres_db = postgres_db

        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_user = mongo_user
        self.mongo_password = mongo_password
        self.mongo_db = mongo_db

        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
    
    @staticmethod
    def from_dict(config: dict) -> ServiceDatabaseConfig:
        return ServiceDatabaseConfig(
            name=config['name'],
            postgres_user=config.get('postgres_user', None),
            postgres_password=config.get('postgres_password', None),
            postgres_host=config.get('postgres_host', None),
            postgres_port=config.get('postgres_port', None),
            postgres_db=config.get('postgres_db', None),

            mongo_host=config.get('mongo_host', None),
            mongo_port=config.get('mongo_port', None),
            mongo_user=config.get('mongo_user', None),
            mongo_password=config.get('mongo_password', None),
            mongo_db=config.get('mongo_db', None),

            redis_host=config.get('redis_host', None),
            redis_port=config.get('redis_port', None),
            redis_password=config.get('redis_password', None),
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,

            'postgres_user': self.postgres_user,
            'postgres_password': self.postgres_password,
            'postgres_host': self.postgres_host,
            'postgres_port': self.postgres_port,
            'postgres_db': self.postgres_db,

            'mongo_host': self.mongo_host,
            'mongo_port': self.mongo_port,
            'mongo_user': self.mongo_user,
            'mongo_password': self.mongo_password,
            'mongo_db': self.mongo_db,

            'redis_host': self.redis_host,
            'redis_port': self.redis_port,
            'redis_password': self.redis_password,
        }

class ServiceConfig:
    def __init__(
        self,
        name: str,
        workflows: list[str],
        enable_http: bool,
        http_host: str,
        http_port: int,
        enable_kafka: bool,
        kafka_host: str,
        kafka_port: int,
        databases: list[ServiceDatabaseConfig],
    ) -> None:
        self.name = name
        self.workflows = workflows
        self.enable_http = enable_http
        self.http_host = http_host
        self.http_port = http_port
        self.enable_kafka = enable_kafka
        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.databases = databases

    @staticmethod
    def from_dict(config: dict) -> ServiceConfig:
        return ServiceConfig(
            name=config['name'],
            workflows=config['workflows'],
            enable_http=config['enable_http'],
            http_host=config['http_host'],
            http_port=config['http_port'],
            enable_kafka=config['enable_kafka'],
            kafka_host=config['kafka_host'],
            kafka_port=config['kafka_port'],
            databases=[ServiceDatabaseConfig.from_dict(database) for database in config['databases']],
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'workflows': self.workflows,
            'enable_http': self.enable_http,
            'http_host': self.http_host,
            'http_port': self.http_port,
            'enable_kafka': self.enable_kafka,
            'kafka_host': self.kafka_host,
            'kafka_port': self.kafka_port,
            'databases': [database.to_dict() for database in self.databases],
        }

# name: tag_service
# workflows:
#   # - ./workflow/kafka_workflow.yaml
#   - ./workflow/query_tags_workflow.yaml
#   - ./workflow/create_tag_workflow.yaml
#   - ./workflow/update_tag_workflow.yaml
#   - ./workflow/delete_tag_workflow.yaml
#   - ./workflow/get_tags_from_record.yaml

# enable_http: true
# enable_kafka: false

# # Following configs will be auto-injected by sft.
# http_host: 0.0.0.0
# http_port: 37200
# kafka_host: localhost
# kafka_port: 9092

# databases:
#   - name: tag
#     postgres_user: postgres
#     postgres_password: "gnBGWg7aL4"
#     postgres_host: second-brain-postgres-postgresql
#     postgres_port: 5432
#     postgres_db: tag-service-tag
