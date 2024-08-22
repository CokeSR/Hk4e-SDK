import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from src.tools.loadconfig import load_config


# ===================== 邮件发送 ===================== #
def send_email_smtp(verification_code, recipient):
    config = load_config()["Mail"]
    sender_email = config["MAIL_USERNAME"]
    sender_password = config["MAIL_PASSWORD"]
    smtp_server = config["MAIL_SERVER"]
    smtp_port = config["MAIL_PORT"]
    sender_name = config["MAIL_DEFAULT_SENDER"]
    # 构建HTML邮件内容
    subject = "SDK 邮箱验证"
    body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
            .container {{ width: 80%; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; }}
            h1 {{ color: #0056b3; }}
            .footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #ddd; text-align: center; font-size: 12px; color: #888; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SDKServer 邮箱验证</h1>
            <hr>
            <p>尊敬的 {recipient}:</p>
            <p>您的邮箱验证码为：<strong style="color:red">{verification_code}</strong>，安全有效期 5 分钟。</p>
            <p>管理员不会向您索要验证码，请妥善保管。</p>
            <p>如果您还有其他问题，请联系系统管理员：<a href="mailto:{sender_email}">{sender_email}</p>
            <div class="footer">
                <p>&copy; 2024 cokeserver@qq.com. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    msg = MIMEMultipart()
    msg["From"] = formataddr((str(Header(sender_name, "utf-8")), sender_email))
    msg["To"] = formataddr((str(Header(recipient, "utf-8")), recipient))
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(body, "html", "utf-8"))
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
