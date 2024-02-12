#!/usr/bin/python

import csv
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import argparse
import nepali_datetime
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder
from sqlalchemy.orm import declarative_base


# Read configuration from JSON file
with open('config\\remote_db_config.json') as f:
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

news_table_name='cg_news'
post_table_name='cg_post_table'
Base = declarative_base() 

# Define a model (example table "NewsBase")
class NewsBase(Base):
        __tablename__ = news_table_name

        id = Column(Integer, primary_key=True, autoincrement=True)

        title = Column(String(200))
        link = Column(String(200))
        newspaper=Column(String(200))
        keyword=Column(String(50))
        content=Column(String(500))
        date_ad = Column(String(15))
        date_bs = Column(String(15))

class PostBase(Base):
        __tablename__ = post_table_name

        id = Column(Integer, primary_key=True, autoincrement=True)

        platform = Column(String(50))
        keyword = Column(String(50))
        profile=Column(String(100))
        caption=Column(String(500))
        link=Column(String(200))
        date=Column(String(50))

def fetch_news(session,NewsBase):
        results = session.query(NewsBase).all()
        session.close()
        return results

def fetch_post(session,PostBase):
        results = session.query(PostBase).all()
        session.close()
        return results
        
def main(credentials,receiver,csv_file):
     
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
            # Now you can use the 'engine' object to interact with the PostgreSQL database
        except Exception as e:
            print(f"Error: {e}")

        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        send(credentials,receiver,csv_file,session)


def send(credentials,receiver,csv_file,session):
        
        results= fetch_news(session,NewsBase)
        posts= fetch_post(session,PostBase)
        nepali_date = nepali_datetime.date.today().strftime('%Y-%m-%d')
        eng_date = datetime.now().strftime('%Y-%m-%d')
        receivers = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for item in reader:
                # print(item)
                try:
                    if(len(item['Emails'])==0):
                        continue
                    receivers.append(item['Emails'])
                except Exception as e:
                    print(f"Exception: {e}")

        print(receivers)    
        with open(credentials) as js:
            '''
            look at the credentials.json file for the sample of json file
            '''
            jsn = json.load(js)
            Email_address = jsn['Email_address']
            Email_password = jsn['Email_password']

        # Attach image as MIMEImage
        message = MIMEMultipart()
        #Change the subject to your choice if you wish
        message['Subject'] = "Coverage Reporting News Articles"
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
            news_body = "<h2>Today's News:</h2>"

            # Append each article to the email body
            for result  in results:
                if(result.date_bs!=nepali_date) and (result.date_ad != eng_date):
                    continue
                news_body += f"""
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
            post_body = "<h2>Today's Posts:</h2>"
            for post  in posts:
                if(post.date != eng_date):
                    continue
                if(post.profile):
                     ref=f'https://twitter.com/{post.profile[1:]}'
                     profile=post.profile
                else:
                    ref=post.link
                    profile='Facebook User'

                post_body += f"""
                <div style="background-color:#f5f0f0;margin:10px 0;border-width:1px;border-style:solid;border-color:#f5f0f0;display:flex">
                    <div style="padding:0 2rem">
                                    <h3>{post.platform}</h3> 
                                    <h4>{post.keyword}</h4>
                                    <h4>{post.date}</h4>
                    </div>
                    <div style="padding-bottom:20px">              
                        <a style="text-decoration: none;" href={ref}><h3 style="color:red">{profile}</h3></a>
                        <div>
                            <p>{post.caption}
                                <a style="text-decoration: none;" href='{post.link}'>Read More...</a>
                            </p>
                        </div>
                    </div>
                </div>
                """

        html_content = f"""
                        <html>
                        <body>
                        <div style="display:block;text-align:center;width:100%">
                                
                                <div style="border: 1px solid #000; padding: 10px;text-align:left;">
                                        {news_body}
                                </div>
                                <div style="border: 1px solid #000; padding: 10px;text-align:left;">
                                        {post_body}
                                </div>
                        </div>
                        </body>
                        </html>
                        """
        message.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com',587) as smtp:
            smtp.starttls()
            try:
                smtp.login(Email_address, Email_password)
                print("Logged in to Email")
            except:
                print("Login Failed")

            print("Sending Email")
            try:
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
    parser.add_argument("-r", "--receiver", type=str, help="Email address of the receiver")
    parser.add_argument("-c", "--credentials", type=str, help="Path to the credentials json file")
    args = parser.parse_args()
    csv_file = args.filename
    # url = args.url
    credentials = args.credentials
    receiver = args.receiver
    main(credentials,receiver,csv_file)
    print("Mailing Complete")
