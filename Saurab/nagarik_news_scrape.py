from re import search
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()
driver.get("https://nagariknews.nagariknetwork.com/search")

title = driver.title
print(title)

search_box = driver.find_element(by=By.ID, value="txtSearch")
submit_button = driver.find_element(
    by=By.XPATH, value="//input[@class='commentBtnText btn btn-primary']"
)


search_box.send_keys("भ्रष्टाचार")
submit_button.click()

sleep(10)


list_of_articles = driver.find_element(by=By.XPATH, value="//div[@class='articles']")
print(list_of_articles.get_attribute("outterHTML"))

# driver.quit()
