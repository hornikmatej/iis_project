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
        admin_bool = False;
        login = request.form['login']
        heslo = request.form['heslo']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_uzivatel WHERE login = % s AND heslo = % s', (login, heslo, ))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (account['id_uziv'], ))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            admin_bool = True;
        if account:
            session['loggedin'] = True
            session['id_uziv'] = account['id_uziv']
            session['login'] = account['login']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg, admin_bool = admin_bool)
        else:
            msg = 'Incorrect login / password !'
    return render_template('login.html', msg = msg)

@app.route('/nr_all_conf', methods = ['GET', 'POST'])
def nr_all_conf():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM konferencia')
    rows = cursor.fetchall()
    cursor.close()
    return render_template("nr_all_conf.html", rows=rows)


@app.route('/nr_conf/<conf_id>', methods =['GET', 'POST'])
def nr_conf(conf_id):
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM konferencia WHERE id_kon = % s', (conf_id, ))
    conf = cursor.fetchone()
    cursor.execute('SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s', (conf_id, ))
    lecs = cursor.fetchall()
    cursor.close()
    if request.method == 'POST' and 'email' in request.form and 'meno' in request.form and 'priezvisko' in request.form and 'pocet' in request.form :
        meno = request.form['meno']
        priezvisko = request.form['priezvisko']
        email = request.form['email']
        pocet = request.form['pocet']
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('INSERT INTO uzivatel VALUES (NULL, % s, % s, % s)', (meno, priezvisko, email, ))
        mysql.connection.commit()
        cursor2.execute('SELECT * FROM uzivatel WHERE meno = % s AND priezvisko = % s AND email = % s', (meno, priezvisko, email, ))
        uzivatel = cursor2.fetchone()
        cursor2.execute('INSERT INTO rezervacia VALUES (% s, % s, % s, % s)', (uzivatel['id_uziv'], conf_id, pocet, False, ))
        mysql.connection.commit()
        cursor2.close()
        msg = 'You have successfully ordered '+str(pocet)+' ticket/s to conference !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template("nr_conf.html", conf = conf, lecs = lecs, msg = msg, conf_id = conf_id)


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
            cursor.close()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route("/index")
def index():
    admin_bool = False
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (session['id_uziv'], ))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            admin_bool = True;
        return render_template("index.html", admin_bool = admin_bool)
    return redirect(url_for('login'))

@app.route("/user_management")
def user_management():
    admin_bool = False
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (session['id_uziv'], ))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            admin_bool = True;
        return render_template("user_management.html", admin_bool = admin_bool)
    return redirect(url_for('login'))


@app.route("/your_account", methods =['GET', 'POST'])
def your_account():
    msg = ''
    admin_bool = False;
    if 'loggedin' in session:
        cursor_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor_uzivatel.execute('SELECT * FROM uzivatel WHERE id_uziv = % s', (session['id_uziv'], ))
        account = cursor_uzivatel.fetchone()
        cursor_uzivatel.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (session['id_uziv'], ))
        admin = cursor_uzivatel.fetchone()
        if admin:
            admin_bool = True;    
        cursor_reg_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor_reg_uzivatel.execute('SELECT * FROM reg_uzivatel WHERE id_uziv = % s', (session['id_uziv'], ))
        reg_uzivatel = cursor_reg_uzivatel.fetchone() 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'meno' in request.form and request.form['meno'] != "":
            meno = request.form['meno']
            cursor.execute('UPDATE uzivatel SET  meno =% s WHERE id_uziv =% s', (meno, session['id_uziv'], ))
            mysql.connection.commit()
            msg+= 'First name updated, '
        if request.method == 'POST' and 'priezvisko' in request.form and request.form['priezvisko'] != "":
            priezvisko = request.form['priezvisko']
            cursor.execute('UPDATE uzivatel SET  priezvisko =% s WHERE id_uziv =% s', (priezvisko, session['id_uziv'], ))
            mysql.connection.commit()
            msg+= 'Last name updated, '
        '''
        if request.method == 'POST' and 'login' in request.form and request.form['login'] != "":
            login = request.form['login']
            cursor.execute('SELECT * FROM reg_uzivatel WHERE login = % s', (login, ))
            account = cursor.fetchone()
            if account:
                msg+= 'Username already exists !, '
            elif not re.match(r'[A-Za-z0-9]+', login):
                msg+= 'Username must contain only characters and numbers !, '
            else:
                cursor.execute('UPDATE reg_uzivatel SET login =% s WHERE id_uziv = % s', ( login, session['id_uziv'], ))
                mysql.connection.commit()
                msg+= 'Username updated, '
        '''
        if request.method == 'POST' and 'heslo' in request.form and request.form['heslo'] != "":
            heslo = request.form['heslo']
            cursor.execute('UPDATE reg_uzivatel SET heslo =% s WHERE id_uziv = % s', ( heslo, session['id_uziv'], ))
            mysql.connection.commit()
            msg+= 'Password updated, '
            
        if request.method == 'POST' and 'email' in request.form and request.form['email'] != "":
            email = request.form['email']
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg+= 'Invalid email address !, '
            else:
                cursor.execute('UPDATE uzivatel SET  email =% s WHERE id_uziv =% s', (email, session['id_uziv'], ))
                mysql.connection.commit()
                msg+= 'Email updated, '
        if msg != "":
            cursor_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor_uzivatel.execute('SELECT * FROM uzivatel WHERE id_uziv = % s', (session['id_uziv'], ))
            account = cursor_uzivatel.fetchone()    
            cursor_reg_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor_reg_uzivatel.execute('SELECT * FROM reg_uzivatel WHERE id_uziv = % s', (session['id_uziv'], ))
            reg_uzivatel = cursor_reg_uzivatel.fetchone() 
        return render_template("your_account.html", account = account, reg_uzivatel = reg_uzivatel, msg = msg[:-2], admin_bool = admin_bool)

    return redirect(url_for('login'))


@app.route("/my_conferences")
def my_conferences():
    admin_bool = False;
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM konferencia WHERE login = % s', (session['login'], ))
        confs = cursor.fetchall()
        cursor.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (session['id_uziv'], ))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            admin_bool = True; 
        return render_template("my_conferences.html", confs=confs, admin_bool = admin_bool)
    return redirect(url_for('login'))


@app.route("/my_reservations", methods = ['GET', 'POST'])
def my_reservations():
    admin_bool = False;
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM rezervacia r JOIN konferencia k ON k.id_kon = r.id_konferencie WHERE id_uzivatela = % s ', (session['id_uziv'], ))
        ress = cursor.fetchall()
        print(ress)
        cursor.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (session['id_uziv'], ))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            admin_bool = True;
        return render_template("my_reservations.html", ress=ress, admin_bool = admin_bool)
    return redirect(url_for('login'))   


@app.route('/my_conf/<conf_id>', methods =['GET', 'POST'])
def my_conf(conf_id):
    admin_bool = False;
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM konferencia WHERE id_kon = % s', (conf_id, ))
    conf = cursor.fetchone()
    cursor.execute('SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s', (conf_id, ))
    lecs = cursor.fetchall()
    cursor.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (session['id_uziv'], ))
    admin = cursor.fetchone()
    cursor.close()
    if admin:
        admin_bool = True; 
    print(lecs)
    return render_template("my_conf.html", conf = conf, lecs = lecs, admin_bool = admin_bool)


@app.route("/all_conferences", methods = ['GET', 'POST'])
def all_conferences():
    admin_bool = False;
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM konferencia')
        confs = cursor.fetchall()
        cursor.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (session['id_uziv'], ))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            admin_bool = True; 
        return render_template("all_conferences.html", confs=confs, admin_bool = admin_bool)
    return redirect(url_for('login'))


@app.route('/r_conf/<conf_id>', methods =['GET', 'POST'])
def r_conf(conf_id):
    if 'loggedin' in session:
        msg = ''
        admin_bool = False;
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM konferencia WHERE id_kon = % s', (conf_id, ))
        conf = cursor.fetchone()
        cursor.execute('SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s', (conf_id, ))
        lecs = cursor.fetchall()
        cursor.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (session['id_uziv'], ))
        admin = cursor.fetchone()
        if admin:
            admin_bool = True; 
        if request.method == 'POST' and 'pocet' in request.form :
            pocet = request.form['pocet']
            uzivatel = session['id_uziv']
            cursor.execute('INSERT INTO rezervacia VALUES (% s, % s, % s, % s)', (uzivatel, conf_id, pocet, False, ))
            mysql.connection.commit()
            msg = 'You have successfully ordered '+str(pocet)+' ticket/s to conference !'
        elif request.method == 'POST' and 'nazov' in request.form and 'obsah' in request.form:
            nazov = request.form['nazov']
            obsah = request.form['obsah']
            cursor.execute('INSERT INTO ziadost_prednaska VALUES (% s, % s, % s, % s)', (conf_id, session['login'], nazov, obsah, ))
            mysql.connection.commit()
            msg = 'You have successfully applied presentation on conference, now wait for confirmation!'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        cursor.close()
        return render_template("r_conf.html", conf = conf, lecs = lecs, msg = msg, conf_id = conf_id, admin_bool = admin_bool)
    return redirect(url_for('login'))


@app.route('/create_conference', methods =['GET', 'POST'])
def create_conference():
    if 'loggedin' in session:  
        msg = ''
        kapacita_msg = ""
        admin_bool = False;
        login = session['login']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE id_uzivatela = % s ', (session['id_uziv'], ))
        admin = cursor.fetchone()
        if admin:
            admin_bool = True; 
        if request.method == 'POST' and 'nazov' in request.form and 'zaner' in request.form and 'od_datum' in request.form and 'do_datum' in request.form and 'cena' in request.form and 'obsah' in request.form:
            nazov = request.form['nazov']
            zaner = request.form['zaner']
            obsah = request.form['obsah']
            od_datum = request.form['od_datum']
            do_datum = request.form['do_datum']
            cena = request.form['cena']

            miestnosti = ""
            kapacita = 0
            for room in request.form.getlist('rooms'):
                cursor.execute('SELECT kapacita FROM miestnost WHERE nazov = % s ', (room, ))
                kapacita_miestnosti = cursor.fetchone()
                kapacita+= kapacita_miestnosti['kapacita']
                miestnosti+=str(room)+","
            miestnosti = miestnosti[:-1]
            
            cursor.execute('INSERT INTO konferencia VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s)', (nazov, zaner, obsah, od_datum, do_datum, cena, login, kapacita, miestnosti ))
            mysql.connection.commit()
            kapacita_msg = "Capacity of conference: "+str(kapacita)
            msg = 'You have successfully created coference !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        cursor.close()
        return render_template("create_conference.html", msg = msg, admin_bool = admin_bool, kapacita_msg = kapacita_msg)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host ="localhost", port = int("5000"))