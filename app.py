import re
import MySQLdb.cursors
from flask_mysqldb import MySQL
from passlib.context import CryptContext
from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)

app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'sql11.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql11447453'
app.config['MYSQL_PASSWORD'] = 'e2KGxNGz6H'
app.config['MYSQL_DB'] = 'sql11447453'

mysql = MySQL(app)

context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=50000
)


@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'login' in request.form and 'heslo' in request.form:
        login = request.form['login']
        heslo = request.form['heslo']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM reg_uzivatel WHERE login = % s"
        params = (login,)
        cursor.execute(sql, params)
        account = cursor.fetchone()
        
        try:
            valid = context.verify(heslo, account['heslo'])
        except:
            msg = 'Incorrect login / password !'
            return render_template('login.html', msg = msg)
        if (valid == True):
            if account:
                sql = "SELECT * FROM admin WHERE id_uzivatela = % s "
                params = (account['id_uziv'],)
                cursor.execute(sql, params)
                admin = cursor.fetchone()
                admin_bool = True if admin else False
                
                cursor.close()
                session['loggedin'] = True
                session['id_uziv'] = account['id_uziv']
                session['login'] = account['login']
                msg = 'Logged in successfully !'
                return render_template('index.html', msg = msg, admin_bool = admin_bool)
            else:
                msg = 'Incorrect login / password !'
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
    sql = "SELECT * FROM konferencia WHERE id_kon = % s"
    params = (conf_id,)
    cursor.execute(sql, params)
    conf = cursor.fetchone()
    sql = "SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s"
    params = (conf_id,)
    cursor.execute(sql, params)
    lecs = cursor.fetchall()
    cursor.close()
    if request.method == 'POST' and 'email' in request.form and 'meno' in request.form and 'priezvisko' in request.form and 'pocet' in request.form :
        meno = request.form['meno']
        priezvisko = request.form['priezvisko']
        email = request.form['email']
        pocet = request.form['pocet']
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "INSERT INTO uzivatel VALUES (NULL, % s, % s, % s)"
        params = (meno, priezvisko, email,)
        cursor2.execute(sql, params)
        mysql.connection.commit()
        sql = "SELECT * FROM uzivatel WHERE meno = % s AND priezvisko = % s AND email = % s"
        params = (meno, priezvisko, email,)
        cursor2.execute(sql, params)
        uzivatel = cursor2.fetchone()
        sql = "INSERT INTO rezervacia VALUES (% s, % s, % s, % s)"
        params = (uzivatel['id_uziv'], conf_id, pocet, False,)
        cursor2.execute(sql, params)
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
        heslo = context.hash(heslo)
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * FROM reg_uzivatel WHERE login = % s"
        params = (login,)
        cursor.execute(sql, params)
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', login):
            msg = 'name must contain only characters and numbers !'
        else:
            sql = "INSERT INTO uzivatel VALUES (NULL, % s, % s, % s)"
            params = (meno, priezvisko, email,)
            cursor.execute(sql, params)
            mysql.connection.commit()
            sql = "SELECT * FROM uzivatel WHERE meno = % s AND priezvisko = % s AND email = % s"
            params = (meno, priezvisko, email,)
            cursor.execute(sql, params)
            uzivatel = cursor.fetchone()
            sql = "INSERT INTO reg_uzivatel VALUES (% s, % s, % s)"
            params = (uzivatel['id_uziv'], login, heslo,)
            cursor.execute(sql, params)
            mysql.connection.commit()
            cursor.close()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route("/index")
def index():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'],)
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        cursor.close()
        
        return render_template("index.html", admin_bool = admin_bool)
    return redirect(url_for('login'))

@app.route("/user_management")
def user_management():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s "
        params = (session['id_uziv'],)
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False
        
        cursor.close()
        
        return render_template("user_management.html", admin_bool = admin_bool)
    return redirect(url_for('login'))


@app.route("/your_account", methods =['GET', 'POST'])
def your_account():
    msg = ''
    if 'loggedin' in session:
        cursor_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM uzivatel WHERE id_uziv = % s"
        params = (session['id_uziv'],)
        cursor_uzivatel.execute(sql, params)
        account = cursor_uzivatel.fetchone()
        
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'],)
        cursor_uzivatel.execute(sql, params)
        admin = cursor_uzivatel.fetchone()
        admin_bool = True if admin else False

        cursor_reg_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * FROM reg_uzivatel WHERE id_uziv = % s"
        params = (session['id_uziv'],)
        cursor_reg_uzivatel.execute(sql, params)
        reg_uzivatel = cursor_reg_uzivatel.fetchone() 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'meno' in request.form and request.form['meno'] != "":
            meno = request.form['meno']
            sql = "UPDATE uzivatel SET  meno =% s WHERE id_uziv =% s"
            params = (meno, session['id_uziv'],)
            cursor.execute(sql, params)
            mysql.connection.commit()
            msg+= 'First name updated, '
        if request.method == 'POST' and 'priezvisko' in request.form and request.form['priezvisko'] != "":
            priezvisko = request.form['priezvisko']
            sql = "UPDATE uzivatel SET  priezvisko =% s WHERE id_uziv =% s"
            params = (priezvisko, session['id_uziv'],)
            cursor.execute(sql, params)
            mysql.connection.commit()
            msg+= 'Last name updated, '
        if request.method == 'POST' and 'heslo' in request.form and request.form['heslo'] != "":
            heslo = request.form['heslo']
            heslo = context.hash(heslo)
            sql = "UPDATE reg_uzivatel SET heslo =% s WHERE id_uziv = % s"
            params = (heslo, session['id_uziv'],)
            cursor.execute(sql, params)
            mysql.connection.commit()
            msg+= 'Password updated, '
            
        if request.method == 'POST' and 'email' in request.form and request.form['email'] != "":
            email = request.form['email']
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg+= 'Invalid email address !, '
            else:
                sql = "UPDATE uzivatel SET  email =% s WHERE id_uziv =% s"
                params = (email, session['id_uziv'],)
                cursor.execute(sql, params)
                mysql.connection.commit()
                msg+= 'Email updated, '
        if msg != "":
            cursor_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "SELECT * FROM uzivatel WHERE id_uziv = % s"
            params = (session['id_uziv'],)
            cursor_uzivatel.execute(sql, params)
            account = cursor_uzivatel.fetchone()    
            cursor_reg_uzivatel = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "SELECT * FROM reg_uzivatel WHERE id_uziv = % s"
            params = (session['id_uziv'],)
            cursor_reg_uzivatel.execute(sql, params)
            reg_uzivatel = cursor_reg_uzivatel.fetchone() 
        return render_template("your_account.html", account = account, reg_uzivatel = reg_uzivatel, msg = msg[:-2], admin_bool = admin_bool)

    return redirect(url_for('login'))


@app.route("/my_conferences")
def my_conferences():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM konferencia WHERE login = % s"
        params = (session['login'],)
        cursor.execute(sql, params)
        confs = cursor.fetchall()
        
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'],)
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        cursor.close()
        
        return render_template("my_conferences.html", confs=confs, admin_bool = admin_bool)
    return redirect(url_for('login'))


@app.route("/my_reservations", methods = ['GET', 'POST'])
def my_reservations():
    admin_bool = False
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM rezervacia r JOIN konferencia k ON k.id_kon = r.id_konferencie WHERE id_uzivatela = % s "
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        ress = cursor.fetchall()
                
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s "
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        cursor.close()
        return render_template("my_reservations.html", ress=ress, admin_bool = admin_bool)
    return redirect(url_for('login'))   


@app.route('/my_conf/<conf_id>', methods = ['GET', 'POST'])
def my_conf(conf_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM konferencia WHERE id_kon = % s"
        params = (conf_id, )
        cursor.execute(sql, params)
        conf = cursor.fetchone()
        conf['miestnosti'] = conf['miestnosti'].split(",")
        
        sql = "SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s AND p.stav = %s"
        params = (conf_id, "Accepted")
        cursor.execute(sql, params)
        presentations = cursor.fetchall()

        sql = "SELECT * FROM prednaska WHERE id_konferencie = % s AND stav = %s"
        params = (conf_id, "In progress")
        cursor.execute(sql, params)
        applications = cursor.fetchall()

        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        if request.method == 'POST' and 'rooms' in request.form and 'datetime' in request.form and 'submit' in request.form and request.form['submit'] == 'Accept':
            sql = "SELECT * FROM miestnost "
            cursor.execute(sql)
            rooms = cursor.fetchall()
            room_id = ""
            for room in rooms:
                print(room)
                if room['nazov'] == str(request.form['rooms']):
                    room_id = int(room['id_miestnosti'])

            sql = "UPDATE prednaska SET id_miestnosti = % s, cas = % s, stav = % s WHERE id_pred = % s"
            params = (room_id, request.form['datetime'], "Accepted", "4")
            print(request.form)
            cursor.execute(sql, params)
            mysql.connection.commit()
            cursor.close() 
        return render_template("my_conf.html", conf=conf, lecs=presentations, applications=applications, admin_bool = admin_bool)
    return redirect(url_for('login'))


@app.route("/all_conferences", methods = ['GET', 'POST'])
def all_conferences():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT * FROM konferencia')
        confs = cursor.fetchall()
        
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'],)
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        cursor.close()

        return render_template("all_conferences.html", confs=confs, admin_bool = admin_bool)
    return redirect(url_for('login'))


@app.route('/r_conf/<conf_id>', methods = ['GET', 'POST'])
def r_conf(conf_id):
    if 'loggedin' in session:
        msg = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM konferencia WHERE id_kon = % s"
        params = (conf_id,)
        cursor.execute(sql, params)
        conf = cursor.fetchone()
        
        sql = "SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s"
        params = (conf_id,)
        cursor.execute(sql, params)
        lecs = cursor.fetchall()
        
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'],)
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False
        
        if request.method == 'POST' and 'pocet' in request.form :
            pocet = request.form['pocet']
            uzivatel = session['id_uziv']
            sql = "SELECT * FROM rezervacia WHERE id_uzivatela = % s AND id_konferencie = % s"
            params = (uzivatel, conf_id,)
            cursor.execute(sql, params)
            ordered = cursor.fetchone()
            if (ordered):
                sql = "UPDATE rezervacia SET pocet_listkov = pocet_listkov + % s WHERE id_uzivatela = % s AND id_konferencie = % s"
                params = (pocet, uzivatel, conf_id,)
                cursor.execute(sql, params)
            else:
                sql = "INSERT INTO rezervacia VALUES (% s, % s, % s, % s)"
                params = (uzivatel, conf_id, pocet, False,)
                cursor.execute(sql, params)
            mysql.connection.commit()
            msg = 'You have successfully ordered '+str(pocet)+' ticket/s to conference !'
        elif request.method == 'POST' and 'nazov' in request.form and 'obsah' in request.form:
            nazov = request.form['nazov']
            obsah = request.form['obsah']
            sql = "INSERT INTO prednaska VALUES (NULL, % s, NULL, NULL, % s, % s, % s, 'In progress')"
            params = (conf_id, session['login'], nazov, obsah,)
            cursor.execute(sql, params)
            mysql.connection.commit()
            msg = 'You have successfully applied presentation on conference, now wait for confirmation!'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        cursor.close()

        # redirect if clicked conference is mine
        if conf['login'] == session['login']:
            return redirect(url_for('my_conf', conf_id = conf_id))
        else:
            return render_template("r_conf.html", conf = conf, lecs = lecs, msg = msg, conf_id = conf_id, admin_bool = admin_bool)
    return redirect(url_for('login'))


@app.route('/create_conference', methods = ['GET', 'POST'])
def create_conference():
    if 'loggedin' in session:  
        msg = ''
        kapacita_msg = ""
        login = session['login']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'],)
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False
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
                sql = "SELECT kapacita FROM miestnost WHERE nazov = % s"
                params = (room,)
                cursor.execute(sql, params)
                kapacita_miestnosti = cursor.fetchone()
                kapacita+= kapacita_miestnosti['kapacita']
                miestnosti+=str(room)+","
            miestnosti = miestnosti[:-1]
            
            sql = "INSERT INTO konferencia VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s)"
            params = (nazov, zaner, obsah, od_datum, do_datum, cena, login, kapacita, miestnosti,)
            cursor.execute(sql, params)
            mysql.connection.commit()
            kapacita_msg = "Capacity of conference: "+str(kapacita)
            msg = 'You have successfully created coference !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        cursor.close()
        return render_template("create_conference.html", msg = msg, admin_bool = admin_bool, kapacita_msg = kapacita_msg)
    return redirect(url_for('login'))


@app.route("/my_applications", methods = ['GET', 'POST'])
def my_applications():
    if 'loggedin' in session:
        msg = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        sql = "SELECT * FROM prednaska p JOIN reg_uzivatel r ON p.login = r.login JOIN konferencia k ON p.id_konferencie = k.id_kon WHERE r.id_uziv = % s AND p.stav = 'In progress'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        applications_in_progress = cursor.fetchall()
        
        sql = "SELECT * FROM prednaska p JOIN reg_uzivatel r ON p.login = r.login JOIN konferencia k ON p.id_konferencie = k.id_kon JOIN miestnost m ON p.id_miestnosti = m.id_miestnosti WHERE r.id_uziv = % s AND p.stav = 'Accepted'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        applications_accepted = cursor.fetchall()
        
        sql = "SELECT * FROM prednaska p JOIN reg_uzivatel r ON p.login = r.login JOIN konferencia k ON p.id_konferencie = k.id_kon WHERE r.id_uziv = % s AND p.stav = 'Declined'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        applications_declined = cursor.fetchall()

        cursor.close()
        
        return render_template("my_applications.html", msg=msg, applications_in_progress=applications_in_progress, applications_accepted=applications_accepted, applications_declined=applications_declined, admin_bool=admin_bool)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host ="localhost", port = int("5000"))