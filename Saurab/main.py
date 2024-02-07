from pandas.core.ops import arithmetic_op
import requests
import feedparser
from bs4 import BeautifulSoup
import pandas as pd
import json
import nepali_datetime
import datetime

from sqlalchemy import except_
import date_utils


import psycopg2
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


def cg_news_csv(file):
    df = pd.read_csv(file)
    return df["Nepali"].tolist()


def cg_news_csv_english(file):
    df = pd.read_csv(file)
    return df["English"].tolist()


def newsbase_csv(file):
    df = pd.read_csv(file)
    return df["Nepali"].tolist()


def newsbase_csv_english(file):
    df = pd.read_csv(file)
    ss = df["English"].tolist()
    return [value for value in ss if isinstance(value, str)]


def scrape_ekantipur(topics, news, yesterday, today):
    newspaper = "ekantipur"
    print(f"ekantipur topics : {topics}\n")
    news[newspaper] = dict()

    for topic in topics:
        url = f"https://ekantipur.com/search/2003/?txtSearch={topic}&year=2024&date-from={yesterday}&date-to={today}"
        page = requests.get(url=url)

        soup = BeautifulSoup(page.content, "html.parser")

        div_with_article = soup.find("div", class_="tagList")
        news[newspaper][topic] = dict()

        if div_with_article:
            articles = div_with_article.find_all("article")
            for idx, each in enumerate(articles):
                date = each.find("time")

                if date:
                    conv_day, conv_month, conv_year = date_utils.get_eng_date(
                        date.text.split()
                    )
                    date = nepali_datetime.date(conv_year, conv_month, conv_day)
                    date_bs = date.strftime("%Y-%m-%d")
                    date_ad = date.to_datetime_date().strftime("%Y-%m-%d")

                    if nepali_datetime.datetime.now().strftime(
                        "%Y-%m-%d"
                    ) == nepali_datetime.datetime(
                        conv_year, conv_month, conv_day
                    ).strftime(
                        "%Y-%m-%d"
                    ):
                        title = (
                            each.find("div", class_="teaser offset")
                            .find("h2")
                            .find("a")
                            .text
                        )
                        link = each.find("a")["href"]
                        each_article_page = requests.get(link)
                        each_article_soup = BeautifulSoup(
                            each_article_page.content, "html.parser"
                        )

                        try:
                            content = each_article_soup.find(
                                "div", class_="current-news-block"
                            ).find_all("p")[0]
                        except:
                            content = None

                        if content:
                            content = content.text

                        news[newspaper][topic][idx] = {
                            "title": title,
                            "content": content,
                            "link": link,
                            "date_ad": date_ad,
                            "date_bs": date_bs,
                        }

    return news


def scrape_onlinemajdur(topics, news):
    print(f"onlinemajdur topics : {topics}\n")
    newspaper = "onlinemajdur"
    news[newspaper] = dict()

    for topic in topics:
        url = f"https://onlinemajdoor.com/?s={topic}"
        articles_list_page = requests.get(url=url)

        news[newspaper][topic] = dict()

        articles_list_soup = BeautifulSoup(articles_list_page.content, "html.parser")

        articles = (
            articles_list_soup.find("main", class_="main-wrapper")
            .find("div", class_="news-sty-two")
            .find("div", class_="row")
            .find_all("div", class_="item")
        )

        # for loop

        for idx, each_article in enumerate(articles):
            link = each_article.find("a")["href"]
            title = each_article.find("h3", class_="title").text

            each_article_page = requests.get(url=link)

            each_article_soup = BeautifulSoup(each_article_page.content, "html.parser")
            try:
                date = each_article_soup.find("ul", class_="comment-time").find("span")
            except AttributeError as e:
                print(e)
                exit()

            if date:
                conv_day, conv_month, conv_year = date_utils.get_eng_date(
                    date.text.split()
                )
                date = nepali_datetime.date(conv_year, conv_month, conv_day)
                date_bs = date.strftime("%Y-%m-%d")
                date_ad = date.to_datetime_date().strftime("%Y-%m-%d")

                # compare date and if today's date and article's date are same then append the scrapped news into news dict
                if nepali_datetime.datetime.now().strftime(
                    "%Y-%m-%d"
                ) == nepali_datetime.datetime(conv_year, conv_month, conv_day).strftime(
                    "%Y-%m-%d"
                ):
                    # -------------------------------- content scrapping ----------------------------------------------------
                    content = None
                    article_content = each_article_soup.find(
                        "div", class_="content single-news-text"
                    )
                    if article_content:
                        try:
                            content = article_content.find("p").text[:255] + "..."
                        except AttributeError:
                            continue
                    else:
                        continue

                    news[newspaper][topic][idx] = {
                        "title": title,
                        "content": content,
                        "link": link,
                        "date_ad": date_ad,
                        "date_bs": date_bs,
                    }

    return news


def rss_to_dict(url):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries:
        item_dict = {}
        item_dict["title"] = entry.title
        item_dict["link"] = entry.link
        item_dict["pubDate"] = entry.published
        item_dict["description"] = entry.summary
        items.append(item_dict)
    return items


def scrape_TheRisingNepalDaily(news, table):
    i = 0
    topics = list()
    if table == "cg_news":
        topics = cg_news_csv_english("./cg_news_keywords.csv")
    elif table == "newsbase":
        topics = newsbase_csv_english("./keywords_sbi.csv")
    elif table == "ncell_news":
        topics = [
            "ncell",
            "Ncell",
            "telecommunication",
            "Telecommunication",
            "telecom",
            "Telecom",
        ]

    print(f"TheRisingNepal topics : {topics}\n")
    url = "https://risingnepaldaily.com/rss"
    items = rss_to_dict(url)
    newspaper = "TheRisingNepal"
    news[newspaper] = dict()

    for topic in topics:
        news[newspaper][topic] = dict()
        for each in items:
            title = each["title"]
            link = each["link"]
            date = each["pubDate"]
            date_ad = date_utils.risingNepal_date_to(date)

            if topic in title:
                print(f"\n\n{link}")
                page = requests.get(link)
                article_soup = BeautifulSoup(page.content, "html.parser")
                content = (
                    article_soup.find("div", class_="rising-single-box-one")
                    .find_all("div", class_="blog-details")[3]
                    .find("p")
                    .text
                ).split(":")[1][1:]
                # print(content)

                news[newspaper][topic][i] = {
                    "title": title,
                    "content": content,
                    "link": link,
                    "date_ad": date_ad,
                    "date_bs": "",
                }
                i = i + 1
    return news


def scrape_himalkhabar(topics, news, from_date="", to_date=""):
    print(f"himalkhabar topics : {topics}\n")

    newspaper = "himalkhabar"
    news[newspaper] = dict()

    for topic in topics:
        url = f"https://www.himalkhabar.com/search?from={from_date}&to={to_date}&keyword={topic}"
        articles_list_page = requests.get(url=url)

        news[newspaper][topic] = dict()

        articles_list_soup = BeautifulSoup(articles_list_page.content, "html.parser")
        div_with_article = articles_list_soup.find_all(
            "div", class_="item-news alt-list media wow fadeIn"
        )
        for idx, each in enumerate(div_with_article):
            link = each.find("a")["href"]
            title = each.find("a").text

            each_article_page = requests.get(url=link)
            each_article_soup = BeautifulSoup(each_article_page.content, "html.parser")
            date = each_article_soup.find("span", class_="designation alt")
            content = (
                each_article_soup.find("div", class_="detail-box").find_all("p")[0].text
            )

            if date:
                conv_day, conv_month, conv_year = date_utils.get_eng_date(
                    date.text.split()[1:]
                )
                date = nepali_datetime.date(conv_year, conv_month, conv_day)
                date_bs = date.strftime("%Y-%m-%d")
                date_ad = date.to_datetime_date().strftime("%Y-%m-%d")

                if nepali_datetime.datetime.now().strftime(
                    "%Y-%m-%d"
                ) == nepali_datetime.datetime(conv_year, conv_month, conv_day).strftime(
                    "%Y-%m-%d"
                ):
                    news[newspaper][topic][idx] = {
                        "title": title,
                        "content": content,
                        "link": link,
                        "date_ad": date_ad,
                        "date_bs": date_bs,
                    }
    return news


def insert_into_remote_db(news, which_table):
    conn = None

    print(
        "\n----------------------------------------------------------------------------------------------------------------------\n\n"
    )
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
                        postgres_insert_query = f""" INSERT INTO {which_table} (keyword, title, content, link, newspaper, date_ad, date_bs) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
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


def choose_table():
    print(
        """
    Which table?
        1. cg_news
        2. newsbase
        3. ncell_news
    Enter the option: """,
        end="",
    )
    choice = int(input())

    if choice == 1:
        topics = cg_news_csv("./cg_news_keywords.csv")
        return "cg_news", topics
    elif choice == 2:
        topics = newsbase_csv("./keywords_sbi.csv")
        return "newsbase", topics
    elif choice == 3:
        topics = ["दुरसंचार", "एन्सियल", "एनसेल"]
        return "ncell_news", topics
    else:
        print("Invalid choice")
        print("terminatting the program")
        exit()


def main():
    ## creates a dictionary for storing news
    news_dict = dict()

    ## for date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    table, topics = choose_table()
    print("\n\n")

    news_dict = scrape_himalkhabar(topics, news_dict, today, today)
    news_dict = scrape_ekantipur(topics, news_dict, today, today)
    news_dict = scrape_onlinemajdur(topics, news_dict)
    news_dict = scrape_TheRisingNepalDaily(news_dict, table)

    print(json.dumps(news_dict, indent=4, ensure_ascii=False))
    print()
    insert_into_remote_db(news=news_dict, which_table=table)


if __name__ == "__main__":
    main()
