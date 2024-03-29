# -*- coding: utf-8 -*-
import os
import sys
import click

from flask import Flask # 从 flask 包导入 Flask 类
from flask import request, url_for, render_template, redirect, flash
# from markupsafe import escape  # 导入 escape
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

WIN = sys.platform.startswith('win')  # 判断是否为 Windows 系统
# 根据不同系统配置sqlite路径
if WIN:
    prefix = 'sqlite:///'  # Windows 系统用三斜线
else:
    prefix = 'sqlite:////'  # 其他系统用四斜线
app = Flask(__name__)  # 实例化该类
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'  # 设置数据签名所需的密钥
db = SQLAlchemy(app)  # 初始化扩展，传入上面的程序实例 app
login_manager = LoginManager(app)  # 实例化扩展类

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受 user ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户，原本的User类要继承 Flask-Login 提供的 UserMixin 类
    return user  # 返回用户对象
login_manager.login_view = 'login'  # 将login页面设置为重定向目标
# login_manager.login_message = 'Please log in.'  # 自定义未登录的报错信息

# 借助 SQLAlchemy，可通过定义 Python 类来表示数据库里的一张表（类属性表示表中的字段/列）
# 通过对这个类进行各种操作来代替写 SQL 语句。这个类我们称之为模型类，类中的属性称之为字段
class User(db.Model,UserMixin):  # 模型类声明继承（db.Model）建立一个用户名的表，表名即类名小写
    id = db.Column(db.Integer, primary_key=True)  # primary_key=True表示ID作为主键
    name = db.Column(db.String(20), unique=True, nullable=False)  # 人名为最长20的字符串，不能重复，不能为空
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到password_hash字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)
    

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

# GET 请求用来获取资源，而 POST 则用来创建 / 更新资源；访问链接时会发送 GET 请求，提交表单会发送 POST 请求
# app.route() 里，可用 methods 关键字传递一个包含 HTTP 方法字符串的列表，表示这个视图函数处理哪种方法类型的请求
# 默认只接受 GET 请求，methods=['GET','POST']表示同时接受 GET 和 POST 请求，针对不同请求采用不同方法
@app.route('/',methods=['GET','POST'])  # 定义了methods后，index.html POST 的表单就能被视图函数正确读取
def index():
    if request.method == 'POST':  # 判断请求类型
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页，不允许未登录用户创建 item
        title = request.form.get('title')
        year = request.form.get('year')  # 将request的表单数据分别放入title和year
        if len(title) > 60 or len(year) != 4 or not title or not year:  # 判断数据是否有误
            flash('Invalid input.')  # flash() 函数用来在视图函数里向模板传递提示消息
            return redirect(url_for('index'))  # 重定向回首页
        movie = Movie(title=title, year=year)  # 数据格式无误，加入数据库
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    # request请求为默认GET时，渲染index.html
    movies = Movie.query.all()
    # 左边的 movies 是模版中使用的变量名称，将定义的虚拟数据传入index.html
    return render_template('index.html', movies=movies)

# 注意methods=[]对应列表，method=''对应单种HTTP方法
@app.route('/movie/edit/<int:movie_id>', methods=['GET','POST'])  # <int> 将传入的movie_id转为整型，合并为URL一部分
@login_required  # 添加后未登录的用户访问对应的 URL，Flask-Login 会把用户重定向到登录页面，并显示一个错误提示
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 从request中获取要编辑的movie_id，若没找到则返回404错误
    if request.method == 'POST':
        title = request.form['title']  # 从request中取出新的title和year
        year = request.form['year']
        if len(title) > 60 or len(year) != 4 or not title or not year:  # 判断新数据是否符合数据库的要求
            flash('Invalid input.')
            return redirect(url_for('edit',movie_id=movie_id))  # 数据格式有误，重定向回编辑页面
        movie.title = title
        movie.year = year  # movie从Movie中取出来后，movie的title和year变化了，commit之后数据库中对应的元素也变化了
        db.session.commit()
        flash('Item updated.')  # 提示已完成编辑
        return redirect(url_for('index'))  # 编辑完成，返回index页面
        
    return render_template('edit.html', movie=movie)  # 无论渲染

@app.route('/movie/delete/<int:movie_id>',methods=['POST'])  # # 限定只接受 POST 请求
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))

@app.route('/login',methods=['GET','POST'])  # 用户登录
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Invalid input')
            return redirect(url_for('login'))
        user = User.query.first()
        if username == user.username and user.validate_password(password):  # 验证用户名和密码
            login_user(user)  # 用户登入
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页 
        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面
    return render_template('login.html')  # HTTP 方法为 GET 时，仅渲染页面

# login——required 意思是要求必须登录了才能执行下去，
# 有些页面或 URL 不允许未登录的用户访问，比如登出页面，或页面上有些内容则需要对未登陆的用户隐藏，比如登出按钮
@app.route('/logout')  # 用户登出
@login_required  # 用于视图保护
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页

# 注册一个错误处理函数，当404错误发生时会触发
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码，正常情况下默认隐藏返回200，表示访问成功

@app.route('/settings', methods=['GET', 'POST'])  # 已登录用户修改用户名
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        current_user.name = name  # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')

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
    db.create_all()  # 创建表格结构，但不会往表格中输入数据，若目前已有表格和数据，此方法不会做任何改变
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

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')  # 接收输入的用户名
# 接收输入的密码，hide_input=True让密码隐藏输入
@click.option(
    '--password', prompt=True, hide_input=True, 
    confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    db.create_all()
    user = User.query.first()
    # 判断当前是否已有账户
    if user:
        click.echo('Updating user...')
        user.name = 'Admin'
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        # 数据库中为空时，要先实例化，才能add
        user = User()
        user.username = username
        user.name='Admin'
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')

