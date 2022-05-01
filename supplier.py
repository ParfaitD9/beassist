import ssl
import os
import smtplib
from jinja2 import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import time

from mars import loadenv


class Supplier:
    def __init__(self, name, email, pays) -> None:
        self.name = name
        self.email = email
        self.pays = pays
    
    def __str__(self) -> str:
        return f"{self.name} : {self.email}"

    def send_mail(self):
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context= ctx) as s:
            #s.starttls()
            s.login(
                os.environ.get('EMAIL_USER'),
                os.environ.get('EMAIL_PASSWORD')
            )
            sender = os.environ.get('EMAIL_USER')
            receiver = self.email
            print(f"Successuly connected as {sender}")

            
            with open('./templates/email-en.html') if self.pays != 'France' else open('./templates/email.html') as f:
                tpl : Template = Template(f.read())
                body = tpl.render(supplier=self)

            
            
            message = MIMEMultipart()
            message['From'] = sender
            message['To'] = receiver
            message['Subject'] = 'Demande de renseignement' if self.pays == 'France' else 'Ask for information'
            
            message.attach(MIMEText(body, 'html'))

            try:
                s.sendmail(
                    from_addr= sender,
                    to_addrs=[self.email,],
                    msg= message.as_string()
                )
            except Exception as e:
                print(f"{e.__class__} : {e.args[0]} with {self.email}")
            else:
                print(f"Mail successfully sent to {self.email}")

if __name__ == '__main__':
    loadenv()
    with open('./docs/catalogue.csv') as f:
        reader = csv.reader(f, delimiter= ',', quotechar= '"')
        for row in list(reader)[1:-3]:
            name, _, email, pays, note = row
            sup = Supplier(name, email, pays)
            if sup.email != 'Pas trouvé':
                sup.send_mail()
                time.sleep(3)