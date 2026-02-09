import smtplib
from email.message import EmailMessage as PyEmail

from app.core.config import settings


def send_smtp(
    subject: str,
    body: str,
    to: list[str],
    cc: list[str] | None = None,
    attachments: list[tuple[str, bytes, str]] | None = None,
):
    """Send an email via SMTP with optional attachments.

    Args:
        subject: Email subject.
        body: Plain text body.
        to: List of recipient addresses.
        cc: Optional list of CC addresses.
        attachments: List of (filename, data_bytes, mime_type) tuples.
    """
    msg = PyEmail()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg.set_content(body)

    if attachments:
        for filename, data, mime in attachments:
            maintype, subtype = mime.split("/", 1)
            msg.add_attachment(
                data, maintype=maintype, subtype=subtype, filename=filename
            )

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
        s.starttls()
        s.login(settings.SMTP_USER, settings.SMTP_PASS)
        s.send_message(msg)
