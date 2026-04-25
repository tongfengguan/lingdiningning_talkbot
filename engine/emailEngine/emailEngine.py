import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
from loguru import logger
from config import config

def send_email_to_user(subject, content, to_email):
    if not config.SMTP_PASSWORD or not config.SMTP_USER: return False
    
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = formataddr((Header(config.BOT_NAME, 'utf-8').encode(), config.SMTP_USER))
    msg['To'] = formataddr((Header("看看", 'utf-8').encode(), to_email))
    msg['Subject'] = Header(subject, 'utf-8').encode()

    for port, use_ssl in [(465, True), (587, False)]:
        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(config.SMTP_HOST, port, timeout=10)
            else:
                server = smtplib.SMTP(config.SMTP_HOST, port, timeout=10)
                server.starttls()
            
            with server:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                server.sendmail(config.SMTP_USER, [to_email], msg.as_string())
            logger.info(f"Email sent via {port}")
            return True
        except Exception as e:
            logger.warning(f"Port {port} failed: {e}")
    return False
