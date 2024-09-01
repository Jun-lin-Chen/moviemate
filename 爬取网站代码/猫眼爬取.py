import requests
from bs4 import BeautifulSoup
import csv

from docutils.nodes import reference
from httpx import Cookies

# 目标网页的URL（假设URL为网页中HTML的实际地址）
url = "https://www.maoyan.com/films?showType=3&offset=30"  # 替换为实际的URL
headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Cookies' :'uuid_n_v=v1; uuid=42CB869066AB11EF9D9773DF9DC75471F2325BCA42E54890BF2195D73349008E; _csrf=4f55617590df55d00dab4158ef19d7a00caf6fb748619b5fcf487e6d14ce0d7f; _lxsdk_cuid=191a26fd241c8-09a26803cb73fd-48667e53-1cb600-191a26fd241c8; HMACCOUNT=48E5DF09246748FD; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1725007123; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; WEBDFPID=0vvvvz294y5454yxyzyzzu4ww22xv7w3808z71y8xv4979587w6wu4wz-2040368911171-1725008910129MIGOSWOfd79fef3d01d5e9aadc18ccd4d0c95071503; token=AgEqIDOn2XpMhUexKIWiSMWUVle6sIwMq5aKmTx3NNG9e_zEGJ1W9P1ut0fzQylqWwvy6XvaJwh5DAAAAABrIgAAFE8ZU22PbxF8zjPt3Zj5iBgmgkMDrc4WZiGqCiqsqCGy0kZZvQihR8eY-pwqdOdw; uid=3697692006; uid.sig=rsNz7_NASMgCIsv3kYQDP1W-eGc; _lxsdk=42CB869066AB11EF9D9773DF9DC75471F2325BCA42E54890BF2195D73349008E; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1725008947; __mta=208017325.1725007123161.1725008860134.1725008946963.23; _lxsdk_s=191a26fd242-63-a84-060%7C%7C62',
    'Reference':'https://passport.maoyan.com/'
}


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
        title_tag = item.find("div", class_="channel-detail movie-item-title")
        title = title_tag.text.strip() if title_tag else "N/A"

        # 提取评分
        rating_tag = item.find("div", class_="channel-detail channel-detail-orange")
        rating = rating_tag.text.strip() if rating_tag else "N/A"

        # 提取电影详细信息
        hover_info = item.find("div", class_="movie-item-hover")
        if hover_info:
            # 提取类型
            type_tag = hover_info.find("div", title="刺猬")  # 这里的"title"可以根据实际数据调整
            type_text = type_tag.text.strip().split("类型:")[1] if type_tag and "类型:" in type_tag.text else "N/A"

            # 提取主演
            cast_tag = hover_info.find("div", title="刺猬")
            cast_text = cast_tag.text.strip().split("主演:")[1] if cast_tag and "主演:" in cast_tag.text else "N/A"

            # 提取上映日期
            date_tag = hover_info.find("div", title="刺猬")
            date_text = date_tag.text.strip().split("上映时间:")[
                1] if date_tag and "上映时间:" in date_tag.text else "N/A"

        else:
            type_text, cast_text, date_text = "N/A", "N/A", "N/A"

        # 提取图片URL
        image_tag = item.find("img", class_="poster-default")
        image_url = image_tag["src"].strip() if image_tag else "N/A"

        # 写入电影信息到CSV文件
        csv_writer.writerow([title, rating, type_text, cast_text, date_text, image_url])

print("电影信息已写入到movies.csv。")