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


def compute_source_trustworthiness(movie_database, source_trustworthiness):
    """
    根据每个电影的事实可信度，更新数据源的可信度。

    参数:
    movie_database (pd.DataFrame): 电影数据库，包含电影、类型、评分、数据源和事实可信度
    source_trustworthiness (dict): 每个数据源的当前可信度

    返回值:
    source_trustworthiness (dict): 更新后的每个数据源的可信度
    """
    for source in movie_database['source'].unique():
        # 计算该数据源提供的所有事实可信度的平均值
        source_movies = movie_database[movie_database['source'] == source]
        if len(source_movies) > 0:
            avg_trustworthiness = source_movies['fact_confidence'].mean()
            source_trustworthiness[source] = avg_trustworthiness
    return source_trustworthiness

def compute_fact_confidence(movie_database, source_trustworthiness):
    """
    根据数据源的可信度，计算每部电影的事实可信度。

    参数:
    movie_database (pd.DataFrame): 电影数据库，包含电影、类型、评分和数据源
    source_trustworthiness (dict): 每个数据源的可信度

    返回值:
    movie_database (pd.DataFrame): 更新了事实可信度的电影数据库
    """
    for index, row in movie_database.iterrows():
        source = row['source']
        source_trust = source_trustworthiness.get(source, 0)
        movie_database.at[index, 'fact_confidence'] = source_trust * row['rating']

    return movie_database

def true_value_iteration_recommendation(user_history, movie_database, num_recommendations=10, max_iterations=10, epsilon=0.001):
    """
    基于迭代的真值推荐算法，根据用户浏览记录从电影数据库中推荐电影

    参数:
    user_history (pd.DataFrame): 用户的历史浏览记录，包含电影名、类型和评分
    movie_database (pd.DataFrame): 电影数据库中的所有电影信息
    num_recommendations (int): 要推荐的电影数量，默认值为10
    max_iterations (int): 最大迭代次数，默认值为10
    epsilon (float): 用于检测收敛的阈值

    返回值:
    recommended_movies (pd.DataFrame): 推荐的电影信息（包含电影名、类型、评分）的DataFrame
    """
    # 初始化数据源可信度，给每个数据源初始值0.5
    movie_database['fact_confidence'] = 0.0
    source_trustworthiness = {source: 0.5 for source in movie_database['source'].unique()}

    # 迭代更新数据源和事实的可信度
    for iteration in range(max_iterations):
        # 1. 根据当前的源可信度更新事实可信度
        movie_database = compute_fact_confidence(movie_database, source_trustworthiness)

        # 2. 根据新的事实可信度更新数据源的可信度
        new_source_trustworthiness = compute_source_trustworthiness(movie_database, source_trustworthiness)

        # 检查可信度是否收敛
        max_change = max([abs(new_source_trustworthiness[source] - source_trustworthiness[source])
                          for source in source_trustworthiness])
        source_trustworthiness = new_source_trustworthiness

        print(f"Iteration {iteration + 1}, max trust change: {max_change}")
        if max_change < epsilon:
            break

    # 按事实可信度排序，并选择前 num_recommendations 个电影
    recommended_movies = movie_database.sort_values(by='fact_confidence', ascending=False).head(num_recommendations)

    return recommended_movies[['movie_name', 'genre', 'rating', 'fact_confidence']]


#基于概率图的真值推荐算法
def true_value_probability_recommendation(user_history, movie_database, source_trustworthiness, num_recommendations=10, max_iterations=10, epsilon=0.001):
    """
    基于概率图的真值推荐算法，根据用户浏览记录从电影数据库中推荐电影

    参数:
    user_history (pd.DataFrame): 用户的历史浏览记录，包含电影名、类型和评分
    movie_database (pd.DataFrame): 电影数据库中的所有电影信息
    source_trustworthiness (dict): 数据源的初始可信度
    num_recommendations (int): 要推荐的电影数量，默认值为10
    max_iterations (int): 最大迭代次数
    epsilon (float): 用于判断收敛的阈值

    返回值:
    recommended_movies (pd.DataFrame): 推荐的电影信息（包含电影名、类型、评分）的DataFrame
    """
    # 初始化电影的事实可信度
    movie_database['fact_confidence'] = 0.0

    for iteration in range(max_iterations):
        # 根据用户的历史记录来更新电影的事实可信度
        user_genres_prob = user_history['genre'].value_counts(normalize=True).to_dict()
        mean_rating = user_history['rating'].mean()
        std_rating = user_history['rating'].std()

        # 遍历电影并更新每个电影的概率评分
        for index, row in movie_database.iterrows():
            genre = row['genre']
            if genre in user_genres_prob:
                genre_probability = user_genres_prob[genre]
                rating_probability = (1 / (std_rating * np.sqrt(2 * np.pi))) * np.exp(
                    -((row['rating'] - mean_rating) ** 2) / (2 * std_rating ** 2))
                movie_database.at[index, 'fact_confidence'] = genre_probability * rating_probability

        # 计算每个源的可信度
        new_source_trustworthiness = compute_source_trustworthiness(movie_database, source_trustworthiness)

        # 检查可信度是否收敛
        max_change = max([abs(new_source_trustworthiness[source] - source_trustworthiness[source])
                          for source in source_trustworthiness])
        if max_change < epsilon:
            break

        source_trustworthiness = new_source_trustworthiness

    # 按可信度排序推荐
    recommended_movies = movie_database.sort_values(by='fact_confidence', ascending=False).head(num_recommendations)
    return recommended_movies[['movie_name', 'genre', 'rating', 'fact_confidence']]


def true_value_collaborative_filtering_recommendation(user_history, movie_database, user_similarity_matrix, source_trustworthiness, num_recommendations=10, max_iterations=10, epsilon=0.001):
    """
    基于协同过滤的真值推荐算法，根据用户浏览记录从电影数据库中推荐电影

    参数:
    user_history (pd.DataFrame): 用户的历史浏览记录，包含电影名、类型和评分
    movie_database (pd.DataFrame): 电影数据库中的所有电影信息
    user_similarity_matrix (pd.DataFrame): 用户之间的相似度矩阵
    source_trustworthiness (dict): 数据源的初始可信度
    num_recommendations (int): 要推荐的电影数量，默认值为10
    max_iterations (int): 最大迭代次数
    epsilon (float): 用于判断收敛的阈值

    返回值:
    recommended_movies (pd.DataFrame): 推荐的电影信息（包含电影名、类型、评分）的DataFrame
    """
    current_user_id = user_history['user_id'].iloc[0]
    similar_users = user_similarity_matrix.loc[current_user_id].sort_values(ascending=False)
    movie_database['fact_confidence'] = 0.0

    for iteration in range(max_iterations):
        # 更新每个电影的事实可信度
        for index, row in movie_database.iterrows():
            movie_id = row['movie_id']
            weighted_score = 0
            similarity_sum = 0

            for similar_user_id, similarity in similar_users.iteritems():
                similar_user_ratings = user_history[user_history['user_id'] == similar_user_id]
                if movie_id in similar_user_ratings['movie_id'].values:
                    rating = similar_user_ratings[similar_user_ratings['movie_id'] == movie_id]['rating'].values[0]
                    weighted_score += similarity * rating
                    similarity_sum += similarity

            if similarity_sum > 0:
                movie_database.at[index, 'fact_confidence'] = weighted_score / similarity_sum

        # 更新源的可信度
        new_source_trustworthiness = compute_source_trustworthiness(movie_database, source_trustworthiness)
        max_change = max([abs(new_source_trustworthiness[source] - source_trustworthiness[source]) for source in source_trustworthiness])
        if max_change < epsilon:
            break

        source_trustworthiness = new_source_trustworthiness

    recommended_movies = movie_database.sort_values(by='fact_confidence', ascending=False).head(num_recommendations)
    return recommended_movies[['movie_name', 'genre', 'rating', 'fact_confidence']]


def true_value_content_based_recommendation(user_history, movie_database, source_trustworthiness, num_recommendations=10, max_iterations=10, epsilon=0.001):
    """
    基于内容的真值推荐算法，根据用户浏览记录从电影数据库中推荐电影

    参数:
    user_history (pd.DataFrame): 用户的历史浏览记录，包含电影名、类型和评分
    movie_database (pd.DataFrame): 电影数据库中的所有电影信息
    source_trustworthiness (dict): 数据源的初始可信度
    num_recommendations (int): 要推荐的电影数量，默认值为10
    max_iterations (int): 最大迭代次数
    epsilon (float): 用于判断收敛的阈值

    返回值:
    recommended_movies (pd.DataFrame): 推荐的电影信息（包含电影名、类型、评分）的DataFrame
    """
    user_genre_preferences = user_history['genre'].value_counts(normalize=True).to_dict()
    movie_database['fact_confidence'] = 0.0

    for iteration in range(max_iterations):
        # 更新电影的事实可信度
        for index, row in movie_database.iterrows():
            genre = row['genre']
            if genre in user_genre_preferences:
                movie_database.at[index, 'fact_confidence'] = user_genre_preferences[genre] * row['rating']

        # 更新源的可信度
        new_source_trustworthiness = compute_source_trustworthiness(movie_database, source_trustworthiness)
        max_change = max([abs(new_source_trustworthiness[source] - source_trustworthiness[source]) for source in source_trustworthiness])
        if max_change < epsilon:
            break

        source_trustworthiness = new_source_trustworthiness

    recommended_movies = movie_database.sort_values(by='fact_confidence', ascending=False).head(num_recommendations)
    return recommended_movies[['movie_name', 'genre', 'rating', 'fact_confidence']]


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


