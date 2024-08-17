import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from src.tools.loadconfig import load_config


# ===================== 邮件发送 ===================== #
def send_email_smtp(subject, body, recipient):
    config = load_config()["Mail"]
    sender_email = config["MAIL_USERNAME"]
    sender_password = config["MAIL_PASSWORD"]
    smtp_server = config["MAIL_SERVER"]
    smtp_port = config["MAIL_PORT"]
    sender_name = config["MAIL_DEFAULT_SENDER"]
    msg = MIMEMultipart()
    msg["From"] = formataddr((str(Header(sender_name, "utf-8")), sender_email))
    msg["To"] = formataddr((str(Header(recipient, "utf-8")), recipient))
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_bytes())  # 发送邮件时使用字节流
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
    return True
