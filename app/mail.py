from threading import Thread
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib



def send_async_email(msg):    
    smtp = smtplib.SMTP('localhost', 25)
    #smtp.connect("localhost")
    #smtp.login(login, password)
    smtp.sendmail(msg['From'], msg['To'], msg.as_string())
    smtp.quit()

def send_email(subject, from_address, to_address, text):    
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    text = text    
    
    part1 = MIMEText(text, 'html')
    msg.attach(part1)
    thr = Thread(target=send_async_email, args=[msg])
    thr.start()
