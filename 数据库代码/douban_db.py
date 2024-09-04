'''
通过mysql实现douban数据的创建及管理（增删改查）
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

# 创建douban_movies数据表
def create_douban_table(cursor):
    try:
        sql = '''
        CREATE TABLE IF NOT EXISTS douban_movies (
            title VARCHAR(255) NOT NULL,
            douban_grade FLOAT
        )
        '''
        cursor.execute(sql)
        print("数据表 douban_movies 创建或已存在。")
    except Exception as e:
        print('创建数据表时发生异常：', e)
        raise

def add_all_douban_data(cursor, data):
    try:
        sql = 'INSERT IGNORE INTO douban_movies(title, douban_grade) VALUES(%s, %s)'
        cursor.executemany(sql, data)
        cursor.connection.commit()
        print(f"成功添加 {cursor.rowcount} 条数据。")
    except Exception as e:
        print('添加所有数据时发生异常：', e)
        raise

def add_single_douban_data(cursor, title, douban_grade):
    try:
        sql = '''
        INSERT INTO douban_movies (title, douban_grade)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
        douban_grade = VALUES(douban_grade);
        '''
        cursor.execute(sql, (title, douban_grade))
        cursor.connection.commit()
        print("单个数据添加完成。")
    except Exception as e:
        print('向数据库添加单个电影评分数据时发生异常：', e)
        raise

def delete_all_douban_data(cursor):
    try:
        sql = 'TRUNCATE TABLE douban_movies'
        cursor.execute(sql)
        print("所有数据已删除。")
    except Exception as e:
        print('删除所有数据时发生异常：', e)
        raise

# 通过电影名称查找并删除单条数据
def delete_single_douban_data_by_title(cursor, title):
    result = cursor.fetchone()
    if result:
        try:
            sql = 'DELETE FROM douban_movies WHERE title = %s'
            cursor.execute(sql, (title,))
            cursor.connection.commit()
            print(f"已删除标题为 '{title}' 的数据。")
        except Exception as e:
            print('从数据库删除电影评分数据时发生异常：', e)
            raise
    else:
        print("未找到匹配的数据。")

# 通过电影名称查找并更新单条数据
def update_single_douban_data_by_title(cursor, title, new_grade):
    result = cursor.fetchone()
    if result:
        try:
            sql = 'UPDATE douban_movies SET douban_grade = %s WHERE title = %s'
            cursor.execute(sql, (new_grade, title))
            cursor.connection.commit()
            print(f"已更新标题为 '{title}' 的电影评分。")
        except Exception as e:
            print('更新数据库电影评分数据时发生异常：', e)
            raise
    else:
        print("未找到匹配的数据。")

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

# 读取csv文件
def read_csv(file_path):
    try:
        return pd.read_csv(file_path, dtype=str).values.tolist()
    except Exception as e:
        print('读取CSV文件时发生异常：', e)
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

            file_path = r'../爬取网站代码/douban_top250.csv'
            data = read_csv(file_path)

            delete_all_douban_data(cursor)
            add_all_douban_data(cursor, data)
            print("数据添加完成。")

            print("准备删除数据...")
            delete_movie_title = input('请输入要删除的电影的名称：')
            if delete_movie_title.strip():
                delete_single_douban_data_by_title(cursor, delete_movie_title)
            else:
                print("未输入有效的电影名称。")

            print("准备更新数据...")
            update_movie_title = input('请输入要更新的电影的名称：')
            if update_movie_title.strip():
                update_movie_grade = 9.9
                update_single_douban_data_by_title(cursor, update_movie_title, update_movie_grade)
            else:
                print("未输入有效的电影名称。")

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