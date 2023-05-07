from pydantic import DirectoryPath, EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import app.config as config


settings = config.Settings()

conf = ConnectionConfig(
	MAIL_USERNAME=settings.mail_username,
	MAIL_PASSWORD=settings.mail_password,
	MAIL_FROM=settings.mail_from,
	MAIL_PORT=settings.mail_port,
	MAIL_SERVER=settings.mail_server,
	MAIL_FROM_NAME=settings.mail_from_name,
	MAIL_STARTTLS=True,
	MAIL_SSL_TLS=False,
	USE_CREDENTIALS=True,
	TEMPLATE_FOLDER='./app/templates/email'
)


async def send_email_async(subject: str, email_to: EmailStr, body: dict, template_name: str = 'email.html'):
	message = MessageSchema(
		subject=subject,
		recipients=[email_to],
		template_body=body,
		subtype=MessageType.html,
	)

	fm = FastMail(conf)
	await fm.send_message(message, template_name=template_name)
