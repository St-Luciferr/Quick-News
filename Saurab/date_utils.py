# Mapping of Nepali month names to English month names
from datetime import datetime


nepali_month_mapping = {
    "वैशाख": "01",
    "बैशाख": "01",
    "जेठ": "02",
    "जेष्ठ": "02",
    "असार": "03",
    "श्रावण": "04",
    "साउन": "04",
    "भदौ": "05",
    "भाद्र": "05",
    "असोज": "06",
    "आश्विन": "06",
    "आश्वयुज": "06",
    "कार्तिक": "07",
    "कात्तिक": "07",
    "मंसिर": "08",
    "पुष": "09",
    "पुस": "09",
    "माघ": "10",
    "फागुन": "11",
    "फाल्गुन": "11",
    "चैत्र": "12",
    "चैत": "12",
}

nepali_to_english_digits = {
    "०": "0",
    "१": "1",
    "२": "2",
    "३": "3",
    "४": "4",
    "५": "5",
    "६": "6",
    "७": "7",
    "८": "8",
    "९": "9",
}


def risingNepal_date_to(date_string):

    date_object = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")

    # Format the date in the desired format
    formatted_date = date_object.strftime("%Y-%m-%d")
    return formatted_date


# Function to convert Nepali numbers to English
def convert_nepali_to_english(nepali_number):
    english_number = "".join(
        nepali_to_english_digits.get(digit, digit) for digit in nepali_number
    )
    return english_number


def get_eng_date(nepali_date):
    nepali_month, nepali_day, nepali_year = nepali_date
    eng_month = nepali_month_mapping.get(nepali_month, nepali_month)
    eng_day = convert_nepali_to_english(nepali_day[:-1])
    # eng_month = convert_nepali_to_english(nepali_month)
    eng_year = convert_nepali_to_english(nepali_year)
    # print(f"nepali month : {nepali_month} -> month in english : {eng_month}")
    # print(f"nepali day   : {nepali_day} ->   month in english : {eng_day}")
    # print(f"nepali year  : {nepali_year} ->  month in english : {eng_year}")
    return int(eng_day), int(eng_month), int(eng_year)
