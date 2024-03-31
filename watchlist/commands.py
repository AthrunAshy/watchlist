import click

from watchlist import app, db
from watchlist.models import User, Movie


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
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        # 数据库中为空时，要先实例化，才能add
        user = User(username=username,name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')