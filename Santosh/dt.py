from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder
from sqlalchemy.orm import declarative_base
import json
from scrape_annapurna import scrape_annapurna
from scrape_gorkhapatra import scrape_gorkhapatra

data_file='keyword.csv'

table_name='cg_news'
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
    # results=scrape_gorkhapatra(data_file,"https://gorkhapatraonline.com/news-search")
    # for result in results:
    #     new_news = NewsBase(
    #         title=result['title'],
    #         link=result['link'],
    #         newspaper=result['domain'],
    #         keyword=result['keyword'],
    #         content=result['desc'],
    #         date_bs=result['date_bs'],
    #         date_ad=result['date_ad']
    #     )
    #     session.add(new_news)
    # try: 
    #     session.commit()
    #     print("Data from Gorkhapatra added Suceessfully")
    # except Exception as e:
    #     print(f"Error: {e}")

    res=scrape_annapurna(data_file,"https://www.annapurnapost.com/search")
    for result in res:
        new_news = NewsBase(
            title=result['title'],
            link=result['link'],
            newspaper=result['domain'],
            keyword=result['keyword'],
            content=result['desc'],
            date_bs=result['date_bs'],
            date_ad=result['date_ad']
        )
        session.add(new_news)
    try: 
        session.commit()
        print("Data from Annapurna added Suceessfully")
    except Exception as e:
        print(f"Error: {e}")
         
    News = session.query(NewsBase).limit(10).all()
    for new in News:
        print(f"Title: {new.title}\t Link: {new.link}\t Date: {new.date} \n Newspaper: {new.newspaper}\t Keyword: {new.keyword}\n Content: {new.content} \n")

    session.close()