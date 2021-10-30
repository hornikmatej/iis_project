from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
  
  
  
app = Flask(__name__)
  
  
app.secret_key = 'your secret key'
  
  
app.config['MYSQL_HOST'] = 'sql11.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql11447453'
app.config['MYSQL_PASSWORD'] = 'e2KGxNGz6H'
app.config['MYSQL_DB'] = 'sql11447453'
  
  
mysql = MySQL(app)
  
  
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'login' in request.form and 'heslo' in request.form:
        login = request.form['login']
        heslo = request.form['heslo']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_uzivatel WHERE login = % s AND heslo = % s', (login, heslo, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id_uziv'] = account['id_uziv']
            session['login'] = account['login']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect login / password !'
    return render_template('login.html', msg = msg)
  

@app.route('/nr_all_conf', methods = ['GET', 'POST'])
def nr_all_conf():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM konferencia')
    rows = cursor.fetchall()
    return render_template("nr_all_conf.html", rows=rows)


@app.route('/nr_conf/<conf_id>') # , methods = ['GET', 'POST']
def nr_conf(conf_id, methods =['GET', 'POST']):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM konferencia WHERE id_kon = % s', (conf_id, ))
    conf = cursor.fetchone()
    return render_template("nr_conf.html", conf = conf) #, conf = conf


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))
  

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'login' in request.form and 'heslo' in request.form and 'email' in request.form and 'meno' in request.form and 'priezvisko' in request.form :
        meno = request.form['meno']
        priezvisko = request.form['priezvisko']
        login = request.form['login']
        heslo = request.form['heslo']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_uzivatel WHERE login = % s', (login, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', login):
            msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute('INSERT INTO uzivatel VALUES (NULL, % s, % s, % s)', (meno, priezvisko, email, ))
            mysql.connection.commit()
            cursor.execute('SELECT * FROM uzivatel WHERE meno = % s AND priezvisko = % s AND email = % s', (meno, priezvisko, email, ))
            uzivatel = cursor.fetchone()
            cursor.execute('INSERT INTO reg_uzivatel VALUES (% s, % s, % s)', (uzivatel['id_uziv'], login, heslo, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)
  
  
@app.route("/index")
def index():
    if 'loggedin' in session: 
        return render_template("index.html")
    return redirect(url_for('login'))
  
  
@app.route("/display")
def display():
    if 'loggedin' in session:
        cursor_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor_uzivatel.execute('SELECT * FROM uzivatel WHERE id_uziv = % s', (session['id_uziv'], ))
        account = cursor_uzivatel.fetchone()    
        cursor_reg_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor_reg_uzivatel.execute('SELECT * FROM reg_uzivatel WHERE id_uziv = % s', (session['id_uziv'], ))
        reg_uzivatel = cursor_reg_uzivatel.fetchone() 
        return render_template("display.html", account = account, reg_uzivatel = reg_uzivatel)
    return redirect(url_for('login'))


@app.route("/update", methods =['GET', 'POST'])
def update():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode' in request.form and 'organisation' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            organisation = request.form['organisation']  
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']    
            postalcode = request.form['postalcode'] 
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'name must contain only characters and numbers !'
            else:
                cursor.execute('UPDATE accounts SET  username =% s, password =% s, email =% s, organisation =% s, address =% s, city =% s, state =% s, country =% s, postalcode =% s WHERE id =% s', (username, password, email, organisation, address, city, state, country, postalcode, session['id'], ))
                mysql.connection.commit()
                msg = 'You have successfully updated !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("update.html", msg = msg)
    return redirect(url_for('login'))
  

@app.route("/my_conferences")
def my_conferences():
    if 'loggedin' in session:
        return render_template("my_conferences.html")
    return redirect(url_for('login'))


@app.route("/all_conferences")
def all_conferences():
    if 'loggedin' in session:
        return render_template("all_conferences.html")
    return redirect(url_for('login'))


@app.route('/create_conference', methods =['GET', 'POST'])
def create_conference():
    if 'loggedin' in session:  
        msg = ''
        login = session['login']
        if request.method == 'POST' and 'nazov' in request.form and 'zaner' in request.form and 'od_datum' in request.form and 'do_datum' in request.form and 'cena' in request.form and 'obsah' in request.form:
            nazov = request.form['nazov']
            zaner = request.form['zaner']
            obsah = request.form['obsah']
            od_datum = request.form['od_datum']
            do_datum = request.form['do_datum']
            cena = request.form['cena']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO konferencia VALUES (NULL, % s, % s, % s, % s, % s, % s, % s)', (nazov, zaner, obsah, od_datum, do_datum, cena, login ))
            mysql.connection.commit()
            msg = 'You have successfully created coference !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("create_conference.html", msg = msg)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host ="localhost", port = int("5000"))