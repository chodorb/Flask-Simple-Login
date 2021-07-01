from flask import Flask,render_template,request,redirect,url_for
import bcrypt
import mysql.connector
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{}:{}@{}/movedb".format('root', '', 'localhost:3306')
app.config['SECRET_KEY'] = '123qwerty!@#'

mydb = mysql.connector.connect(
    host='localhost',
    username='root',
    password='',
    database = 'movedb'
)
cur = mydb.cursor()



db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30),unique=True)
    password = db.Column(db.String(128))
    company = db.Column(db.String(30))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/user_creation',methods=['GET','POST'])
def user_creation():
    if request.method == 'GET':
        return render_template('user_creation.html')
    else:
        login = request.form['login']
        password = request.form['password'].encode('utf-8')
        company = request.form['company']
        hash_password = bcrypt.hashpw(password,bcrypt.gensalt()).decode(encoding='utf-8')

        cur.execute(f'INSERT INTO user (id,username,password,company) VALUES (NULL,"{login}","{hash_password}","{company}")')
        mydb.commit()
    return redirect(url_for('user_creation'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        login = request.form['login']
        password = request.form['password'].encode('utf-8')
        user = User.query.filter_by(username=f"{login}").first()
        if user == None:
            return "Non-Existing User"
        else:
            if bcrypt.checkpw(password,user.password.encode('utf-8')):
                login_user(user)
                return "Success"
            else:
                return "Bad creds."

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'You are logged out'

@app.route('/')
def home():
    try:
        return "Hi "+current_user.username
    except AttributeError:
        return redirect(url_for('login'))

if __name__ == "__main__":  
    app.run(debug=True,host='0.0.0.0')