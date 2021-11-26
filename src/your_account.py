from src.modules import *


@app.route("/your_account", methods=['GET', 'POST'])
def your_account():
    """ Function is called when user want to update his account information
    if user is not logged in alredy, user is redicted to login page
    according to the entered inputs, the user information in the database are updated
    when user want to change password he need to enter old password and new one must be entered twice 
    function return msg which contains information for user
    """

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

        cursor_reg_uzivatel = mysql.connection.cursor(
            MySQLdb.cursors.DictCursor)
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
            msg += 'First name updated, '
        if request.method == 'POST' and 'priezvisko' in request.form and request.form['priezvisko'] != "":
            priezvisko = request.form['priezvisko']
            sql = "UPDATE uzivatel SET  priezvisko =% s WHERE id_uziv =% s"
            params = (priezvisko, session['id_uziv'],)
            cursor.execute(sql, params)
            mysql.connection.commit()
            msg += 'Last name updated, '
        if request.method == 'POST' and 'aktualne_heslo' in request.form and request.form['aktualne_heslo'] != "" and 'heslo1' in request.form and request.form['heslo1'] != "" and 'heslo2' in request.form and request.form['heslo2'] != "":
            aktualne_heslo = request.form['aktualne_heslo']
            heslo1 = request.form['heslo1']
            heslo2 = request.form['heslo2']

            sql = "SELECT * FROM reg_uzivatel WHERE id_uziv = % s"
            params = (session['id_uziv'],)
            cursor.execute(sql, params)
            account = cursor.fetchone()

            try:
                valid = context.verify(aktualne_heslo, account['heslo'])
            except:
                msg += 'Password NOT updated WRONG actual password entered !, '

            if heslo1 == heslo2 and valid == True:
                heslo1 = context.hash(heslo1)
                sql = "UPDATE reg_uzivatel SET heslo =% s WHERE id_uziv = % s"
                params = (heslo1, session['id_uziv'],)
                cursor.execute(sql, params)
                mysql.connection.commit()
                msg += 'Password updated, '
            else:
                msg += 'Password NOT updated, you entered wrong actual or new passwords do not match, '
        elif request.method == 'POST' and (request.form['aktualne_heslo'] != "" or request.form['heslo1'] != "" or request.form['heslo2'] != ""):
            msg += 'Password NOT updated, fill required inputs, '

        if request.method == 'POST' and 'email' in request.form and request.form['email'] != "":
            email = request.form['email']
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg += 'Invalid email address !, '
            else:
                sql = "UPDATE uzivatel SET email = % s WHERE id_uziv = % s"
                params = (email, session['id_uziv'],)
                cursor.execute(sql, params)
                mysql.connection.commit()
                msg += 'Email updated, '
        if msg != "":
            cursor_uzivatel = mysql.connection.cursor(
                MySQLdb.cursors.DictCursor)
            sql = "SELECT * FROM uzivatel WHERE id_uziv = % s"
            params = (session['id_uziv'],)
            cursor_uzivatel.execute(sql, params)
            account = cursor_uzivatel.fetchone()
            cursor_reg_uzivatel = mysql.connection.cursor(
                MySQLdb.cursors.DictCursor)
            sql = "SELECT * FROM reg_uzivatel WHERE id_uziv = % s"
            params = (session['id_uziv'],)
            cursor_reg_uzivatel.execute(sql, params)
            reg_uzivatel = cursor_reg_uzivatel.fetchone()
        return render_template("your_account.html", account=account, reg_uzivatel=reg_uzivatel, msg=msg[:-2], admin_bool=admin_bool)

    return redirect(url_for('login'))
