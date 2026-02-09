import email
import imaplib
from email.header import decode_header

from app.core.config import settings


def _decode(s):
    if not s:
        return None
    parts = decode_header(s)
    out = ""
    for p, enc in parts:
        if isinstance(p, bytes):
            out += p.decode(enc or "utf-8", errors="ignore")
        else:
            out += p
    return out


def fetch_latest_emails(limit: int = 50) -> list[dict]:
    """Fetch the latest *limit* emails from the configured IMAP account."""
    M = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
    M.login(settings.IMAP_USER, settings.IMAP_PASS)
    M.select(settings.IMAP_FOLDER)
    typ, data = M.search(None, "ALL")
    ids = data[0].split()[-limit:]
    emails_out: list[dict] = []
    for eid in ids:
        typ, msgdata = M.fetch(eid, "(RFC822)")
        raw = msgdata[0][1]  # type: ignore[index]
        msg = email.message_from_bytes(raw)

        subject = _decode(msg.get("Subject"))
        frm = _decode(msg.get("From"))
        to = _decode(msg.get("To"))
        cc = _decode(msg.get("Cc"))
        msg_id = msg.get("Message-ID")
        in_reply_to = msg.get("In-Reply-To")

        body_text = None
        body_html = None
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition") or "")
                if "attachment" in disp:
                    continue
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                charset = part.get_content_charset() or "utf-8"
                if ctype == "text/plain" and body_text is None:
                    body_text = payload.decode(charset, errors="ignore")
                if ctype == "text/html" and body_html is None:
                    body_html = payload.decode(charset, errors="ignore")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                body_text = payload.decode(charset, errors="ignore")

        emails_out.append(
            {
                "subject": subject,
                "from": frm,
                "to": to,
                "cc": cc,
                "provider_msg_id": msg_id,
                "thread_id": in_reply_to,
                "body_text": body_text,
                "body_html": body_html,
            }
        )

    M.logout()
    return emails_out
