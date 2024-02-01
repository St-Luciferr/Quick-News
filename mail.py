#!/usr/bin/python

import csv
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import argparse
from scrape_gorkhapatra import scrape_gorkhapatra
import nepali_datetime
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder
from sqlalchemy.orm import declarative_base


# Read configuration from JSON file
with open('remote_db_config.json') as f:
    config = json.load(f)

# Access individual parameters
ssh_host = config['ssh']['host']
ssh_port = config['ssh']['port']
ssh_username = config['ssh']['username']
ssh_private_key = config['ssh']['private_key']

postgres_host = config['postgres']['host']
postgres_port = config['postgres']['port']
postgres_user = config['postgres']['user']
postgres_password = config['postgres']['password']
postgres_db = config['postgres']['database']

table_name='cg_news'
Base = declarative_base() 
# Define a model (example table "NewsBase")
class NewsBase(Base):
        __tablename__ = table_name

        id = Column(Integer, primary_key=True, autoincrement=True)

        title = Column(String(200))
        link = Column(String(200))
        newspaper=Column(String(200))
        keyword=Column(String(50))
        content=Column(String(500))
        date_ad = Column(String(15))
        date_bs = Column(String(15))

def fetch_news():
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_pkey=ssh_private_key,
        remote_bind_address=(postgres_host, postgres_port)
    ) as tunnel:
    
        try:
            engine = create_engine(
                f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{tunnel.local_bind_port}/{postgres_db}"
            )
            print("Engine Created.")

        # Perform your database operations here

        except Exception as e:
            print(f"Error: {e}")

        Base.metadata.create_all(engine)
        # Now you can use the 'engine' object to interact with the PostgreSQL database
        Session = sessionmaker(bind=engine)
        session = Session()
        results = session.query(NewsBase).all()
        session.close()
        return results
        

def send(credentials,receiver,results,csv_file):
    nepali_date = nepali_datetime.date.today().strftime('%Y-%m-%d')
    eng_date = datetime.now().strftime('%Y-%m-%d')
    receivers = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for item in reader:
            try:
                if(len(item['Emails'])==0):
                    continue
                receivers.append(item['Emails'])
            except:
                break

    print(receivers)    
    with open(credentials) as js:
        '''
        look at the credentials.json file for the sample of json file
        '''
        jsn = json.load(js)
        Email_address = jsn['Email_address']
        Email_password = jsn['Email_password']
        print(f"Email Address: {Email_address}")
        print(f"Email Password: {Email_password}")


    # Attach image as MIMEImage
    message = MIMEMultipart()
    #Change the subject to your choice if you wish
    message['Subject'] = "Adverse Reporting News Articles"
    message['From'] = Email_address
    message['To'] = receiver
    # message['BCC']= ", ".join(cc)
    all_receivers = [receiver] + receivers
   
   
    if(len(results)==0):
        print("No articles to send")
        email_body = "<h2>No Articles Today:</h2>"
        message.attach(MIMEText(email_body, "html"))
    else:
        # Create the email body using HTML format
        email_body = "<h2>Today's News:</h2>"

        # Append each article to the email body
        for result  in results:
            if(result.date_bs!=nepali_date) and (result.date_ad != eng_date):
                continue
            email_body += f"""
            <div style="background-color:#f5f0f0;margin:10px 0;border-width:1px;border-style:solid;border-color:#f5f0f0;display:flex">
                <div style="padding:0 2rem">
                                <h3>{result.newspaper}</h3> 
                                <h4>{result.keyword}</h4>
                                <h4>{result.date_ad}</h4>
                </div>
                <div style="padding-bottom:20px">                
                    <a style="text-decoration: none;" href='{result.link}'><h3 style="color:red">{result.title}</h3></a>
                    <div>
                        <p>{result.content}
                            <a style="text-decoration: none;" href='{result.link}'>Read More...</a>
                        </p>
                    </div>
                </div>

            </div>
            """

    html_content = f"""
                    <html>
                    <body>
                    <div style="display:block;text-align:center;width:100%">
                            <div style="width:100%;height:50%">
                                    <img src="cid:image_banner" height="auto" width="50%" style="object-fit:contain;height:auto"><div class="a6S" dir="ltr" style="opacity: 0.01; left: 500px; top: 270.5px;"><span data-is-tooltip-wrapper="true" class="a5q" jsaction="JIbuQc:.CLIENT"><button class="VYBDae-JX-I VYBDae-JX-I-ql-ay5-ays CgzRE" jscontroller="PIVayb" jsaction="click:h5M12e;clickmod:h5M12e; pointerdown:FEiYhc; pointerup:mF5Elf; pointerenter:EX0mI; pointerleave:vpvbp; pointercancel:xyn4sd; contextmenu:xexox;focus:h06R8; blur:zjh6rb;mlnRJb:fLiPzd;" data-idom-class="CgzRE" jsname="hRZeKc" aria-label="Download attachment " data-tooltip-enabled="true" data-tooltip-id="tt-c1" data-tooltip-classes="AZPksf" id="" jslog="91252; u014N:cOuCgd,Kr2w4b,xr6bB; 4:WyIjbXNnLWY6MTc4OTQyNzMxNDY4NjQ5NDA1MyJd; 43:WyJpbWFnZS9qcGVnIl0."><span class="OiePBf-zPjgPe VYBDae-JX-UHGRz"></span><span class="bHC-Q" data-unbounded="false" jscontroller="LBaJxb" jsname="m9ZlFb" soy-skip="" ssk="6:RWVI5c"></span><span class="VYBDae-JX-ank-Rtc0Jf" jsname="S5tZuc" aria-hidden="true"><span class="bzc-ank" aria-hidden="true"><svg height="20" viewBox="0 -960 960 960" width="20" focusable="false" class=" aoH"><path d="M480-336 288-528l51-51 105 105v-342h72v342l105-105 51 51-192 192ZM263.717-192Q234-192 213-213.15T192-264v-72h72v72h432v-72h72v72q0 29.7-21.162 50.85Q725.676-192 695.96-192H263.717Z"></path></svg></span></span><div class="VYBDae-JX-ano"></div></button><div class="ne2Ple-oshW8e-J9" id="tt-c1" role="tooltip" aria-hidden="true">Download</div></span></div>
                            </div>
                            <div style="border: 1px solid #000; padding: 10px;text-align:left;">
                                    {email_body}
                            </div>
                    </div>
                    </body>
                    </html>
                    """
    message.attach(MIMEText(html_content, 'html'))
    with open('banner.png', 'rb') as image_file:
        image_attachment = MIMEImage(image_file.read(), name='banner.png')
        image_attachment.add_header('Content-ID', '<image_banner>')
        message.attach(image_attachment)

    # with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
    with smtplib.SMTP('smtp.gmail.com',587) as smtp:
        smtp.starttls()
        try:
            smtp.login(Email_address, Email_password)
            print("Logged in to Email")
        except:
            print("Login Failed")

        print("Sending Email")
        try:
            # message = "From: %s\r\n" % Email_address + "To: %s\r\n" % reciever + "CC: %s\r\n" % ",".join(cc) + "Subject: %s\r\n" % message['Subject'] + "\r\n"  + "hello"
            # to = [reciever] + cc 
            
            smtp.sendmail(Email_address, all_receivers, message.as_string())
            print(f"Email Sent to {all_receivers}")
        except Exception as e:
            print("Failed to send Email")
            print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="scrapes keywords from news website")
    parser.add_argument("-f", "--filename", type=str,
                        help="Path to the csv file containing keywords")
    # parser.add_argument("-u", "--url", type=str, help="URL to scrape")
    parser.add_argument("-r", "--receiver", type=str, help="Email address of the receiver")
    parser.add_argument("-c", "--credentials", type=str, help="Path to the credentials json file")
    args = parser.parse_args()
    csv_file = args.filename
    # url = args.url
    credentials = args.credentials
    receiver = args.receiver

    results= fetch_news()

    send(credentials,receiver,results,csv_file)

    print("Mailing Complete")
