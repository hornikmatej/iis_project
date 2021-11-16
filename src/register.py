from modules import *

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'login' in request.form and 'heslo1' in request.form and 'heslo2' in request.form and 'email' in request.form and 'meno' in request.form and 'priezvisko' in request.form:
        meno = request.form['meno']
        priezvisko = request.form['priezvisko']
        login = request.form['login']
        heslo1 = request.form['heslo1']
        heslo2 = request.form['heslo2']
        if heslo1 == heslo2:
            heslo = context.hash(heslo1)
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
                msg = 'login must contain only characters and numbers !'
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

        else:
            msg = 'Passwords are not match!'
    
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    
    return render_template('register.html', msg = msg)