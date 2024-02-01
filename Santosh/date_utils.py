
# Mapping of Nepali month names to English month names
nepali_month_mapping = {
    'वैशाख': '01',
    'जेठ': '02',
    'असार': '03',
    'साउन': '04',
    'भदौ': '05',
    'असोज': '06',
    'कात्तिक': '07',
    'मंसिर': '08',
    'पुस': '09',
    'पुष': '09',
    'माघ': '10',
    'फागुन': '11',
    'चैत': '12',
}

nepali_to_english_digits = {
    '०': '0',
    '१': '1',
    '२': '2',
    '३': '3',
    '४': '4',
    '५': '5',
    '६': '6',
    '७': '7',
    '८': '8',
    '९': '9',
}

# Function to convert Nepali numbers to English
def convert_nepali_to_english(nepali_number):
    english_number = ''.join(nepali_to_english_digits.get(digit, digit) for digit in nepali_number)
    if(len(english_number)==1):
        english_number='0'+english_number
    return english_number

def get_eng_date(nepali_date):
    day, nepali_month, year, _ = nepali_date.split()
    english_month = nepali_month_mapping.get(nepali_month, nepali_month)
    eng_day=convert_nepali_to_english(day)
    eng_month=convert_nepali_to_english(english_month)
    eng_year=convert_nepali_to_english(year)
    if(eng_year[-1]==','):
        return int(eng_day),int(eng_month),int(eng_year[:-1])
    return int(eng_day),int(eng_month),int(eng_year)

# Function to get the date n days earlier
def get_date_ndays_earlier(date,n):
    year, month, day = date.split('-')
    day = int(day)
    month = int(month)
    year = int(year)
    if day <= n:
        if month == 1:
            day = 31 - (n - day)
            month = 12
            year -= 1
        else:
            month -= 1
            if month in [1, 3, 5, 7, 8, 10, 12]:
                day = 31 - (n - day)
            elif month in [4, 6, 9, 11]:
                day = 30 - (n - day)
            else:
                if year % 4 == 0:
                    day = 29 - (n - day)
                else:
                    day = 28 - (n - day)
    else:
        day -= n
    return f"{year}-{month}-{day}"



