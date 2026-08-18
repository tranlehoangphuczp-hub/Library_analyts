import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://quotes.toscrape.com/"
response = requests.get(url)
html_doc = response.text
soup = BeautifulSoup(html_doc, "html.parser")
objects = soup.find_all("div", {"class": "quote"})
data_list = []
for object in objects:
    setence_tag = object.find("span", class_=  "text")
    quote = setence_tag.text
    author_tag = object.find("small", class_= "author")
    author = author_tag.text
    row = {
        "Câu noi": quote,
        "Tác giả": author
    }
    data_list.append(row)
df = pd.DataFrame(data_list)
df.to_csv("firsr_data_crawled.csv",sep = ";", index = False, encoding = "utf-8-sig")
print("Cào dữ liệu thành công!")
# sep: tách cột