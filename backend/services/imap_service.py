import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
from backend.database import SessionLocal
from backend import models
from backend.services.parser import parse_status_from_text

load_dotenv()
IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_PORT = int(os.getenv('IMAP_PORT', 993))
IMAP_USER = os.getenv('IMAP_USER')
IMAP_PASS = os.getenv('IMAP_PASS')


def _decode_header_part(h):
    parts = decode_header(h)
    out = []
    for val, enc in parts:
        if isinstance(val, bytes):
            out.append(val.decode(enc or 'utf-8', errors='ignore'))
        else:
            out.append(val)
    return ''.join(out)


def poll_inbound_and_process(limit=10):
    """Simple IMAP poller that looks for UNSEEN messages and tries to parse them.
    This is a minimal implementation; for production use webhooks or robust mail parsing.
    """
    if not IMAP_HOST or not IMAP_USER:
        print("IMAP not configured; skipping poll")
        return 0

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select('inbox')
        status, data = mail.search(None, '(UNSEEN)')
        mail_ids = data[0].split()[:limit]
        session = SessionLocal()
        processed = 0
        for mid in mail_ids:
            status, msg_data = mail.fetch(mid, '(RFC822)')
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            message_id = msg.get('Message-ID')
            subject = _decode_header_part(msg.get('Subject') or '')
            from_ = _decode_header_part(msg.get('From') or '')
            to = _decode_header_part(msg.get('To') or '')
            # Get body
            body = None
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    disp = str(part.get('Content-Disposition'))
                    if ctype == 'text/plain' and 'attachment' not in disp:
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            # Deduplicate
            existing = session.query(models.EmailMessage).filter_by(external_message_id=message_id).first()
            if existing:
                continue

            # Save raw email
            email_record = models.EmailMessage(
                external_message_id=message_id,
                direction='inbound',
                subject=subject,
                body_text=body,
                sender=from_,
                recipients=to
            )
            session.add(email_record)
            session.commit()

            
            import re
            m = re.search(r"<([^>]+)>", from_)
            sender_email = m.group(1) if m else from_
            consultant = session.query(models.Consultant).filter(models.Consultant.email == sender_email).first()

            parsed = parse_status_from_text(body or '')

            # Create StatusUpdate only if we detect useful info
            if parsed.get('status_label') or parsed.get('status_pct'):
                su = models.StatusUpdate(
                    task_id=None,
                    consultant_id=consultant.id if consultant else None,
                    status_pct=parsed.get('status_pct'),
                    status_label=parsed.get('status_label'),
                    summary=parsed.get('summary'),
                    blockers=parsed.get('blockers'),
                    eta_date=parsed.get('eta_date'),
                    source_email_id=email_record.id
                )
                session.add(su)
                session.commit()

            processed += 1
        session.close()
        mail.logout()
        print(f"IMAP poll processed {processed} messages")
        return processed
    except Exception as e:
        print("IMAP poll error:", e)
        return 0
