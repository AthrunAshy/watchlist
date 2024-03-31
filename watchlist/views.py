from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie


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
            flash('Invalid input.')
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