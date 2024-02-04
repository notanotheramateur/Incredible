from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
socketio = SocketIO(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

@app.route('/')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user, courses=Course.query.all())
    else:
        return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return "Invalid login credentials"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/course/<int:course_id>')
def course(course_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    if not user or not course:
        return "Unauthorized", 401

    return render_template('course.html', user=user, course=course)

@socketio.on('message')
def handle_message(msg):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            emit('message', {'username': user.username, 'message': msg}, broadcast=True)

if __name__ == '__main__':
    db.create_all()
    socketio.run(app, debug=True)