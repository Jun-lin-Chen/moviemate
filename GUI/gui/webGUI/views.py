from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.shortcuts import HttpResponse  # 导入HttpResponse模块
from .models import UserInfo
import json, pymysql

def helloworld(request):  # request是必须带的实例。类似class下方法必须带self一样
    return HttpResponse("Hello World!!")  # 通过HttpResponse模块直接返回字符串到前端页面

# def index_view(request):
#     question = request.POST.get('search', '')
#     print(f'question: {question}')
#
#     return render(request, 'index.html')

def search_douban_data_by_title(cursor, title):
    try:
        sql = 'SELECT * FROM douban_movies WHERE title LIKE %s'
        # cursor.execute(sql, (title,))
        cursor.execute(sql, ('%' + title + '%',))
        result = cursor.fetchone()
        results = {
            'Name': result[6],
            'img': result[9],
            'MM Rating': result[7],
            'Category': result[2],
            'Star': result[1],
            'Date': result[4],
            'url': result[5]
        }
        return results
    except Exception as e:
        print('查询douban电影数据库时发生异常：', e)
        raise

def author_view(request):
    return render(request, 'author.html')

#登录界面
def toLogin_view(request):
    return render(request, 'login.html') #返回渲染好的login界面

#将用户输入的用户名与密码与数据库中数据进行比对
def Login_view(request):

    u = request.POST.get('user','')
    p = request.POST.get('password','')

    if u and p :
        c = UserInfo.objects.filter(user_name=u, user_password=p).count()
        if c:
            return HttpResponseRedirect('http://127.0.0.1:8000/dev/index/')
        else:
            return HttpResponse('Login failed！')
    else:
        return HttpResponse('Your user name or password should not be empty！')

#注册界面
def toRegister_view(request):
    return render(request, 'register.html') #返回渲染好的界面

#将用户注册信息存入数据库
def register_view(request):
    u = request.POST.get('user', '')
    p = request.POST.get('password', '')
    if u and p:
        if UserInfo.objects.filter(user_name=u).exists():
            return HttpResponse('This username is already taken. Please try another one.')
        else:
            stu = UserInfo(user_name=u, user_password=p)
            stu.save()
            # Pass a message to the template
            message = 'Register successfully! Redirecting to login page in 2s...'
            return render(request, 'register_success.html', {'message': message})
    else:
        return HttpResponse('Please try again！')

def index_view(request):
    question = request.POST.get('search', '')
    print(f'index-question: {question}')
    host = 'localhost'
    user = 'root'
    password = '123456'
    port = 3306
    database = 'MovieMate'
    charset = 'utf8'
    if question:
        try:
            connection = pymysql.connect(host=host, user=user, password=password, port=port, charset=charset, database=database)
            print({f'connection:{connection}'})
            if connection:
                with connection.cursor() as cursor:
                    results = search_douban_data_by_title(cursor, question)
                    print(f'index-results:{results}')
                    if results:
                        # 读取现有的JSON文件
                        with open(r'D:\PythonProject\moviemate\movie-reommendation-system\GUI\gui\webGUI\static\assets\userData\post.json','r', encoding='utf-8') as file:
                            data = json.load(file)
                        if data:
                            # 更新target字段
                            data['target'] = results
                        else:
                            return HttpResponse('data is empty')
                        # 将更新后的数据写回到JSON文件
                        with open(r'D:\PythonProject\moviemate\movie-reommendation-system\GUI\gui\webGUI\static\assets\userData\post.json','w', encoding='utf-8') as file:
                            json.dump(data, file, ensure_ascii=False, indent=4)
                        # 渲染模板
                        response = render(request, 'post.html')
                        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                        response['Pragma'] = 'no-cache'
                        response['Expires'] = '0'
                        return response
                    else:
                        return HttpResponse('No matched movies')
            else:
                return HttpResponse('Database connection failed')
        except Exception as e:
            print(e)
            return HttpResponse(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()  # 确保在最后关闭数据库连接
    else:
        return render(request, 'index.html')

def post_view(request):
    # 搜索的电影
    question = request.GET.get('search', '')
    print(f'post-question: {question}')
    response = render(request, 'post.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
