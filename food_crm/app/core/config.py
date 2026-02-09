from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://crm:crm@localhost:5432/crm"
    JWT_SECRET: str = "CHANGE_ME_SUPER_LONG"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 60 * 12

    # SMTP outbound
    SMTP_HOST: str = "smtp.yourhost.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "user@domain.com"
    SMTP_PASS: str = "pass"
    SMTP_FROM: str = "user@domain.com"

    # IMAP inbound
    IMAP_HOST: str = "imap.yourhost.com"
    IMAP_PORT: int = 993
    IMAP_USER: str = "user@domain.com"
    IMAP_PASS: str = "pass"
    IMAP_FOLDER: str = "INBOX"


settings = Settings()
