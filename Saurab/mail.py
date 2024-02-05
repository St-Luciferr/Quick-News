import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(destination_mail, body, today):
    sender_email = "saurab.tharu2@gmail.com"
    sender_password = "ldng eqgz vnci rulr"

    message = MIMEMultipart()
    message["From"] = "Saurab Tharu"
    message["To"] = destination_mail
    message["Subject"] = f"News from eKantipur : {today}"

    body = MIMEText(body, "plain", "utf-8")
    message.attach(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()

        server.login(sender_email, sender_password)

        server.sendmail(sender_email, destination_mail, message.as_string())

    print("Email sent successfully!")
