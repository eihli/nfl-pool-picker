import os
import smtplib

RECV_EMAIL = os.environ.get('RECV_EMAIL')
EMAIL = os.environ.get('ALERT_EMAIL')
EMAIL_PASS = os.environ.get('ALERT_EMAIL_PASS')


def alert(module_name, msg):
    with smtplib.SMTP('smtp.gmail.com', 587) as s:
        s.starttls()
        s.login(EMAIL, EMAIL_PASS)
        subject = f"Error in module: {module_name}"
        msg = f"Subject: {subject}\n\n{msg}"
        s.sendmail(EMAIL, RECV_EMAIL, msg)


alert('temp', 'msg')
