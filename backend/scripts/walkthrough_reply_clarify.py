"""One-off reply to Luda's question about how to open the walkthrough.

Sends the new zip (with cleaner top-level structure) and explains how to use it.
"""

import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
SECRETS_PATH = SCRIPT_DIR / ".secrets" / "gmail_app_password.txt"
ATTACHMENT_PATH = PROJECT_ROOT / "docs" / "walkthrough_report.zip"

FROM_EMAIL = "ali@colaberry.com"
FROM_NAME = "Ali Muwwakkil"
SUBJECT = "Re: AI Pathway - 17 changes ready for review + new feedback process"

TO = ["ludakopeikina@gmail.com"]
CC = ["ram@colaberry.com", "vivmuk@gmail.com"]
BCC = ["ali@colaberry.com"]

BODY_TEXT = """Hi Luda,

You're right, the original layout wasn't clear. I had the HTML and all 17 screenshot files at the same level in the folder, so it wasn't obvious which one to open.

Attached is a new zip with a cleaner structure. When you unzip, you'll see:

  walkthrough_report/
    README.txt              (says the same thing as this email)
    WALKTHROUGH.html        (click this one)
    screenshots/            (ignore, HTML uses it automatically)
    WALKTHROUGH_REPORT.md   (alternate markdown format, also ignorable)

Just double-click WALKTHROUGH.html, or right-click and Open With Safari or Chrome. The browser opens one page with all 17 changes as scrollable cards. Each card has the screenshot, URL, description, and the Approved / Issue / Question feedback widget.

You can ignore the screenshots folder entirely. The HTML references it automatically.

Future rounds will use this cleaner structure.

Thanks,
Ali
"""


def main() -> int:
    if not ATTACHMENT_PATH.exists():
        sys.stderr.write(f"ERROR: attachment not found at {ATTACHMENT_PATH}\n")
        return 1

    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = ", ".join(TO)
    msg["Cc"] = ", ".join(CC)
    msg["Subject"] = SUBJECT
    msg.set_content(BODY_TEXT)

    with open(ATTACHMENT_PATH, "rb") as fp:
        msg.add_attachment(
            fp.read(),
            maintype="application",
            subtype="zip",
            filename="walkthrough_report.zip",
        )

    pw = SECRETS_PATH.read_text(encoding="utf-8").strip().replace(" ", "")
    all_recipients = TO + CC + BCC

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(FROM_EMAIL, pw)
            refused = smtp.send_message(
                msg, from_addr=FROM_EMAIL, to_addrs=all_recipients
            )
    except smtplib.SMTPException as exc:
        sys.stderr.write(f"SMTP error: {exc}\n")
        return 2

    if refused:
        sys.stderr.write(f"Refused by server: {refused}\n")
        return 3

    print(
        f"Sent.\n"
        f"  To:      {', '.join(TO)}\n"
        f"  CC:      {', '.join(CC)}\n"
        f"  BCC:     {', '.join(BCC)}\n"
        f"  Subject: {SUBJECT}\n"
        f"  Size:    {ATTACHMENT_PATH.stat().st_size:,} bytes attached"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
