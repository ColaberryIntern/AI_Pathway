"""Quick acknowledgment of Luda's screenshot concern.

The URL-fix reply addressed her first follow-up but missed her second one
about screenshots not matching descriptions. This sends a brief follow-up
explaining which items lack a red highlight and how to assess them anyway,
so she can keep reviewing while we fix the highlighter for the next round.
"""

import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SECRETS_PATH = SCRIPT_DIR / ".secrets" / "gmail_app_password.txt"

FROM_EMAIL = "ali@colaberry.com"
FROM_NAME = "Ali Muwwakkil"
SUBJECT = "Re: AI Pathway - 17 changes ready for review + new feedback process"

TO = ["ludakopeikina@gmail.com"]
CC = ["ram@colaberry.com", "vivmuk@gmail.com"]
BCC = ["ali@colaberry.com"]

BODY_TEXT = """Hi Luda,

I missed your second email when I sent the URL fix. You are right that several screenshots do not have a red highlight box around the change.

7 of the 17 cards ended up with plain page screenshots because our highlight script could not find the specific element to draw a box around. The screenshots are of the correct page, but they do not visually call out what changed. The affected items are:

  03 (skills review merged), 04 (hover tooltip), 05 (targeted role label),
  06 (skill match messaging), 08 (journey roadmap removed),
  13 (example 2 A/B comparison), 17 (deterministic skill ordering)

For those 7 items in the current zip, please:

  1. Click the live URL on the card. The change is visible on the page when you land there.
  2. Use the "What was changed" description on the card as your guide.
  3. If the change is hard to find on the live page, mark the card as a Question and I will point you to it.

For the other 10 items (01, 02, 07, 09-12, 14-16), the red highlight is in the screenshot as expected.

I am fixing the highlighter so this will not repeat. You do not need to wait on that. Please keep working through the current zip.

Thanks,
Ali
"""


def main() -> int:
    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = ", ".join(TO)
    msg["Cc"] = ", ".join(CC)
    msg["Subject"] = SUBJECT
    msg.set_content(BODY_TEXT)

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

    print(f"Sent to: {all_recipients}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
