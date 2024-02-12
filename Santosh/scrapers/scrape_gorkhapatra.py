import csv
import requests
import argparse
from bs4 import BeautifulSoup
from datetime import datetime
from utils import date_utils
import nepali_datetime

def create_date_list(date,n):
    date_list=[]
    for i in range(n):
        date_list.append(date_utils.get_date_ndays_earlier(date,i))
    return date_list

def scrape_gorkhapatra(csv_file, url):
    receivers = []
    keywords = []
    results = []
    nepali_date = nepali_datetime.date.today().strftime('%Y-%m-%d')
    print(nepali_date)
    date_list=create_date_list(nepali_date,10)
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
    get_response = session.get(url.strip(), headers=headers, timeout=10)
    xsrf_token_cookie = session.cookies.get("XSRF-TOKEN")
    cookies = {'XSRF-TOKEN': xsrf_token_cookie}
    # Check if the GET request was successful (status code 200)
    if get_response.status_code == 200:
        # Parse the HTML content of the GET response
        soup = BeautifulSoup(get_response.content, 'html.parser')
        # Extract the CSRF token from the form
        csrf_token = soup.find('input', {'name': '_token'})['value']
        print(f"CSRF Token: {csrf_token}")
    else:
        print(
            f"Error: Unable to retrieve data. Status Code: {response.status_code}")
        exit()

    total_count = 0
    # Perform a search for each keyword
    key_count=0
    for keyword in keywords:
        key_count+=1
        search_params = {
            '_token': csrf_token,
            'keywords': keyword,
            'from': earlier_date,
            'to': eng_date,
        }
        # search_url = f'{url}?q={keyword}'
        response = session.post(
            url.strip(), cookies=cookies, data=search_params, headers=headers, timeout=10)

        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')
            count = 0
            # Extract and print relevant information (adjust based on website structure)
            for article in soup.find_all('div', class_='blog-box-layout1 text-left squeezed mb-0'):
                title = article.find('h2', class_='item-title').text
                desc=article.find('p').text[:300]

                link = article.find('a')['href']

                li_with_i = article.find(
                    'i', class_='fas fa-calendar-alt').parent
                date_text = li_with_i.get_text(strip=True)
                date = date_utils.get_eng_date(date_text)
                formated_date = f"{date[2]}-{date[1]}-{date[0]}"
                date_in_AD=nepali_datetime.date(date[2], date[1], date[0]).to_datetime_date()
                # print(formated_date)
                # exit()
                # if(formated_date in date_list):
                if (formated_date==nepali_date):
                    print(formated_date,nepali_date)
                    result = {}
                    # print(f"Title: {title}, Link: {link}")
                    result['title'] = title
                    result['link'] = link
                    result['keyword'] = keyword
                    result['date_bs'] = formated_date
                    result['date_ad'] = date_in_AD.strftime('%Y-%m-%d')
                    result['content']=desc
                    result['domain']= "Gorkhapatra"
                    results.append(result)
                    count += 1
        else:
            print(
                f"Error: Unable to retrieve data. Status Code: {response.status_code}")

        print(f"{key_count}: Total {count} articles found for {keyword}")
        total_count += count
    print(f"Total {total_count} articles found for all keywords")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="scrapes keywords from news website")
    parser.add_argument("-f", "--filename", type=str,
                        help="Path to the csv file containing keywords")
    parser.add_argument("-u", "--url", type=str, help="URL to scrape")
    args = parser.parse_args()
    csv_file = args.filename
    url = args.url
    scrape_gorkhapatra(csv_file, url)
    print("Scraping Complete")
