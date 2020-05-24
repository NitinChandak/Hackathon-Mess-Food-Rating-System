import os,json
from datetime import datetime , timedelta
from flask import Flask, session, redirect, render_template, request, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, redirect, render_template, url_for , session, request, flash
import psycopg2
from flask_debug import Debug
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
app.secret_key='mess'

engine = create_engine(os.getenv("DATABASE_URL"))
db1 = scoped_session(sessionmaker(bind=engine))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(400), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    messname = db.Column(db.String(400), nullable = False)
    rating = db.Column(db.Float(), nullable = False)
    num_of_rating = db.Column(db.Integer(), nullable = False)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=["POST", "GET"])
def login():
    # ----------------------------------------------------
    if 'email' in session:
    # ----------------------------------------------------    
        flash('Already Signed in')
        return redirect(url_for('index'))
    else:
        return render_template('signin.html')


@app.route('/signin_validation', methods=["POST", "GET"])
def signin_validation():
    if request.method == 'POST':
        # get user info from input
        email = request.form['email']
        password = request.form['Password']

        # check if password match with database
        check_user = db1.execute("select * from public.users where email = :email", {'email' : email}).fetchone()

        if check_user: 
            list = []
            for i in check_user:
               list.append(i)

            check_email = list[0]
            check_pass = list[1]
            if check_email == email and check_pass == password:
                session.permanent = True
                session['password'] = check_pass
                session['email'] = check_email
                flash('Signin successful')
                return redirect(url_for('index'))
            else:
                flash('User name or password is incorrect')
                return redirect(url_for('login'))
        else:
            flash('You are not signed-up in this website. Please register first.')
            return redirect(url_for('login'))
    else:
        flash('Signin failed')
        return redirect(url_for('login'))
 

@app.route('/home', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_messname = request.form['messname']
        task_rating = request.form['rating']
        task_num_of_rating = 1
        new_task = Todo(content=task_content, messname=task_messname, rating=task_rating, num_of_rating=task_num_of_rating)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/home')
        except:
            return 'There was an issue'
    else :
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks = tasks)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == "POST":
        # task.content = request.form['content']
        # task.messname = request.form['messname']
        val = float(request.form['rating'])
        # task.rating = task.rating + float(val)
        task.num_of_rating = task.num_of_rating + 1
        task.rating = (task.rating * (task.num_of_rating - 1) + val)/task.num_of_rating
        task.rating = '%.1f'%task.rating
        try:
            db.session.commit()
            return redirect('/home')
        except:
            return "ISSUE"

    else :
         return render_template('update.html', task=task)

# @app.route('/search/<int:id>', methods=['GET','POST'])
# def search():
# SEARCH FUCTION HERE
# def login():

#     session.clear()

#     email = request.form.get("email")
#     if request.method == "POST":

#         if not request.form.get("email"):
#             return render_template("404.html", message="must provide email")

#         elif not request.form.get("password"):
#             return render_template("404.html", message="must provide password")

#         rows = db.execute("SELECT * FROM users WHERE email = :email",
#                             {"email": email})
        
#         result = rows.fetchone()

#         if result == None or not check_password_hash(result[2], request.form.get("password")):
#             return render_template("404.html", message="invalid email and/or password")

#         # Remember which user has logged in
#         session["user_id"] = result[0]
#         session["user_name"] = result[1]

#         # Redirect user to home page
#         return redirect("/home")

#     else:
#         return render_template("login.html")

# @app.route("/logout")
# def logout():

#     session.clear()

#     return redirect("/home")

@app.route('/signout')
def signout():
    if 'email' in session:
        session.pop('email', None)
        session.pop('password', None)

        flash('Signed out successfully', 'info')
        return redirect(url_for('login'))
    else:
        flash('Already Singed out')
        return  redirect(url_for('login'))


@app.route("/register", methods=["GET", "POST"])
def register():
    
    session.clear()
    
    if request.method == "POST":

        userCheck = db1.execute("SELECT * FROM users WHERE email = :email",
                          {"email":request.form.get("email")}).fetchone()

        if userCheck:
            flash("here2")
            print("$2")
            return render_template("/", message="Registration successful")

        elif not request.form.get("Password"):
            flash("here3")
            print("$3")
            
            # return render_template("404.html", message="must provide password")

        
        
        # Hash user's password to store in DB
        # hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        
        # Insert register into DB
        email = request.form['email']
        password = request.form['Password']
        db1.execute("INSERT INTO users (email, password) VALUES (:email, :password)",
                            {"email":email, 
                             "password":password})

        db1.commit()

        flash('Account created', 'info')

        # Redirect user to login page
        return redirect("/")

    else:
        return render_template("signin.html")
if __name__ == "__main__":
    app.run(debug=True)
