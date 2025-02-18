import unittest

from watchlist import app, db
from watchlist.models import User, Movie
from watchlist.commands import forge, initdb

class WatchlistTestCase(unittest.TestCase):

    def setUp(self):
        # 更改 app 参数
        app.config.update(
            TESTING=True,  # 开启测试模式，这样在出错时不会输出多余信息
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'  # 使用 SQLite 内存型数据库，不会干扰开发的数据库文件
        )

        # 创建应用上下文
        self.app_context = app.app_context()
        self.app_context.push()

        # 创建数据库和表
        db.create_all()
        # 创建测试数据，一个用户，一个电影条目
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='Test Movie Title', year='2024')
        # 使用 add_all() 方法一次添加多个模型类实例（即上面创建的user和movie），传入列表
        db.session.add_all([user, movie])  # 相当于把两句 db.session.add(user) db.session.add(movie) 合一起了
        db.session.commit()

        self.client = app.test_client()  # 创建测试客户端（即浏览器），模拟客户端请求，这样测试就不用真的进入网页去点edit delete
        self.runner = app.test_cli_runner()  # 创建测试命令运行器，用来触发自定义命令

    def tearDown(self):
        db.session.remove()  # 清除数据库会话
        db.drop_all()  # 删除数据库表

        # 移除应用上下文
        self.app_context.pop()

    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    # 测试 404 页面
    def test_404_page(self):
        response = self.client.get('/nothing')  # 调用 get() 方法就相当于浏览器向服务器发送 GET 请求，传入目标 URL
        data = response.get_data(as_text=True)  # 获取 Unicode 格式的响应主体
        self.assertIn('Page Not Found - 404', data)  # 判断 404 页面响应是否包含 Page Not Found - 404
        self.assertIn('Go Back', data)  # 判断 404 页面响应是否包含 Go Back
        self.assertEqual(response.status_code, 404)  # 判断响应状态码是否为 404

    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)

    # 测试数据库，需要登入用户
    # 辅助方法，用于登入用户
    def login(self):
        # 通过 post 方法 传入用户名和密码
        self.client.post('/login', data={
            'username':'test',
            'password':'123'
        }, follow_redirects=True)  # 将 follow_redirects 参数设为 True 可以跟随重定向，最终返回的会是重定向后的响应

    # 测试创建条目
    def test_create_item(self):
        # 用上面的login方法先登入测试账户
        self.login()

        # 测试创建条目操作
        response = self.client.post('/', data={
            'title':'New Movie',
            'year':'2024'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)  # 判断返回的数据中是否有Item created.
        self.assertIn('New Movie', data)  # 判断返回的数据中是否有New Moive.

        # 测试创建条目操作，但电影标题为空
        response = self.client.post('/', data={
            'title':'',
            'year':'2024'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)  
        self.assertIn('Invalid input.', data)  # 判断返回的数据中是否有Invalid input.能正确地报错

         # 测试创建条目操作，但电影年份为空
        response = self.client.post('/', data={
            'title':'',
            'year':'2024'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

    # 测试更新条目
    def test_update_item(self):
        # 登录测试账户
        self.login()

        # 测试更新页面
        response = self.client.get('/movie/edit/1')  # 用 GET 方法访问编辑页面
        data = response.get_data(as_text=True)
        # 查看页面数据中是否含有setUp()定义的测试数据
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie Title', data)
        self.assertIn('2024', data)

        # 测试更新条目操作
        response = self.client.post('/movie/edit/1',data={
            'title':'New Movie Edited',
            'year':'2025'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.',data)
        self.assertIn('New Movie Edited',data)

        # 测试更新条目操作，但电影标题为空
        response = self.client.post('/movie/edit/1', data={
            'title':'',
            'year':'2025'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)

        # 测试更新条目操作，但电影年份为空
        response = self.client.post('/movie/edit/1', data={
            'title':'New Movie Edited Again',
            'year':''
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertNotIn('New Movie Edited Again', data)
        self.assertIn('Invalid input.', data)

    # 测试删除条目
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        # self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie Title', data)

    # 测试登录保护
    def test_login_protect(self):
        # 未调用self.login(),即测试未登录情况下不该有的页面元素是否正确地未显示
        response = self.client.get('/')  
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('<form method="post">', data)  # 未登录的情况下不应该能够提交表单
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    # 测试登录
    def test_login(self):
        # 按照 setUp 设置的 username 和 password 看能否正常登录
        response = self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success',data)
        self.assertIn('Login success',data)
        self.assertIn('Logout',data)
        self.assertIn('Settings',data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        # 测试使用错误的密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 测试使用错误的用户名登录
        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 测试使用空的密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

        # 测试使用空的用户名登录
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

# 测试登出
    def test_logout(self):
        # 先登录测试账户
        self.login()
        # 获取登出页面的返回信息
        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye.', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('<form method="post">', data)        

    # 测试设置
    def test_settings(self):
        # 登录测试账户
        self.login()
        # 测试设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Your Name', data)

        # 测试更新设置
        response = self.client.post('/settings', data={
            'name':'New Test',
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated.', data)
        self.assertIn('New Test', data)

        # 测试更新设置，改名为空名称
        response = self.client.post('/settings', data={
            'name':'',
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated.', data)
        self.assertIn('Invalid input.', data)

    # 上述是测试各个视图函数，还需测试自定义命令，即 @app.cli.command() 装饰的部分
    # 测试 initdb 命令
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)  # invoke() 的传入参数即自定义命令名，会执行该命令
        # 判断是否与正常运行的返回输出信息一致
        self.assertIn('Initialized database.', result.output)  # 返回的命令执行结果对象的 output 属性返回命令的输出信息
    
    # 测试 forge 命令
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Mission Accomplished', result.output)
        self.assertNotEqual(Movie.query.count(), 0)  # 判断 forge 命令后数据库的 Movie 数据条数不为0

    # 测试生成管理员账户
    def test_admin_command(self):
        # 先清除测试的 User 数据库，再创建一个新表格
        db.drop_all()
        db.create_all()
        # 待测试命令需要输入参数，就用 args 关键字直接给出命令参数列表
        result = self.runner.invoke(args=['admin', '--username', 'Athrun', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'Athrun')
        self.assertTrue(User.query.first().validate_password('123'))

     # 测试更新管理员账户
    def test_admin_command_update(self):
        # 上一个测试中已经建立了一个测试的管理员账户，下面要更新这个账户
        result = self.runner.invoke(args=['admin', '--username', 'Ashy', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'Ashy')
        self.assertTrue(User.query.first().validate_password('456'))

# 当这个脚本被直接运行时（而不是被导入到其他脚本中），执行以下代码块
if __name__ == '__main__':
    # 自动查找当前文件中的测试用例（以 test_ 开头的方法）并执行
    unittest.main()