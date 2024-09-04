'''
实现数据库的创建及管理（增删改查）
注：运行之前需要在本地安装mysql
'''
import pymysql
import pandas as pd

# 连接数据库
def database_connection(host, user, password, port, database, charset):
    connection = None
    try:
        connection = pymysql.connect(host=host, user=user, password=password, port=port, db=database, charset=charset)
        return connection
    except Exception as e:
        print('在连接数据库时发生异常：', e)
        raise  # 重新抛出异常

# 创建数据库
def create_database(cursor, database):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        print(f"数据库 {database} 创建或已存在。")
    except Exception as e:
        print('创建数据库时发生异常：', e)
        raise

# 创建maoyan_movies数据表
def create_maoyan_movies_table(cursor):
    try:
        sql = '''
        CREATE TABLE IF NOT EXISTS maoyan_movies (
            title VARCHAR(255) NOT NULL,
            grade FLOAT,
            genre VARCHAR(255),
            cast VARCHAR(255),
            release_date DATE,
            image_url VARCHAR(255),
            PRIMARY KEY (title)
        )
        '''
        cursor.execute(sql)
        print("数据表 maoyan_movies 创建或已存在。")
    except Exception as e:
        print('创建数据表时发生异常：', e)
        raise

def read_csv(file_path):
    try:
        # 读取 CSV 文件到 DataFrame
        data = pd.read_csv(file_path)
        # 替换 NaN 值为 None
        data.fillna(value={'grade': None, 'genre': None, 'cast': None, 'release_date': None, 'image_url': None}, inplace=True)
        # 将 DataFrame 转换为列表
        return data.values.tolist()
    except Exception as e:
        print('读取CSV文件时发生异常：', e)
        raise

def add_all_maoyan_data(cursor, data):
    try:
        sql = '''
        INSERT INTO maoyan_movies (title, grade, genre, cast, release_date, image_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        grade = VALUES(grade),
        genre = VALUES(genre),
        cast = VALUES(cast),
        release_date = VALUES(release_date),
        image_url = VALUES(image_url);
        '''
        cursor.executemany(sql, data)
        cursor.connection.commit()
        print(f"成功添加 {cursor.rowcount} 条数据。")
    except Exception as e:
        print('添加所有数据时发生异常：', e)
        raise

def main():
    host = 'localhost'
    user = 'root'
    password = '123456'
    port = 3306
    database = 'moviemate'
    charset = 'utf8'

    try:
        with database_connection(host, user, password, port, database, charset) as connection:
            with connection.cursor() as cursor:
                create_database(cursor, database)
                cursor.execute(f"USE {database}")

                create_maoyan_movies_table(cursor)

                file_path = r'D:\PythonProject\MovieRecommendation\test\douban_top250.csv'
                data = read_csv(file_path)

                add_all_maoyan_data(cursor, data)
                print("数据添加完成。")

    except Exception as e:
        print('在执行主函数main时发生异常：', e)
        raise
    finally:
        print("程序执行完毕")

if __name__ == '__main__':
    main()