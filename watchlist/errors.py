from flask import render_template

from watchlist import app

# 注册一个错误处理函数，当404错误发生时会触发
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('errors/404.html'), 404  # 返回模板和状态码，正常情况下默认隐藏返回200，表示访问成功

@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html'), 400

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500