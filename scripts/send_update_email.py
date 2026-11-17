#!/usr/bin/env python3
"""Send a styled question-update email after a successful GitHub Actions commit."""
import html
import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

host = os.getenv("SMTP_HOST")
username = os.getenv("SMTP_USERNAME")
password = os.getenv("SMTP_PASSWORD")
if not all([host, username, password]):
    raise SystemExit("SMTP credentials not configured; email not sent. Set SMTP_HOST, SMTP_USERNAME and SMTP_PASSWORD in GitHub Actions secrets.")
port = int(os.getenv("SMTP_PORT") or "465")
report_path = Path("weekly-update.json")
if not report_path.exists():
    raise SystemExit("Missing update report; email not sent.")
report = json.loads(report_path.read_text(encoding="utf-8"))
count = int(report.get("question_count", 0))
if count != 100:
    raise SystemExit("Expected exactly 100 questions; email not sent.")
url = "https://ishtihar.github.io/ibps-rrb-clerk-mock-test/"
recipient = "tamanathakur1999@gmail.com"
topics = report.get("topics", {})
rows = "".join(
    f'<tr><td style="padding:7px 0;border-bottom:1px solid #e3eaf5">{html.escape(str(topic))}</td><td style="padding:7px 0;text-align:right;border-bottom:1px solid #e3eaf5">{int(n)} Questions</td></tr>'
    for topic, n in topics.items()
)
body = f"""<!doctype html><html><body style="margin:0;padding:28px 12px;background:#f2f5fa;font-family:Arial,Helvetica,sans-serif;color:#18304e"><table role="presentation" style="max-width:580px;width:100%;margin:auto;background:#fff;border-radius:14px;border-collapse:separate;border-spacing:0;overflow:hidden"><tr><td style="background:#102d55;padding:28px;color:white"><div style="font-size:13px;letter-spacing:2px;color:#b5d4ff;font-weight:bold">RRB PREP</div><h1 style="font-size:25px;margin:12px 0 0;color:white">100 New Practice Questions Added!</h1></td></tr><tr><td style="padding:28px"><p><strong>Dear Student,</strong></p><p style="line-height:1.8">Great news! We have added <strong>100 fresh practice questions</strong> across Quantitative Aptitude and Reasoning to help you prepare for the IBPS RRB Clerk examination.</p><p style="line-height:1.8">Challenge yourself with the latest set and improve your speed, accuracy and confidence.</p><div style="background:#f1f6ff;border-radius:10px;padding:16px 20px;margin:20px 0"><strong>What's New?</strong><table style="width:100%;font-size:13px;margin-top:10px;border-collapse:collapse">{rows}</table><p style="margin:12px 0 0;font-weight:bold">Total: 100 New Questions</p></div><table role="presentation" style="margin:25px auto"><tr><td bgcolor="#1767d2" style="border-radius:9px"><a href="{url}" style="display:inline-block;padding:16px 32px;text-decoration:none;color:white;font-weight:bold;font-size:16px">Start Mock Test</a></td></tr></table><p style="text-align:center;color:#52667e;font-size:14px">Practice regularly. Every question brings you one step closer to your goal.</p><div style="background:#fff3cd;border:1px solid #e7c66a;border-radius:10px;padding:20px;margin-top:24px;color:#654600;line-height:1.8"><strong style="color:#795200">विद्यार्थियों के लिए विशेष संदेश</strong><p>प्रिय विद्यार्थी,</p><p>मॉक टेस्ट पूरा करने के बाद कृपया इसी ईमेल का जवाब देकर <strong>“DONE”</strong> लिखकर भेजें।</p><p>साथ ही बताइए कि <strong>आप एक दिन में कितने मॉक टेस्ट देना चाहते हैं — 1, 2, 3 या उससे अधिक?</strong></p><p>हम आपकी तैयारी के लिए आगे भी नए प्रश्न जोड़ते रहेंगे।</p><p><strong>आपका कोई सुझाव, शिकायत या फीडबैक हो तो इसी ईमेल का Reply करके हमें जरूर बताएँ।</strong></p><p style="text-align:center;font-weight:bold">आपकी तैयारी, आपकी राय और आपकी सफलता — यही हमारी प्राथमिकता है!</p></div><p style="margin-top:24px">Best wishes,<br><strong>Team RRB Prep</strong></p></td></tr><tr><td style="background:#f8fafd;text-align:center;padding:16px;font-size:12px;color:#718198">RRB Prep | IBPS RRB Clerk Mock Test</td></tr></table></body></html>"""
msg = EmailMessage()
msg["From"] = username
msg["To"] = recipient
msg["Subject"] = "RRB Prep | 100 New Questions Added — Start Your Mock Test!"
msg.set_content("Dear Student,\n\n100 new RRB Prep questions are ready. Start Mock Test: " + url + "\n\nमॉक टेस्ट पूरा करने के बाद DONE लिखकर Reply करें। रोज कितने टेस्ट चाहते हैं और कोई फीडबैक हो तो बताएं।\n\nTeam RRB Prep")
msg.add_alternative(body, subtype="html")
if port == 465:
    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=25) as smtp:
        smtp.login(username, password)
        smtp.send_message(msg)
else:
    with smtplib.SMTP(host, port, timeout=25) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(username, password)
        smtp.send_message(msg)
print("Update email sent to " + recipient)
