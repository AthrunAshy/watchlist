# -*- coding: utf-8 -*-
import os
import sys
import click

from flask import Flask, url_for, render_template  # 从 flask 包导入 Flask 类
# from markupsafe import escape  # 导入 escape
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith('win')  # 判断是否为 Windows 系统
# 根据不同系统配置sqlite路径
if WIN:
    prefix = 'sqlite:///'  # Windows 系统用三斜线
else:
    prefix = 'sqlite:////'  # 其他系统用四斜线
app = Flask(__name__)  # 实例化该类
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)  # 初始化扩展，传入上面的程序实例 app


# 借助 SQLAlchemy，可通过定义 Python 类来表示数据库里的一张表（类属性表示表中的字段/列）
# 通过对这个类进行各种操作来代替写 SQL 语句。这个类我们称之为模型类，类中的属性称之为字段
class User(db.Model):  # 模型类声明继承（db.Model）建立一个用户名的表，表名即类名小写
    id = db.Column(db.Integer, primary_key=True)  # primary_key=True表示ID作为主键
    name = db.Column(db.String(20), unique=True, nullable=False)  # 人名为最长20的字符串，不能重复，不能为空


class Movie(db.Model):  # 电影标题和上映年份的表
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 上映年份


# 为hello函数绑定对应的 URL，当用户在浏览器访问这个URL的时候，就会触发这个函数，获取返回值，并显示到浏览器窗口
@app.route('/hello')  # 装饰器，用于将 URL 路由和视图函数关联起来，参数是URL规则字符串，'/'指根地址
# @app.route('/index')  # 一个视图函数可以绑定多个URL
# @app.route('/home')  # 一个视图函数可以绑定多个URL
def hello():  # 视图函数，用于处理请求
    return '<h1>Welcome to My Watchlist!</h1>'  # 视图函数内容，此处可按HTML规则，浏览器可识别后渲染

# @app.route('/user/<name>')  # 尖括号来表示动态路由，根据请求的name不同而得到不同的 URL路径
# def user_page(name):
#     return f'User: {escape(name)}'  # escape() 函数对 name 变量进行转义处理，防止用户输入中出现恶意代码

# 注册一个模板上下文处理函数，返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中
# 可以将多个模板都需要用到的参数加入此处，一起注入无需每次都写
@app.context_processor
def inject_user():
    user = User.query.first()
    return {"user":user}

@app.route('/index')
def index():
    movies = Movie.query.all()
    # 左边的 movies 是模版中使用的变量名称，将定义的虚拟数据传入index.html
    return render_template('index.html', movies=movies)

# 注册一个错误处理函数，当404错误发生时会触发
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码，正常情况下默认隐藏返回200，表示访问成功

@app.route('/test')
def test_url_for():
    print(url_for('hello'))  # 在命令行窗口查看输出的 URL
    print(url_for('user_page', name='Athrun'))
    print('test_url_for')
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面
    # 用来向指定的资源传递参数 问号 ? 开始，以键值对的形式写出，多个键值对之间使用 & 分隔
    print(url_for('test_url_for', num=2))  # 输出：/test?num=2 
    return 'Test page'

# 注册为flask命令，这样可以在命令行中通过 flask initdb 来调用这个函数
@app.cli.command()
# 定义了一个名为 --drop 的命令行选项，如果传入这个选项，则 drop 参数的值将为 True
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """初始化数据库"""
    if drop:
        db.drop_all()  # 如果使用此命令时加上了'--drop'，则drop为True，则清除数据库
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

@app.cli.command()
def forge():
    """数据输入数据库"""
    db.create_all()
    # 定义虚拟数据，可用 faker 库的 Faker 类来生成虚拟数据，这里直接输入
    name = 'Athrun'
    # movies 是一个列表，其中每个元素都是一个字典
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

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        # 逐个取出movies 列表中的字典，放入movie 变量中
        movie = Movie(title=m['title'],year=m['year'])
        # 把每个取出来的movie 添加到数据库
        db.session.add(movie)
    # user和movie一起commit
    db.session.commit()
    # 打印完成信息
    click.echo('Mission Accomplished')
