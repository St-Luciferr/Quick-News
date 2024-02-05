import psycopg2
import datetime
import totalnews

# from news_list import news

news = totalnews.news


print("connection init")
try:
    connection = psycopg2.connect(
        user="test",
        password="password",
        host="18.217.209.236",
        port="5432",
        database="quicknews",
    )
    cursor = connection.cursor()
    print("conn cursor")

    # ---------------------------------------------------------------------------------------------------------------------------------------

    for newspaper in news:
        print(f"news paper:  {newspaper}\n")
        newspaper_name_dict = news[newspaper]  # kun newspaper
        newspaper_name = newspaper
        for topic in newspaper_name_dict:
            keywords = topic  # topic of each article

            topic_dict = newspaper_name_dict[topic]
            # print(f"{topic_dict}\n\n")
            for news_num in topic_dict:
                news_num_dict = topic_dict[news_num]
                title = news_num_dict["title"]
                link = news_num_dict["link"]
                date_ad = news_num_dict["date_ad"]
                date_bs = news_num_dict["date_bs"]
                content = news_num_dict["content"]
                postgres_insert_query = """ INSERT INTO newsbase (keyword, title, content, link, newspaper, date_ad, date_bs) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                now_time = datetime.datetime.now()
                # date = now_time.strftime("%Y-%m-%d")
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

                connection.commit()
                count = cursor.rowcount
                print(count, "Record inserted successfully into mobile table")

    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
# ---------------------------------------------------------------------------------------------------------------------------------------


except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into `test_news` table", error)
