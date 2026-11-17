#!/usr/bin/env python3
"""Send GitHub Actions report using repository SMTP secrets; never log credentials."""
import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

host = os.getenv("SMTP_HOST")
username = os.getenv("SMTP_USERNAME")
password = os.getenv("SMTP_PASSWORD")
port = int(os.getenv("SMTP_PORT") or "465")
if not all([host, username, password]):
    print("Email not sent: configure SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD as GitHub Actions secrets.")
    raise SystemExit(0)
report_path = Path("weekly-update.json")
report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
status = os.getenv("UPDATE_RESULT", "unknown")
changed = os.getenv("UPDATE_CHANGED", "unknown")
msg = EmailMessage()
msg["Subject"] = f"RRB Prep weekly questions: {status} ({report.get('week', 'unknown')})"
msg["From"] = username
msg["To"] = os.getenv("MAIL_TO", "ishtiharkhan@gmail.com")
msg.set_content(
    f"RRB Prep weekly update\nStatus: {status}\nCommitted changes: {changed}\n"
    f"Week: {report.get('week', 'unknown')}\nQuestions: {report.get('question_count', 'unknown')}\n"
    f"Topics: {report.get('topics', {})}\nRepository: {os.getenv('REPO_URL', '')}\n"
)
if port == 465:
    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=25) as smtp:
        smtp.login(username, password)
        smtp.send_message(msg)
else:
    with smtplib.SMTP(host, port, timeout=25) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(username, password)
        smtp.send_message(msg)
print("Update email sent.")
