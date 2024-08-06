import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json, time

try:
    with open('env.json', 'r') as file:
            config = json.load(file)
            SMTP_SERVER = str(config['CONFIG_MAIL']['SMTP_SERVER'])
            SMTP_PORT = str(config['CONFIG_MAIL']['SMTP_PORT'])
            SMTP_USERNAME = str(config['CONFIG_MAIL']['SMTP_USERNAME'])
            SMTP_PASSWORD = str(config['CONFIG_MAIL']['SMTP_PASSWORD'])
            FROM_EMAIL = str(config['CONFIG_MAIL']['FROM_EMAIL'])
            TO_EMAIL = str(config['CONFIG_MAIL']['TO_EMAIL'])
            

    def send_email(subject, body):
        # Tạo đối tượng email
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Gửi email
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()  # Bảo mật kết nối
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error: {e}")

    # Ví dụ sử dụng
    # send_email(
    #     subject='Test Email',
    #     body='This is a test email.',
    # )
    

except Exception as e:
    print(repr(e))   