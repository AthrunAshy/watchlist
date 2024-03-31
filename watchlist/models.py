from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import db


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