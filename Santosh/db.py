from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from scrape_gorkhapatra import scrape
import argparse
import json
from urllib.parse import urlparse
from datetime import datetime

def get_domain_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Define a declarative base
Base = declarative_base()
    
# Define a model (example table "NewsBase")
class NewsBase(Base):
        __tablename__ = 'newsbase'

        id = Column(Integer, Sequence('id'), primary_key=True)
        title = Column(String(200))
        link = Column(String(200))
        domain=Column(String(200))
        keyword=Column(String(50))
        date=Column(String(50))
        

def insert_data(database_config,csv_file,url):
    domain=get_domain_from_url(url)
    date = datetime.now().strftime('%Y-%m-%d')
    print(domain)
    # exit()
    results=scrape(csv_file, url)
    with open(database_config, 'r') as json_file:
        connection_details = json.load(json_file)
    # Construct the database URL
    DATABASE_URL = f"postgresql://{connection_details['user']}:{connection_details['password']}@{connection_details['host']}:{connection_details['port']}/{connection_details['dbname']}"
    remote_url="mysql+mysqlconnector://<user>:<pass>@<addr>/<schema>"
    # Create an SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Create the table in the database
    Base.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    for result in results:
        new_news = NewsBase(
            title=result['title'],
            link=result['link'],
            domain=domain,  
            keyword=result['keyword'],
            date=result['date']
        )
        session.add(new_news)
    session.commit()

    # Query and print all News
    News = session.query(NewsBase).all()
    for new in News:
        print(f"News ID: {new.id}, Title: {new.title}, Link: {new.link},keyword: {new.keyword},date: {new.date}")

    # Close the session
    session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="scrapes keywords from news website")
    parser.add_argument("-f", "--csvfile", type=str,
                        help="Path to the csv file containing keywords")
    parser.add_argument("-u", "--url", type=str, help="URL to scrape")
    parser.add_argument("-c", "--config", type=str, help="Path to the database config json file")
    args = parser.parse_args()
    csv_file = args.csvfile
    url = args.url
    database_config = args.config
    insert_data(database_config,csv_file,url)

    print("Inserting Complete")