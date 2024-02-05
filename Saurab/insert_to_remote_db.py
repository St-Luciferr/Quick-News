import psycopg2
import datetime
from main import main
import totalnews

news = main()

from sshtunnel import SSHTunnelForwarder


# Replace these values with your actual SSH and database connection details
ssh_params = {
    "ssh_address_or_host": "18.217.209.236",
    "ssh_username": "ubuntu",
    "ssh_pkey": "/home/saurab/Downloads/quickfox/rpa-dev.pem",
    "remote_bind_address": ("127.0.0.1", 5432),
}

# Replace these values with your actual database connection details
db_params = {
    "host": "localhost",
    "port": 5432,
    "database": "quicknews",
    "user": "test",
    "password": "password",
}

conn = None

try:
    # Create an SSH tunnel
    with SSHTunnelForwarder(**ssh_params) as tunnel:
        print(f"Tunnel established at localhost:{tunnel.local_bind_port}")

        # Establish a connection to the PostgreSQL server through the SSH tunnel
        conn = psycopg2.connect(
            host="localhost",
            port=tunnel.local_bind_port,
            user=db_params["user"],
            database=db_params["database"],
            password=db_params["password"],
        )
        cursor = conn.cursor()

        # news = main()
        for newspaper in news:
            print(f"news paper:  {newspaper}\n")
            newspaper_name_dict = news[newspaper]  # kun newspaper
            newspaper_name = newspaper
            for topic in newspaper_name_dict:
                keywords = topic  # topic of each article

                topic_dict = newspaper_name_dict[topic]
                for news_num in topic_dict:
                    news_num_dict = topic_dict[news_num]
                    title = news_num_dict["title"]
                    link = news_num_dict["link"]
                    date_ad = news_num_dict["date_ad"]
                    date_bs = news_num_dict["date_bs"]
                    content = news_num_dict["content"]
                    postgres_insert_query = """ INSERT INTO cg_news (keyword, title, content, link, newspaper, date_ad, date_bs) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                    record_to_insert = (
                        keywords,
                        title,
                        content,
                        link,
                        newspaper_name,
                        date_ad,
                        date_bs,
                    )
                    cursor.execute(postgres_insert_query, record_to_insert)

                    conn.commit()
                    count = cursor.rowcount
                    print(count, "Record inserted successfully into mobile table")


except psycopg2.Error as e:
    print("Unable to connect to the database.")
    print(e)

finally:
    # Close the cursor and connection
    if conn:
        conn.close()
        print("Connection closed.")
