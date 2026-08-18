import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# Fake người dùng thật:
chrome_options = Options()

# Thêm một User-Agent giả lập trình duyệt của người dùng thật
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Khởi chạy driver với cấu hình người dùng ảo
driver = webdriver.Chrome(options=chrome_options)

# Vào trang thông tin cần đào dữ liệu
url = "https://shopee.vn/search?keyword=b%C3%A0n%20ph%C3%ADm%20c%C6%A1"
driver.get(url)

# Setup time lượt tải đầu
time.sleep(5)
driver.execute_script("window.scrollTo(0,1000);")

# -----Dùng bs4 để lấy dữ liệu-----
html_source = driver.page_source
driver.quit()
soup = BeautifulSoup(html_source, "html.parser")
products = soup.find_all("div", {"data-sqe": "item"})
print(products)
