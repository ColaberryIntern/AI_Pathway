"""Send the walkthrough email with zip attachment via Gmail SMTP.

Reads app password from backend/scripts/.secrets/gmail_app_password.txt
(gitignored) or the GMAIL_APP_PASSWORD environment variable.

Generate an app password at https://myaccount.google.com/apppasswords (2FA required).
"""

import os
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
SUBJECT = "AI Pathway - 17 changes ready for review + new feedback process"

TO = ["ludakopeikina@gmail.com", "ram@colaberry.com"]
CC = ["vivmuk@gmail.com"]
BCC = ["ali@colaberry.com"]

BODY_TEXT = """Hi Luda, Ram (cc Vivek),

Quick update. We've shipped 17 visual and UX changes covering Luda's Apr 15 and Apr 28 feedback, Vivek's Apr 29 chapter depth and Try-in-LLM requests, and the new Implementation Task as the 6th chapter section.

Rather than going back and forth on individual items, I'd like to walk you through a new review process we've built. It should make this round (and every future round) significantly faster.

How to use it:

1. Unzip the attachment and open WALKTHROUGH.html in any browser. No install needed.
2. You'll see 17 cards, one per change, each with a screenshot of the affected screen, the live URL, and a quick description of what changed and why.
3. For each card, mark it Approved, Issue, or Question. Add a note for Issues and Questions.
4. Your notes auto-save in the browser, so you can stop and come back. Refreshing won't lose your work.
5. When you're done, click "Generate Feedback Email" at the bottom right. It compiles everything into a structured email, pre-fills it back to me, and you just hit send.

Why this matters:

When your reply comes back, our system reads the structured format and routes each requested fix directly to the right files. No interpretation, no clarifying questions, no "what did you mean exactly?" Each item is independently tracked. Approved items don't get re-tested. Only the issues and questions need attention next round.

Going forward:

Every batch of visual changes will come to you in this format. The expected loop is: ship change, you review the HTML, you click send, fixes go in, next HTML comes back. Should noticeably tighten the cycle for both of us.

If anything in the file doesn't render or the format is unclear, just reply and let me know.

Thanks,
Ali
"""


def load_app_password() -> str:
    pw = os.environ.get("GMAIL_APP_PASSWORD")
    if not pw and SECRETS_PATH.exists():
        pw = SECRETS_PATH.read_text(encoding="utf-8").strip()
    if not pw:
        sys.stderr.write(
            f"ERROR: GMAIL_APP_PASSWORD not set and {SECRETS_PATH} missing.\n"
        )
        sys.exit(1)
    return pw.replace(" ", "")


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

    app_password = load_app_password()
    all_recipients = TO + CC + BCC

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(FROM_EMAIL, app_password)
            refused = smtp.send_message(
                msg, from_addr=FROM_EMAIL, to_addrs=all_recipients
            )
    except smtplib.SMTPAuthenticationError as exc:
        sys.stderr.write(f"SMTP auth failed: {exc}\n")
        return 2
    except smtplib.SMTPException as exc:
        sys.stderr.write(f"SMTP error: {exc}\n")
        return 3

    if refused:
        sys.stderr.write(f"Refused by server: {refused}\n")
        return 4

    print(
        f"Sent.\n"
        f"  From:    {FROM_EMAIL}\n"
        f"  To:      {', '.join(TO)}\n"
        f"  CC:      {', '.join(CC)}\n"
        f"  BCC:     {', '.join(BCC)}\n"
        f"  Subject: {SUBJECT}\n"
        f"  Size:    {ATTACHMENT_PATH.stat().st_size:,} bytes attached"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
