from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key='something_random'

class User(db.Model):

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    posts = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

@app.route('/', methods=['POST', 'GET'])
def index():
    posts = Post.query.order_by(Post.post_id).all()
    
    return render_template('blogmain.html', posts = posts)

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) < 3:
            flash('Name must be longer than 3 characters','error')
            return redirect('/signup')
        if len(password) < 3:
            flash('Passwords must be longer than 3 characters','error')
            return redirect('/signup')
        if password != verify:
            flash('Passwords do not match','error')
            return redirect('/signup')
                
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            session['username'] = username
            return redirect('/add_post')
        else:
            flash('That name is already in use, Please choose another','error')
            return redirect('/signup')
    else:
        return render_template ('signup.html')

@app.before_request
def require_login():
    allowed_routes = ['login','signup','index','single']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/home')
def home():
    users = User.query.all()

    return render_template('home.html', users=users)

@app.route('/one_user')
def one_user():
    id= request.args['id']
    user = User.query.filter_by(user_id=id).first()
    username = user.username
    posts = Post.query.filter_by(owner_id = id).all()

    return render_template('one_user.html', posts=posts, username=username)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('Logged in as {}'.format(username))
            return redirect('/add_post')
        else:
            if user == False:
                flash('user does not exist', 'error')     
            if user.password != password:
                flash('user password incorrect', 'error')     

    return render_template ('login.html')

@app.route('/add_post', methods=['get','post'])
def addpost():
     
    return render_template('add-post.html', title='Create a new post')

@app.route('/latest', methods=['POST'])
def latest():
    title = request.form['title']
    content = request.form['content']
    owner = User.query.filter_by(username=session['username']).first()

    new_post = Post(title, content, owner)
    db.session.add(new_post)
    db.session.commit()
    
    return render_template('latest.html', title=title, content=content)

@app.route('/single')
def single():
    id= request.args['id']
    post = Post.query.filter_by(post_id = id).first()
    user_id = post.owner_id
    username = User.query.filter_by(user_id = user_id).first()
    return render_template('single.html', user_id=user_id, title=post.title, content=post.content, username=username.username)

if __name__ == '__main__':
    app.run()