import mysql.connector
import numpy as np
import pandas as pd


# 连接到MySQL数据库
def connect_to_db(host, user, password, database):
    """
    连接到 MySQL 数据库

    参数:
    host (str): 数据库主机地址，例如 'localhost'
    user (str): 数据库用户名
    password (str): 数据库用户密码
    database (str): 数据库名称

    返回值:
    connection (mysql.connector.connection_cext.CMySQLConnection): 返回一个数据库连接对象，用于执行SQL查询
    """
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )


# 从用户浏览记录表中获取用户的历史浏览数据
def fetch_user_browsing_history(cursor, user_id):
    """
    获取用户的历史浏览记录

    参数:
    cursor (mysql.connector.cursor_cext.CMySQLCursor): 用于执行SQL查询的数据库游标
    user_id (int): 目标用户的ID，用于筛选该用户的浏览记录

    返回值:
    browsing_history (pd.DataFrame): 包含用户浏览的电影名、类型和评分的DataFrame
    """
    query = """
    SELECT movie_name, genre, rating 
    FROM user_browsing_history
    WHERE user_id = %s
    """
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()

    # 将数据存储在pandas DataFrame中
    browsing_history = pd.DataFrame(data, columns=['movie_name', 'genre', 'rating'])
    return browsing_history


# 从电影数据库中获取所有电影信息
def fetch_movie_database(cursor):
    """
    获取电影数据库中的所有电影信息

    参数:
    cursor (mysql.connector.cursor_cext.CMySQLCursor): 用于执行SQL查询的数据库游标

    返回值:
    movie_database (pd.DataFrame): 包含电影名、类型和评分的DataFrame
    """
    query = """
    SELECT movie_name, genre, rating 
    FROM movies
    """
    cursor.execute(query)
    data = cursor.fetchall()

    # 将数据存储在pandas DataFrame中
    movie_database = pd.DataFrame(data, columns=['movie_name', 'genre', 'rating'])
    return movie_database


# 基于迭代的真值推荐算法
def true_value_iteration_recommendation(user_history, movie_database, num_recommendations=10):
    """
    基于迭代的真值推荐算法，根据用户浏览记录从电影数据库中推荐电影

    参数:
    user_history (pd.DataFrame): 用户的历史浏览记录，包含电影名、类型和评分
    movie_database (pd.DataFrame): 电影数据库中的所有电影信息
    num_recommendations (int): 要推荐的电影数量，默认值为10

    返回值:
    recommended_movies (pd.DataFrame): 推荐的电影信息（包含电影名、类型、评分）的DataFrame
    """
    # 将用户的历史记录转换为向量
    user_genres = user_history['genre'].value_counts(normalize=True).to_dict()

    # 创建一个电影推荐得分列
    movie_database['score'] = 0.0

    # 遍历电影数据库中的电影，并根据用户偏好迭代计算推荐分数
    for index, row in movie_database.iterrows():
        genre = row['genre']
        if genre in user_genres:
            movie_database.at[index, 'score'] = user_genres[genre] * row['rating']

    # 按得分排序，并选择前num_recommendations个电影
    recommended_movies = movie_database.sort_values(by='score', ascending=False).head(num_recommendations)

    return recommended_movies[['movie_name', 'genre', 'rating']]

#基于概率图的真值推荐算法
def true_value_probability_recommendation(user_history, movie_database, num_recommendations=10):
    """
    基于概率图的真值推荐算法，根据用户浏览记录从电影数据库中推荐电影

    参数:
    user_history (pd.DataFrame): 用户的历史浏览记录，包含电影名、类型和评分
    movie_database (pd.DataFrame): 电影数据库中的所有电影信息
    num_recommendations (int): 要推荐的电影数量，默认值为10

    返回值:
    recommended_movies (pd.DataFrame): 推荐的电影信息（包含电影名、类型、评分）的DataFrame
    """
    # 将用户的历史记录转换为向量，得到每种类型出现的概率
    user_genres_prob = user_history['genre'].value_counts(normalize=True).to_dict()

    # 电影的评分分布（假设评分符合正态分布）
    mean_rating = user_history['rating'].mean()
    std_rating = user_history['rating'].std()

    # 创建一个电影推荐得分列
    movie_database['prob_score'] = 0.0

    # 遍历电影数据库中的电影，并根据用户偏好和评分概率计算推荐分数
    for index, row in movie_database.iterrows():
        genre = row['genre']
        if genre in user_genres_prob:
            # 基于用户对该类型的偏好概率
            genre_probability = user_genres_prob.get(genre, 0)

            # 假设评分符合正态分布，计算评分的概率密度
            rating = row['rating']
            rating_probability = (1 / (std_rating * np.sqrt(2 * np.pi))) * np.exp(-((rating - mean_rating) ** 2) / (2 * std_rating ** 2))

            # 计算总的推荐分数 = 类型概率 * 评分概率
            total_probability = genre_probability * rating_probability
            movie_database.at[index, 'prob_score'] = total_probability

    # 按得分排序，并选择前num_recommendations个电影
    recommended_movies = movie_database.sort_values(by='prob_score', ascending=False).head(num_recommendations)

    return recommended_movies[['movie_name', 'genre', 'rating']]

def true_value_collaborative_filtering_recommendation(user_history, movie_database, user_similarity_matrix, num_recommendations=10):
    """
    基于协同过滤的真值推荐算法，根据用户浏览记录从电影数据库中推荐电影

    参数:
    user_history (pd.DataFrame): 用户的历史浏览记录，包含电影名、类型和评分
    movie_database (pd.DataFrame): 电影数据库中的所有电影信息
    user_similarity_matrix (pd.DataFrame): 用户之间的相似度矩阵
    num_recommendations (int): 要推荐的电影数量，默认值为10

    返回值:
    recommended_movies (pd.DataFrame): 推荐的电影信息（包含电影名、类型、评分）的DataFrame
    """
    # 获取当前用户的历史记录中的用户ID
    current_user_id = user_history['user_id'].iloc[0]

    # 获取与当前用户最相似的其他用户
    similar_users = user_similarity_matrix.loc[current_user_id].sort_values(ascending=False)

    # 创建一个电影推荐得分列
    movie_database['score'] = 0.0

    # 遍历电影数据库中的电影，并根据相似用户的喜好计算推荐分数
    for index, row in movie_database.iterrows():
        genre = row['genre']
        movie_id = row['movie_id']

        # 根据与当前用户相似的用户的观影记录，计算推荐分数
        weighted_score = 0
        similarity_sum = 0

        for similar_user_id, similarity in similar_users.iteritems():
            similar_user_ratings = user_history[user_history['user_id'] == similar_user_id]

            if movie_id in similar_user_ratings['movie_id'].values:
                rating = similar_user_ratings[similar_user_ratings['movie_id'] == movie_id]['rating'].values[0]
                weighted_score += similarity * rating
                similarity_sum += similarity

        if similarity_sum > 0:
            movie_database.at[index, 'score'] = weighted_score / similarity_sum

    # 按得分排序，并选择前num_recommendations个电影
    recommended_movies = movie_database.sort_values(by='score', ascending=False).head(num_recommendations)

    return recommended_movies[['movie_name', 'genre', 'rating']]


def true_value_content_based_recommendation(user_history, movie_database, num_recommendations=10):
    """
    基于内容的真值推荐算法，根据用户浏览记录从电影数据库中推荐电影

    参数:
    user_history (pd.DataFrame): 用户的历史浏览记录，包含电影名、类型和评分
    movie_database (pd.DataFrame): 电影数据库中的所有电影信息
    num_recommendations (int): 要推荐的电影数量，默认值为10

    返回值:
    recommended_movies (pd.DataFrame): 推荐的电影信息（包含电影名、类型、评分）的DataFrame
    """
    # 将用户的历史记录转换为向量
    user_genre_preferences = user_history['genre'].value_counts(normalize=True).to_dict()

    # 创建一个电影推荐得分列
    movie_database['score'] = 0.0

    # 遍历电影数据库中的电影，并根据用户的内容偏好计算推荐分数
    for index, row in movie_database.iterrows():
        genre = row['genre']
        if genre in user_genre_preferences:
            # 使用用户对特定类型电影的偏好来加权电影的评分
            movie_database.at[index, 'score'] = user_genre_preferences[genre] * row['rating']

    # 按得分排序，并选择前num_recommendations个电影
    recommended_movies = movie_database.sort_values(by='score', ascending=False).head(num_recommendations)

    return recommended_movies[['movie_name', 'genre', 'rating']]


# 主函数：从数据库中获取数据并推荐电影
def main(user_id):
    """
    从数据库中获取用户的浏览记录和电影信息，并使用真值推荐算法推荐电影

    参数:
    user_id (int): 目标用户的ID

    输出:
    打印推荐的电影列表
    """
    # MySQL数据库连接参数
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'movie_db'
    }

    # 连接到数据库
    db_conn = connect_to_db(**db_config)
    cursor = db_conn.cursor()

    # 获取用户的浏览记录
    user_history = fetch_user_browsing_history(cursor, user_id)

    # 获取电影数据库中的所有电影信息
    movie_database = fetch_movie_database(cursor)

    # 使用真值推荐算法推荐电影
    # recommended_movies = true_value_iteration_recommendation(user_history, movie_database)

    # 打印推荐的电影
    print("推荐的电影列表:")
    print(recommended_movies)

    # 关闭数据库连接
    cursor.close()
    db_conn.close()


if __name__ == "__main__":
    # 假设要为用户ID为1的用户推荐电影
    user_id = 1
    main(user_id)
