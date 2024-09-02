import requests
from bs4 import BeautifulSoup
import csv

from docutils.nodes import reference
from httpx import Cookies
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
import cv2
from selenium.webdriver import ActionChains
import requests
from io import BytesIO
from bs4 import BeautifulSoup
import csv



# 目标网页的URL（假设URL为网页中HTML的实际地址）
url = "https://www.maoyan.com/films?showType=3&offset=30"  # 替换为实际的URL
headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Cookies' :'uuid_n_v=v1; uuid=42CB869066AB11EF9D9773DF9DC75471F2325BCA42E54890BF2195D73349008E; _csrf=4f55617590df55d00dab4158ef19d7a00caf6fb748619b5fcf487e6d14ce0d7f; _lxsdk_cuid=191a26fd241c8-09a26803cb73fd-48667e53-1cb600-191a26fd241c8; HMACCOUNT=48E5DF09246748FD; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1725007123; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; WEBDFPID=0vvvvz294y5454yxyzyzzu4ww22xv7w3808z71y8xv4979587w6wu4wz-2040368911171-1725008910129MIGOSWOfd79fef3d01d5e9aadc18ccd4d0c95071503; token=AgEqIDOn2XpMhUexKIWiSMWUVle6sIwMq5aKmTx3NNG9e_zEGJ1W9P1ut0fzQylqWwvy6XvaJwh5DAAAAABrIgAAFE8ZU22PbxF8zjPt3Zj5iBgmgkMDrc4WZiGqCiqsqCGy0kZZvQihR8eY-pwqdOdw; uid=3697692006; uid.sig=rsNz7_NASMgCIsv3kYQDP1W-eGc; _lxsdk=42CB869066AB11EF9D9773DF9DC75471F2325BCA42E54890BF2195D73349008E; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1725008947; __mta=208017325.1725007123161.1725008860134.1725008946963.23; _lxsdk_s=191a26fd242-63-a84-060%7C%7C62',
    'Reference':'https://passport.maoyan.com/'
}
# 配置Selenium WebDriver
options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")  # 无头模式（可选）
browser = webdriver.Edge(options=options)

wait = WebDriverWait(browser, 5)

# 打开网页
browser.get(url)

# 等待10秒钟
time.sleep(10)

# 获取当前页面的URL
current_url = browser.current_url



# 发起请求获取网页内容
response = requests.get(url,headers=headers)
html_content = response.text
print(html_content)

# 创建BeautifulSoup对象来解析HTML
soup = BeautifulSoup(html_content, "html.parser")

# 打开CSV文件准备写入电影信息
with open("movies.csv", mode="w", newline="", encoding="utf-8") as file:
    csv_writer = csv.writer(file)
    # 写入CSV文件的标题行
    csv_writer.writerow(["影片名称", "评分", "类型", "主演", "上映日期", "图片URL"])

    # 查找所有电影项
    movie_items = soup.find_all("div", class_="movie-item film-channel")

    for item in movie_items:
        # 提取影片名称
        title_tag = item.find("span", class_="name")
        title = title_tag.text.strip() if title_tag else "N/A"

        # 提取评分
        rating_tag = item.find("span", class_="score channel-detail-orange")
        rating = rating_tag.text.strip() if rating_tag else "暂无评分"

        # 提取电影详细信息
        hover_info = item.find("div", class_="movie-item-hover")
        if hover_info:
            # 提取类型
            type_text = "N/A"
            for div in hover_info.find_all("div", class_="movie-hover-title"):
                if "类型:" in div.get_text():
                    type_text = div.get_text(strip=True).split("类型:")[1].strip()
                    break

            # 提取主演
            cast_text = "N/A"
            for div in hover_info.find_all("div", class_="movie-hover-title"):
                if "主演:" in div.get_text():
                    cast_text = div.get_text(strip=True).split("主演:")[1].strip()
                    break

            # 提取上映日期
            date_text = "N/A"
            for div in hover_info.find_all("div", class_="movie-hover-title"):
                if "上映时间:" in div.get_text():
                    date_text = div.get_text(strip=True).split("上映时间:")[1].strip()
                    break

            # print("类型:", type_text)
            # print("主演:", cast_text)
            # print("上映时间:", date_text)
        else:
            print("No hover_info found")

        # 提取图片 URL
        image_tag = item.find("img", class_="movie-hover-img")
        image_url = image_tag["src"].strip() if image_tag and "src" in image_tag.attrs else "N/A"

        # 写入电影信息到 CSV 文件
        csv_writer.writerow([title, rating, type_text, cast_text, date_text, image_url])

print("电影信息已写入到 movies.csv。")

# 关闭浏览器
browser.quit() 
