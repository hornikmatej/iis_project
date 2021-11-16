from modules import *

@app.route('/')
@app.route('/login', methods = ['GET', 'POST'])
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
                return render_template('index.html', msg = msg, admin_bool = admin_bool, session = session)
            else:
                msg = 'Incorrect login / password !'
        else:
            msg = 'Incorrect login / password !'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))