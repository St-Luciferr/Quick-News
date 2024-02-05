import requests
from bs4 import BeautifulSoup
import pandas as pd

import json
import nepali_datetime
import datetime

from requests.models import parse_header_links
import date_utils


from mail import send_mail


def return_from_csv(file):
    df = pd.read_csv(file)
    return df["Nepali"].tolist()


def scrape_ekantipur(topics, news, yesterday, today):
    newspaper = "ekantipur"
    print(f"ekantipur topics : {topics}")
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
                        content = (
                            each_article_soup.find("div", class_="current-news-block")
                            .find_all("p")[0]
                            .text
                        )
                        # print("\n\n")
                        # print(
                        #     "|-----------------------------------------------------------------------------------------------------------|"
                        # )
                        # print(f"date : {date}")
                        # print(f"link : {link}")
                        # print(f"title : {title}")
                        # print(f"contnet: {content}")
                        # print(
                        #     "|-----------------------------------------------------------------------------------------------------------|"
                        # )
                        # print(date)
                        # print(f"{conv_year}-{conv_month}-{conv_day}")
                        news[newspaper][topic][idx] = {
                            "title": title,
                            "content": content,
                            "link": link,
                            "date_ad": date_ad,
                            "date_bs": date_bs,
                        }

    return news


def scrape_onlinemajdur(topics, news):
    print(f"online majdur topics : {topics}")
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
            # print(
            #     "|-----------------------------------------------------------------------------------------------------------|"
            # )
            # print(f"newspaper : {newspaper}")
            # print(f"link : {link}")
            # print(f"title : {title}")
            try:
                date = each_article_soup.find("ul", class_="comment-time").find("span")
            except AttributeError as e:
                print(e)
                exit()

            # print(f"date : {date.text}")

            # -------------------------------- content scrapping ----------------------------------------------------
            content = None
            article_content = each_article_soup.find(
                "div", class_="content single-news-text"
            )
            if article_content:
                try:
                    content = article_content.find("p").text[:255] + "..."
                    # first_br_tag = p_element.find("br")
                    # content = "".join(
                    #     p_element.contents[: p_element.contents.index(first_br_tag)]
                    # )
                except AttributeError:
                    continue
            else:
                continue
            # print(f"contnet: {content}")
            # print(
            #     "|-----------------------------------------------------------------------------------------------------------|\n"
            # )

            if date:
                conv_day, conv_month, conv_year = date_utils.get_eng_date(
                    date.text.split()
                )
                date = nepali_datetime.date(conv_year, conv_month, conv_day)
                date_bs = date.strftime("%Y-%m-%d")
                date_ad = date.to_datetime_date().strftime("%Y-%m-%d")
                # print(f"{conv_year}-{conv_month}-{conv_day}")
                #
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


def scrape_himalkhabar(topics, news, from_date="", to_date=""):
    print(f"himalkhabar topics : {topics}")

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
        # print(f"topic : {topic}")

        # print(f"TOPIC : {topic}\n")
        for idx, each in enumerate(div_with_article):
            link = each.find("a")["href"]
            title = each.find("a").text

            each_article_page = requests.get(url=link)
            each_article_soup = BeautifulSoup(each_article_page.content, "html.parser")
            date = each_article_soup.find("span", class_="designation alt")
            content = (
                each_article_soup.find("div", class_="detail-box").find_all("p")[0].text
            )
            # print(
            #     "|-----------------------------------------------------------------------------------------------------------|\n"
            # )
            # print("\n\n")
            # print(f"date : {date}")
            # print(f"link : {link}")
            # print(f"title : {title}")
            # print(f"content: {content}")
            # print(
            #     "|-----------------------------------------------------------------------------------------------------------|\n"
            # )

            if date:
                conv_day, conv_month, conv_year = date_utils.get_eng_date(
                    date.text.split()[1:]
                )
                # print(f"{conv_year}-{conv_month}-{conv_day}")
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


def main():
    news_dict = dict()
    topics = return_from_csv("./nepali_keyword.csv")
    topics = ['दुरसंचार', 'एन्सियल', 'एनसेल']
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime(
        "%Y-%m-%d"
    )

    # print("before")
    news_dict = scrape_onlinemajdur(topics, news_dict)
    news_dict = scrape_himalkhabar(topics, news_dict, today, today)
    news_dict = scrape_ekantipur(topics, news_dict, today, today)
    print(json.dumps(news_dict, indent=4, ensure_ascii=False))
    return news_dict


if __name__ == "__main__":
    main()
