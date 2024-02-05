import csv
import nepali_datetime
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import date_utils
from urllib.parse import urlparse
import time

def get_domain_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def create_date_list(date,n):
    date_list=[]
    for i in range(n):
        date_list.append(date_utils.get_date_ndays_earlier(date,i))
    return date_list

def scrape_annapurna(csv_file, url):
    receivers = []
    keywords = []
    results = []
    links=[]
    nepali_date = nepali_datetime.date.today().strftime('%Y-%m-%d')
    # date_list=create_date_list(nepali_date,1)
    eng_date = datetime.now().strftime('%Y-%m-%d')
    earlier_date = date_utils.get_date_ndays_earlier(eng_date, 1)

    print(f"Today's Date: {nepali_date}")
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for item in reader:
            try:
                receivers.append(item['User Emails'])
            except:
                pass
            try:
                keywords.append(item['Keywords'])
            except:
                pass

    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    total_count = 0
    # Perform a search for each keyword
    for keyword in keywords:
        search_url=f"{url.strip()}?q={keyword}"
        print(search_url)
        response = session.get(search_url.strip(), headers=headers, timeout=40)
        # print("status code", response.status_code)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')
            category = soup.find('div', class_='category__news')
            count = 0
            # Extract and print relevant information (adjust based on website structure)
            for article in category.find_all('div', class_='grid__card'):
                result={}
                title_element = article.find('h3', class_='card__title')
                title=title_element.get_text(strip=True)
                domain=get_domain_from_url(url)

                link = "https://"+domain+title_element.find('a')['href']
                content=article.find('div',class_='card__desc')
                post=session.get(link.strip(), headers=headers, timeout=40)
                if post.status_code == 200:
                    post_soup = BeautifulSoup(post.content, 'html.parser')
                    date_element=post_soup.find('p', class_='date')
                    # date=date_element.find('time').get_text(strip=True)
                    full_date=date_element.get_text(strip=True)
                    split_date=full_date.split()
                    nepali_date=split_date[1][:-1]+" "+split_date[0]+" "+split_date[2]+" "+split_date[3]
                    date = date_utils.get_eng_date(nepali_date)
                    formated_date = f"{date[2]}-{date[1]}-{date[0]}"
                    date_in_AD=nepali_datetime.date(date[2], date[1], date[0]).to_datetime_date()
                    
                    # print(formated_date)
                    
                else:
                    print(
                        f"Error: Unable to retrieve data. Status Code: {post.status_code}")
                    
                # print(formated_date)
                # print(f"formated_date:{formated_date},date_list:{date_list}")
                # exit()
                if(formated_date ==nepali_date):
                    # print(date_list)
                    links.append(link)
                    # print(f"Title: {title}, Link: {link}, Date: {formated_date}")
                # if (formated_date):
                    result = {}
                    # print(f"Title: {title}, Link: {link}")
                    result['title'] = title
                    result['link'] = link
                    result['keyword'] = keyword
                    result['date_bs'] = formated_date
                    result['date_ad'] = date_in_AD.strftime('%Y-%m-%d')
                    result['content']=content.get_text(strip=True)
                    result['domain']="Annapurna Post"
                    results.append(result)
                    # print(results)
                    # exit()
                    # print(f"Title:{result['title']  }, Link:{result['link']}, Keyword:{result['keyword']}, Date:{result['date']}\n Desc:{result['desc']}")
                    count += 1
            
        else:
            print(
                f"Error: Unable to retrieve data. Status Code: {response.status_code}")
        total_count += count
        print(f"Total {count} articles found for {keyword}")
        time.sleep(10)
    print(f"Total {total_count} articles found for all keywords")
    return results

if __name__ == "__main__":
    scrape_annapurna("data.csv","https://www.annapurnapost.com/search")