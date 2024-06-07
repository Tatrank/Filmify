# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request,jsonify, g, make_response
import sqlite3
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt 
import jwt
import datetime
# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)
app.secret_key = b'_53oi3uriq9pifpff;apl'
csrf = CSRFProtect(app) 

bcrypt = Bcrypt(app) 

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection
# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/todolater')
# ‘/’ URL is bound with hello_world() function.
def todo():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM film').fetchall()
    conn.close()
        
    return render_template('index.html', films=data)


@app.route('/', methods=['GET', 'POST'])
# ‘/’ URL is bound with hello_world() function.
def home():
    if request.method == 'POST':
        password = request.form['Password']
        username = request.form['Username']
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
        conn = get_db_connection()
        if (username and password):
            try:
                data = conn.execute('SELECT password, role FROM user WHERE username = ?', (username,))
                conn.commit()
                user = data.fetchone()
        
                if user:
                    if bcrypt.check_password_hash(user['password'], password):
                        token = jwt.encode({           'user_id': username,'role': user["role"],'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')
                        resp = make_response(jsonify(message='Login successful'))
                        resp.set_cookie('jwt', token, httponly=True, samesite='Strict')
                        return resp, 200

                    else:
                        return 'error'
                else:
                    conn.execute('INSERT INTO user (username, password) VALUES (?, ?)',
                     (username, hashedPassword))
                    conn.commit()

                    if bcrypt.check_password_hash(user['password'], password):
                        token = jwt.encode({           'user_id': username,'role': "USER",'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')
                        resp = make_response(jsonify(message='Login successful'))
                        resp.set_cookie('jwt', token, httponly=True, samesite='Strict')
                        return resp, 200

                    else:
                        return 'error'

            except Exception as e:
                return str(e)
    
    return render_template('authForm.html')

@app.route('/protected', methods=['GET'])
def protected():
    token = request.cookies.get('jwt')
    if not token:
        return jsonify(message='Token is missing'), 401
    
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify(message='This is a protected route', user_id=data['user_id'], role=data['role']), 200
    except jwt.ExpiredSignatureError:
        return jsonify(message='Token has expired'), 401
    except jwt.InvalidTokenError:
        return jsonify(message='Invalid token'), 401



@app.route('/form/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        length = request.form['length']
        release_year = request.form['rel']

        conn = get_db_connection()
        conn.execute('INSERT INTO film (title, description, release_year, length) VALUES (?, ?, ?, ?)',
                     (title, description, release_year, length))
        conn.commit()
        conn.close()
        return 'Film was added'
    return render_template('form.html')





@app.route('/films', methods=['GET'])
def add_film():
    conn = get_db_connection()
    conn.execute('INSERT INTO film (title, description, release_year, length) VALUES (?, ?, ?, ?)',
                 ('The Big Fish', "lol",1235, 120 ))
    conn.commit()
    conn.close()
    return 'New film was added'
# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True)