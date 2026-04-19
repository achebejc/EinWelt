import smtplib
from email.mime.text import MIMEText

from app.core.config import settings


def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Send a plain-text email.

    When SMTP credentials are not configured the function logs the message to
    stdout so that development environments still surface the content (e.g.
    password-reset links) without requiring a real mail server.
    """
    if not settings.smtp_host or not settings.smtp_username:
        # Development stub — print instead of sending
        print(
            f"[email stub] To: {to_email} | Subject: {subject}\n{body}"
        )
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    if settings.smtp_use_tls:
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        server.starttls()
    else:
        server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port)

    server.login(settings.smtp_username, settings.smtp_password or "")
    server.sendmail(settings.smtp_from, [to_email], msg.as_string())
    server.quit()
