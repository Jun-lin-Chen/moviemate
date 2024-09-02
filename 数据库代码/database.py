'''
实现功能：读取已爬取的csv数据
实现数据库管理：增删改查
'''
from idlelib.iomenu import encoding

import pymysql
import pandas as pd

#连接数据库
def database_connection(host, user, password, port, database, charset):
    connection = None
    try:
        connection = pymysql.connect(host=host, user=user, password=password, port=port, db=database, charset=charset)
        return connection
    except Exception as e:
        print('在连接数据库时发生异常：', e)
        raise  # 重新抛出异常

#将所有数据添加到数据库
def add_all_data(cursor, data):
    try:
        sql = 'INSERT IGNORE INTO douban_movies(title, douban_grade) VALUES(%s, %s)'  # 使用IGNORE避免主键值重复
        cursor.executemany(sql, data)
        cursor.connection.commit()
        print(f"成功添加 {cursor.rowcount} 条数据。")
    except Exception as e:
        print('添加所有数据时发生异常：', e)
        raise  # 重新抛出异常

#添加单条数据到数据库
def add_single_data(cursor, title, douban_grade):
    try:
        # 使用 ON DUPLICATE KEY UPDATE 来避免重复插入，并在主键冲突时更新记录
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
        raise  # 重新抛出异常

#删除数据库的表格douban_movies的所有数据
def delete_all_data(cursor):
    try:
        sql = 'TRUNCATE TABLE douban_movies'
        cursor.execute(sql)
        print("所有数据已删除。")
    except Exception as e:
        print('删除所有数据时发生异常：', e)
        raise

#通过电影名称查找并删除单条数据
def delete_single_data_by_title(cursor, title):
    try:
        sql = 'DELETE FROM douban_movies WHERE title = %s'
        cursor.execute(sql, (title,))
        cursor.connection.commit()
        print(f"已删除标题为 '{title}' 的数据。")
    except Exception as e:
        print('从数据库删除电影评分数据时发生异常：', e)
        raise  # 重新抛出异常

#通过电影名称查找并更新单条数据
def update_single_data_by_title(cursor, title, new_grade):
    try:
        result = cursor.fetchone()
        if result:
            sql = 'UPDATE douban_movies SET douban_grade = %s WHERE title = %s'
            cursor.execute(sql, (new_grade, title))
            cursor.connection.commit()
            print(f"已更新标题为 '{title}' 的电影评分。")
        else:
            print("未找到该电影。")
    except Exception as e:
        print('更新数据库电影评分数据时发生异常：', e)
        raise  # 重新抛出异常

#通过电影名称查找单条数据
def search_single_data_by_title(cursor, title):
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
        raise  # 重新抛出异常

#读取csv文件
def read_csv(file_path):
    try:
        return pd.read_csv(file_path, dtype=str).values.tolist()
    except Exception as e:
        print('读取CSV文件时发生异常：', e)
        raise

def main():
    # 运行代码的用户，根据实际情况进行修改
    host = '10.203.219.236'  #
    user = 'z305'  # 用户名
    password = '123456'  # 密码
    port = 3306  # 端口号
    database = 'MovieMate'  # 数据库名
    charset = 'utf8'

    try:
        with database_connection(host, user, password, port, database, charset) as connection:
            with connection.cursor() as cursor:

                file_path = r'D:\PythonProject\MovieRecommendation\test\douban_top250.csv'

                data = read_csv(file_path)

                delete_all_data(cursor)
                try:
                    add_all_data(cursor, data)
                    print("数据添加完成。")
                except Exception as e:
                    print(e)

                print("准备删除数据...")
                delete_movie_title = '龙猫'
                if delete_movie_title.strip():
                    delete_single_data_by_title(cursor, delete_movie_title)
                else:
                    print("未输入有效的电影名称。")

                print("准备更新数据...")
                update_movie_title = '这个杀手不太冷'
                if update_movie_title.strip():
                    update_movie_grade = 9.9
                    if update_movie_grade:
                        update_single_data_by_title(cursor, update_movie_title, update_movie_grade)
                    else:
                        print("未输入有效的评分。")
                else:
                    print("未输入有效的电影名称。")

                print("准备查询数据...")
                search_movie_title = '楚门的世界'
                if search_movie_title.strip():
                    result = search_single_data_by_title(cursor, search_movie_title)
                else:
                    print("未输入有效的电影名称。")

    except Exception as e:
        print('在执行主函数main时发生异常：', e)
        raise
    finally:
        print("程序执行完毕")

if __name__ == '__main__':
    main()