"""Reply to Luda with the URL-fix zip.

Explains that her two flagged issues were a tooling bug (broken URL substitution),
not application bugs, and ships an updated zip with working live URLs.
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

Thanks for sending the structured feedback. Quick read on what you flagged:

The two issues you marked (items 03 skill review merge and 04 hover tooltip) were not application bugs. They were a bug in the walkthrough HTML itself. The live URL was rendering as /analysis/** because of a parsing error in our report generator, plus the temp profile we use for screenshots was getting deleted right after the run, so even a correctly-rendered URL would have led nowhere. The actual changes for items 03 and 04 are working correctly in the deployed product. The screenshots showed them; you just couldn't click through to verify.

I've fixed both bugs in the walkthrough tool:

1. URL substitution now works (no more /analysis/**)
2. The demo profile stays alive so every URL in the report is clickable
3. The reviewer name field is now required (your previous submission came through with the placeholder text)

Attached is an updated zip with the working URLs. Same structure as before:

  walkthrough_report/
    README.txt              (instructions)
    WALKTHROUGH.html        (click this one)
    screenshots/            (ignore)
    WALKTHROUGH_REPORT.md   (alternate format)

A couple of things to know:

- Your in-progress notes from the previous zip will not carry over to this one (browser local storage is keyed to the file). You will need to re-mark the 4 items you already reviewed.
- The 2 items you marked as Issues should now resolve. Click the URL on each card and you will land on the correct analysis page; the merged skill review and hover tooltip should both be visible.
- Pick up from item 05 once you re-do 01 through 04.

Sorry for the rework. The fix is in place so this will not happen again on future rounds.

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
