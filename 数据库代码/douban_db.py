'''
通过mysql实现douban数据的创建及管理（增删改查）
'''
import pymysql
import pandas as pd

# 创建数据库
def create_database(cursor, database):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        print(f"数据库 {database} 创建或已存在。")
    except Exception as e:
        print('创建数据库时发生异常：', e)
        raise

# 创建douban_movies数据表
def create_douban_table(cursor):
    try:
        sql = '''
        CREATE TABLE IF NOT EXISTS douban_movies (
            director VARCHAR(255) NOT NULL,
            starring VARCHAR(255) NOT NULL,
            genre VARCHAR(255) NOT NULL,
            region VARCHAR(255) NOT NULL,
            year VARCHAR(255) NOT NULL,
            detail_url VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            rating VARCHAR(255) NOT NULL,
            rating_count VARCHAR(255) NOT NULL,
            poster_url VARCHAR(255) NOT NULL
        )
        '''
        cursor.execute(sql)
        print("数据表 douban_movies 创建或已存在。")
    except Exception as e:
        print('创建数据表时发生异常：', e)
        raise

def add_all_douban_data(cursor, data):
    try:
        sql = 'INSERT IGNORE INTO douban_movies(director, starring, genre, region, year, detail_url, title, rating, rating_count, poster_url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.executemany(sql, data)
        cursor.connection.commit()
        print(f"成功添加 {cursor.rowcount} 条数据。")
    except Exception as e:
        print('添加所有数据时发生异常：', e)
        raise

def delete_all_douban_data(cursor):
    try:
        sql = 'TRUNCATE TABLE douban_movies'
        cursor.execute(sql)
        print("所有数据已删除。")
    except Exception as e:
        print('删除所有数据时发生异常：', e)
        raise

# 通过电影名称查找单条数据
def search_single_douban_data_by_title(cursor, title):
    try:
        sql = 'SELECT * FROM douban_movies WHERE title = %s'
        cursor.execute(sql, (title,))
        result = cursor.fetchone()
        if result:
            print("查询结果：", result)
        else:
            print("未找到匹配的数据。")
        return result
    except Exception as e:
        print('查询数据库电影评分数据时发生异常：', e)
        raise

# # 读取csv文件
# def read_csv(file_path):
#     try:
#         return pd.read_csv(file_path, dtype=str).values.tolist()
#     except Exception as e:
#         print('读取CSV文件时发生异常：', e)
#         raise

def read_excel(file_path):
    try:
        # 读取 Excel 文件
        df = pd.read_excel(file_path, dtype=str)
        # 替换 NaN 值为 ''
        df.fillna('', inplace=True)
        # 将 DataFrame 转换为列表
        return df.values.tolist()
    except Exception as e:
        print('读取Excel文件时发生异常：', e)
        raise

def main():
    host = 'localhost'
    user = 'root'
    password = '123456'
    port = 3306
    database = 'MovieMate'
    charset = 'utf8'

    try:
        connection = pymysql.connect(host=host, user=user, password=password, port=port, charset=charset)
        with connection.cursor() as cursor:
            create_database(cursor, database)
            cursor.execute(f"USE {database}")

            create_douban_table(cursor)

            file_path = r'../爬取网站代码/豆瓣电影.xlsx'
            data = read_excel(file_path)

            print('数据长度', len(data))

            #delete_all_douban_data(cursor)
            add_all_douban_data(cursor, data)
            print("数据添加完成。")

            print("准备查询数据...")
            search_movie_title = input('请输入要查询的电影的名称：')
            if search_movie_title.strip():
                result = search_single_douban_data_by_title(cursor, search_movie_title)
            else:
                print("未输入有效的电影名称。")

    except Exception as e:
        print('在执行主函数main时发生异常：', e)
        raise
    finally:
        print("程序执行完毕")

if __name__ == '__main__':
    main()