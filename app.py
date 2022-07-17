
from flask import Flask, redirect, render_template, request, session, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# blog tabel
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(70),nullable=False)
    data = db.Column(db.String(1500),nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    def __repr__(self):
        return '<Data %r>' % self.title

# tabel for login and signup
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    def __repr__(self):
        return '<Data %r>' % self.data + 'password %r' % self.password


@app.route('/',methods=['POST','GET'])
def home():
    if 'username' in session:
        if request.method == 'POST':
            username = session['username']
            title = request.form['title']
            data = request.form['data']
            data = Blog(username=username, title=title, data = data)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('read'))
        else:    
            return render_template('home.html',sessionn='username')
        
    return redirect(url_for('login'))


@app.route('/sign-up',methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        username = session['username']
        password = session['password']
        user = Data.query.filter_by(username=username).first()
        if user:
            flash('username already exist', category='error')
            return redirect(url_for('signup'))
        else:
            new_Data = Data(username=username,password=generate_password_hash(password) )
            db.session.add(new_Data)
            db.session.commit()
            flash('Account created',category='success')
            return redirect(url_for('read'))
    return render_template('login.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        password = request.form['password']
        username = session['username']
        user = Data.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                
                return redirect(url_for('read'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist, please signup.', category='error')
    return render_template('login1.html')
       

@app.route('/mywrite')
def mywrite():
    if 'username' in session:
        username = session['username']
        data =  Blog.query.filter_by(username=username).order_by(Blog.created_at.desc()).all()
        return render_template('mywriting.html',data=data,sessionn='username')
    return redirect('/login')


@app.route('/readmore/<int:id>',methods=['GET', 'POST'])
def readmore(id):
    data = Blog.query.filter_by(id=id).all()
    return render_template('read.html',data=data,sessionn='username')

@app.route('/read',methods=['GET', 'POST'])
def read():
    if 'username' in session:
        data = Blog.query.order_by(Blog.created_at.desc()).all()
        return render_template('blog.html',data=data,sessionn='username')
    return redirect('/login')

@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username",None)
        return redirect(url_for("login"))
    
    return redirect(url_for('login'))
       
@app.route('/delete/<int:id>')
def delete(id):
    blog = Blog.query.get_or_404(id)
    try:
        db.session.delete(blog)
        db.session.commit()
        return redirect('/mywrite')
    except:
        return "There was a problem deleting data."

if __name__ == "__main__":
    app.run(debug=True)
