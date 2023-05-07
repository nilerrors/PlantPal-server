from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    authjwt_secret_key: str

    mail_username: str
    mail_password: str
    mail_from: EmailStr
    mail_port: int = 587
    mail_server: str = 'smtp.office365.com'
    mail_from_name: str = 'PlantPal'

    class Config:
        env_file = '.env'

