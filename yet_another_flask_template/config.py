from dataclasses import dataclass

from sqlalchemy import URL

@dataclass
class Config:
    SECRET_KEY: str = "development"
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_NAME: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    
    def db_url(self, engine: str ="asyncpg") -> URL:
        return URL.create(
            f"postgresql+{engine}",
            username=self.DB_USER,
            password=self.DB_PASS,
            database=self.DB_NAME,
            host=self.DB_HOST,
            port=int(self.DB_PORT),
        )


def load_config() -> Config:
    return Config()

