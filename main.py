from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key='something_random'

class Post(db.Model):

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    ##owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content):
        self.title = title
        self.content = content

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Post(title, content)
        db.session.add(new_post)
        db.session.commit()

    posts = Post.query.filter_by().all()

    return render_template('blogmain.html', title='Build-a-blog', posts = posts)

@app.route('/add_post', methods=['post'])
def addpost():
    return render_template('add-post.html', title='Create a new post')

if __name__ == '__main__':
    app.run()