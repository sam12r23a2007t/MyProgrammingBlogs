from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date, datetime
import math
import bcrypt

with open('config.json', 'r') as f:
    params = json.load(f)['params']

app = Flask(__name__)

app.secret_key = "hellgdfgdotheretfdgdf5465bfg5416dfgdfglogssecreetkeydsfsdfksdfjsdlkfsdl"

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/blogs"
db = SQLAlchemy(app)

date2 = date.today()
year1 = date2.year
year2 = year1-1
year = f"{year1}-{year2}"

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    descr = db.Column(db.String(10000), nullable=False)
    posted_on = db.Column(db.String(12), nullable=False)
    img = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)

class Users(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)

class Comments(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    descr = db.Column(db.String(10000), nullable=False)
    posted_conn = db.Column(db.String(100), nullable=False)
    posted_on = db.Column(db.String(12), nullable=False)
    posted_by = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    date2 = date.today()
    year1 = date2.year
    year2 = year1-1
    year = f"{year1}-{year2}"
    return render_template('index.html', params=params, year=year)

@app.route('/about')
def about():
    return render_template('about.html', params=params, year=year)

@app.route('/contact')
def contact():
    return render_template('contact.html', params=params, year=year)


@app.route('/posts')
def post():
    post = Posts.query.filter_by().all()
    last = math.ceil(len(post)/params['no_of_post'])
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1

    page = int(page)
    postdata = post[(page-1)*params['no_of_post']:(page-1)*params['no_of_post']+params['no_of_post']]
    if (page==1):
        prev = "#"
        nextnum = "?page="+str(page+1)
    elif (page==last):
        prev = "?page="+str(page-1)
        nextnum = "#"
    else:
        prev = "?page="+str(page-1)
        nextnum = "?page="+str(page+1)
    return render_template('post.html', params=params, year=year, postdata=postdata, prev=prev, nextnum=nextnum)

@app.route('/viewpost/<string:slug>')
def viewpost(slug):

    if ("uname2" in session):
        loggedin = "True"
    else:
        loggedin = "False"

    posts = Posts.query.filter_by(slug=slug).first()
    comment2 = Comments.query.filter_by(posted_conn=slug).all()
    return render_template('viewposttemplate.html', params=params, year=year, posts=posts, comment2=comment2, loggedin=loggedin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('uname')
        password = request.form.get('password')
        if (params['admin_user_name']==name and params['admin_user_password']==password):
            session['uname']=name
            return redirect('/dashboard')
    return render_template('dashboard.html', params=params, year=year)

@app.route('/dashboard')
def dashboard():
    if ("uname" in session and session['uname']==params['admin_user_name']):
        posts = Posts.query.filter_by().all()
        return render_template('dashboard.html', params=params, year=year, posts=posts)
    return render_template('login.html', params=params, year=year)

@app.route('/operation/<string:sno>', methods=['GET', 'POST'])
def operation(sno):
    if ("uname" in session and session['uname']==params['admin_user_name']):
        if request.method == 'POST':
            title1 = request.form.get('title')
            descr2 = request.form.get('descr')
            slug2 = request.form.get('slug')
            img4 = request.form.get('img')
            if sno=='0':
                post = Posts(title=title1, descr=descr2, img=img4, slug=slug2, posted_on=datetime.now())
                db.session.add(post)
                db.session.commit()
                return redirect('/dashboard')
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title1
                post.descr = descr2
                post.img = img4
                post.slug = slug2
                db.session.commit()
                return redirect('/dashboard')
        posts = Posts.query.filter_by(sno=sno).first()
        return render_template('operation.html', params=params, year=year, posts=posts, sno=sno)
    
@app.route("/logout")
def logout():
    if "uname" in session and session['uname']==params['admin_user_name']:
        session.pop('uname')
    return redirect('/dashboard')

@app.route('/userlogout')
def userlogout():
    if "uname2" in session:
        session.pop('uname2')
        return redirect('/')

@app.route('/delete/<string:sno>')
def delete(sno):
    if "uname" in session and session['uname']==params['admin_user_name']:
        deletepost = Posts.query.filter_by(sno=sno).first()
        db.session.delete(deletepost)
        db.session.commit()
        return redirect('/dashboard')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        name2 = request.form.get('name')
        email2 = request.form.get('email')
        phone2 = request.form.get('phone')
        rawpassword = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if (rawpassword==cpassword):
            password2 = bcrypt.hashpw(rawpassword.encode('utf-8') , bcrypt.gensalt())
            user = Users(name=name2, email=email2, password=password2, phone=phone2)
            db.session.add(user)
            db.session.commit()
            return redirect('/userlogin')
            
    return render_template('signin.html', params=params, year=year)

@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        name3 = request.form.get('uname')
        password3 = request.form.get('password')
        user = Users.query.filter_by(name=name3).first()
        if (user.name==name3):
            if bcrypt.checkpw(password3.encode('utf-8'), user.password.encode('utf-8')):
                session['uname2']=name3
                return redirect('/')
    return render_template('userlogin.html', params=params, year=year)

@app.route('/try')
def try1():
    return render_template('try.html')

@app.route('/comment', methods=['POST', 'GET'])
def comment():
    if request.method=='POST':
        comment_descr = request.form.get('descr')
        conn = request.form.get('post')
        comment = Comments(descr = comment_descr, posted_by = session['uname2'], posted_conn = conn, posted_on = datetime.now())
        db.session.add(comment)
        db.session.commit()
        return redirect('/viewpost/'+conn)

if __name__=='__main__':
    app.run(debug=True)