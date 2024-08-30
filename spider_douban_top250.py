'''
2024/08/30
实现功能：
爬取了豆瓣网top250的电影名及评分
并保存在了本地数据库中
'''
import requests
from bs4 import BeautifulSoup
import pymysql

def douban_top250():
    try:
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/XX.0.0.0 Safari/537.36"
        }

        title_list=[]
        grade_list=[]
        for i in range(0,250,25):
            response = requests.get(f"https://movie.douban.com/top250?start={i}&filter=", headers = headers) #headers作为参数传入，把爬虫请求伪装成浏览器请求
            content = response.text #html
            soup = BeautifulSoup(content, "html.parser") #解析html

            all_titles = soup.findAll('span', attrs={'class': 'title'}) #查找信息
            all_grades = soup.findAll('span', attrs={'class': 'rating_num'})

            for title in all_titles:
                title = title.get_text().split('/')[0].strip()
                """
                获得的文本信息是‘电影中文名/电影原名’,以‘/’分开,
                用split按照‘/’划分为列表，并返回列表第一个值，
                strip去除文本内容前后空格
                """
                if title:
                    title_list.append(title)

            for grade in all_grades:
                grade = grade.get_text().strip()
                grade_list.append(grade)

        movie_list = [(i, title, grade) for i, title, grade in zip(range(1,251), title_list, grade_list)]
        return movie_list

    except Exception as e:
        print('在爬取豆瓣top250数据时发生异常：',e)
        raise  # 重新抛出异常

def database_connection(host, user, password, port, database, charset):
    connection = None
    try:
        connection = pymysql.connect(host=host, user=user, password=password,port=port, db=database, charset=charset)
        return connection
    except Exception as e:
        print('在连接数据库时发生异常：',e)
        raise  # 重新抛出异常

def add_data(cursor, data):
    try:
        sql = 'INSERT IGNORE INTO douban_movies(id, title, douban_grade) VALUES(%s, %s, %s)' #使用IGNORE避免主键值重复
        cursor.executemany(sql, data)
        cursor.connection.commit()
    except Exception as e:
        print('向数据库添加电影评分数据时发生异常：',e)
        raise  # 重新抛出异常

def truncate_data(cursor):
    try:
        sql = 'TRUNCATE TABLE douban_movies'
        cursor.execute(sql)
    except Exception as e:
        print('在清空数据时发生异常：',e)
        raise

def main():
    host = 'localhost' #主机名称一般来说都是localhost
    user = 'root'  #用户名
    password = '123456'  #密码
    port = 3306  #端口号
    database = 'MovieMate'  #选择数据库
    charset = 'utf8'

    try:
        with database_connection(host, user, password, port, database, charset) as connection:
            with connection.cursor() as cursor:
                truncate_data(cursor) #清空数据
                data = douban_top250()
                add_data(cursor, data)

    except Exception as e:
        print('在执行主函数main时发生异常：', e)
        raise

if __name__ == '__main__':
    main()
