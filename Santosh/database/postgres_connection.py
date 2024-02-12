from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder
import json
from urllib.parse import urlparse
from datetime import datetime

def get_domain_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Define a declarative base
Base = declarative_base()

# ... (previous imports)

def main():
    with open('config\\remote_db_config.json') as f:
        config = json.load(f)

    # Access individual parameters
    ssh_host = config['ssh']['host']
    ssh_port = config['ssh']['port']
    ssh_username = config['ssh']['username']
    ssh_private_key = config['ssh']['private_key']
    print(ssh_private_key)
    postgres_host = config['postgres']['host']
    postgres_port = config['postgres']['port']
    postgres_user = config['postgres']['user']
    postgres_password = config['postgres']['password']
    postgres_db = config['postgres']['database']

    # Define a declarative base
    Base = declarative_base()

    # Define a model (example table "NewsBase")
    class NewsBase(Base):
        __tablename__ = 'bank_news'
        id = Column(Integer, primary_key=True, autoincrement=True)
        title = Column(String(200))
        link = Column(String(200))
        newspaper = Column(String(200))
        keyword = Column(String(50))
        content = Column(String(500))
        date_ad = Column(String(15))
        date_bs = Column(String(15))

    
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_pkey=ssh_private_key,
        remote_bind_address=(postgres_host, postgres_port),
        
    ) as tunnel:
        print("SSH Tunnel created successfully")

        try:
            engine = create_engine(
                f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{tunnel.local_bind_port}/{postgres_db}"
            )
            print("Connected to PostgreSQL server")

            Base.metadata.create_all(engine)
            # Now you can use the 'engine' object to interact with the PostgreSQL database
            Session = sessionmaker(bind=engine)
            session = Session()

            News = session.query(NewsBase).limit(10).all()
            for new in News:
                print(f"Title: {new.title}\t Link: {new.link}\t Date: {new.date_ad} \n Newspaper: {new.newspaper}\t Keyword: {new.keyword}\n Content: {new.content} \n")

            session.close()

        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")

    

if __name__ == "__main__":
    main()
