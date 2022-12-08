from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)


# Mysql所在的主机名
HOSTNAME = "127.0.0.1"
# Mysql监听的端口号，默认3306
PORT = 3306
# 连接Mysql的用户名， 读者用自己设置的
USERNAME = 'tangming'
# 连接Mysql的密码
PASSWORD = "130796"
# mysql上创建的数据库名称
DATABASE = "bili_flask"

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"

# 在app.config中设置好连接数据库的信息
# 然后使用SQLAlchemy(app)创建一个db对象
# SQLAlchemy会自动读取app.config中连接数据库的信息
# 创建数据库连接对象
db = SQLAlchemy(app)

# 汲及到flask上下文
# with app.app_context():
#     # 测试mysql连接信息
#     with db.engine.connect() as conn:
#         rs = conn.execute("select 1")
#         print(rs.fetchone())    # 连接成功则打印(1,)


class User(db.Model):
    # 定义表名
    __tablename__ = "user"
    # db.Integer为int类型， primary_key=True为主键，autoincrement=True为自动加1
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # db.String(100)为数据库的varchar类型，最大长度为100, nullable=False不能为空
    username = db.Column(db.String(100), nullable=False)
    # db.String(100)为数据库的varchar类型，最大长度为100, nullable=False不能为空
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    signature = db.Column(db.String(100), nullable=True)

    # 这个就是要和Article里面的author字段对应，2者一起声明才能使用
    # articles就是Article里面author的back_populates="articles"
    # author就是Article里面author字段名称，要一一对应，有点麻烦
    # articles = db.relationship("Article", back_populates="author")



class Article(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # 添加作者的外键, 这个类型得看这个外键的主键的类型是什么类型， 保持同步
    # user.id： user是User的缩写， id是User表的主键
    # 以后可以通过这个外键就知道这本书的作者是谁
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # 还有一种操作是：外键反向取，flask有3种方式声明模型
    # 第1种
    # author = db.relationship("User")    # 相当于是通过查找上面的字段author_id， 再赋值到这里，就是可以通过article.author可以拿到user数据

    # 第2种
    # 现在假如知道一个user对象，但是想要拿到所有关于这个作者的所有的文章
    # user.articles  知道user对象，取这个表的外键articles， 但是这个也需要在User模型里面定义对应的字段
    # 要和User字段articles一一对应
    # author就是User表articles字段参数back_populates="author"
    # articles就是User表的articles字段
    # author = db.relationship("User", back_populates="articles")

    # 第3种
    # backref:会自动的给User模型添加一个articles的属性，用来获取文章鲭
    author = db.relationship("User", backref="articles")


# 这样创建一条数据进入数据库
# 在底层其实对应的就是sql语句：insert user(username, password) values('唐', '11111')
# user = User(username="唐", password="111111")


# 将所有表映射到数据里面，但是一般我们不使用这个，如果某个表里面需要修改某个字段，或者增加、删除某一个字段的时候，就不行了
# with app.app_context():
#     db.create_all()


# 一般我们使用这个迁移技术， 模型修改字段，增加字段，删除字段，都可以通过这个来执行映射到数据库
migrate = Migrate(app, db)

# ORM模型映射成表的三步
# 1. flask db init：这步只需要执行一次， 第一次才需要执行, 需要进入项目根目录
# 2. flask db migrate：识别ORM模型的改变，生成迁移脚本, 改变生成一次后，必须执行flask db upgrade， 不能修改字段执行2次flask db migrate
# 3. flask db upgrade：运行迁移脚本，同步到数据库中


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# 增操作
@app.route('/user/add')
def add_user():
    # 1、创建orm对象
    user = User(username="唐", password="130796")
    # 2、将orm对象添加到db.session中， 就是与数据库的一个会话
    db.session.add(user)
    # 3、将db.session中的改变同步到数据库中
    db.session.commit()
    return '用户创建成功'


# 查询操作
@app.route('/user/query')
def query_user():
    # 1、get查找， 根据主键查找，只能查找出一条来，如果有2条就会出错，所以一般是查主键
    # query是模型继承了db.Model, 所以有这个方法可以调用
    user = User.query.get(1)
    print(f'{user.id} : {user.username}--{user.password}')
    # 2、filter_by查找， 多条， query对象，类数组， 可以循环、切片等操作，
    users = User.query.filter_by(username="唐")
    for u in users:
        print(u.username)
    return "查询用户成功！"


# 修改操作
@app.route("/user/update")
def update_user():
    # 取第一条数据，是一个get对象
    user = User.query.filter_by(username="唐").first()
    user.password = "2222"
    db.session.commit() # 直接同步到数据库，就不用像添加那样使用db.session.add(user)
    return "用户数据修改成功"


# 删除操作
@app.route("/user/delete")
def delete_user():
    # 1、先查找
    user = User.query.get(1)
    # 2、从db.session中删除
    db.session.delete(user)
    # 3、将db.session中的参数，同步到数据库中
    db.session.commit()
    return "用户数据删除成功！"


# 添加文章， 测试user外键
@app.route("/article/add")
def article_add():
    article1 = Article(title="Flask学习大纲", content="Flaskwqqq")
    article1.author = User.query.get(2)

    article2 = Article(title="Django学习大纲", content="Djangowqqq")
    article2.author = User.query.get(2)

    # 添加到session中, 如果有多条，可以这样
    db.session.add_all([article1, article2])
    # 同步session中的数据到数据库中
    db.session.commit()
    return "添加文章成功！"


# 查找文章， 通过user对象查询所有文章， 外键反向取
@app.route("/article/query")
def query_article():
    user = User.query.get(2)
    # 现在通过user对象拿所有文章
    for article in user.articles:
        print(article.title)
    return "通过user对象查询所有文章成功！ "


if __name__ == '__main__':
    app.run()
