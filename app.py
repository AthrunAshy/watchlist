# -*- coding: utf-8 -*-
from flask import Flask,url_for,render_template  # 从 flask 包导入 Flask 类
from markupsafe import escape  # 导入 escape
app = Flask(__name__)  # 实例化该类


# 定义虚拟数据
name = 'Athrun'
movies = [
    {'title': 'The Shawshank Redemption', 'year': 1994},
    {'title': 'The Godfather', 'year': 1972},
    {'title': 'The Dark Knight', 'year': 2008},
    {'title': 'Schindler\'s List', 'year': 1993},
    {'title': 'Pulp Fiction', 'year': 1994},
    {'title': 'The Lord of the Rings: The Return of the King', 'year': 2003},
    {'title': 'The Good, the Bad and the Ugly', 'year': 1966},
    {'title': 'Fight Club', 'year': 1999},
    {'title': 'Forrest Gump', 'year': 1994},
    {'title': 'Inception', 'year': 2010}
]

# 为hello函数绑定对应的 URL，当用户在浏览器访问这个URL的时候，就会触发这个函数，获取返回值，并显示到浏览器窗口
@app.route('/hello')  # 装饰器，用于将 URL 路由和视图函数关联起来，参数是URL规则字符串，'/'指根地址
# @app.route('/index')
# @app.route('/home')  # 一个视图函数可以绑定多个URL
def hello():  # 视图函数，用于处理请求
    return 'Welcome to My Watchlist!'  # 视图函数内容
    # return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'  # 此处可按HTML规则

# @app.route('/user/<name>')  # 尖括号来表示动态路由，根据请求的name不同而得到不同的 URL路径
# def user_page(name):
#     return f'User: {escape(name)}'  # escape() 函数对 name 变量进行转义处理，防止用户输入中出现恶意代码

# @app.route('/test')
# def test_url_for():
#     print(url_for('hello'))  # 在命令行窗口查看输出的 URL
#     print(url_for('user_page', name='Athrun'))
#     print(url_for('user_page', name='Bob'))
#     print('test_url_for')
#     # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面
#     # 用来向指定的资源传递参数 问号?开始，以键值对的形式写出，多个键值对之间使用&分隔
#     print(url_for('test_url_for', num=2))  # 输出：/test?num=2 
#     return 'Test page'

@app.route('/index')
def index():
    # 左边的jname是模版中使用的变量名称，将定义的虚拟数据传入index
    return render_template('index.html', jname=name, jmovies=movies)
