from src.modules import *


@app.route("/my_conferences")
def my_conferences():
    """Overview of conferences that belong to logged in user.
    Loads table of conferences that belong to logged in user and 
    parses them into two tables, incoming conferences and conferences
    that already ended.
    """
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Loads the data of all incoming or already running conferences
        sql = "SELECT * FROM konferencia WHERE login = % s AND do_datum > % s ORDER BY od_datum"
        params = (session['login'], (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),)
        cursor.execute(sql, params)
        confs = cursor.fetchall()

        # Loads the data of all conferences that ended
        sql = "SELECT * FROM konferencia WHERE login = % s AND do_datum <= % s ORDER BY od_datum"
        params = (session['login'], (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),)
        cursor.execute(sql, params)
        ended_confs = cursor.fetchall()

        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'],)
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        cursor.close()

        return render_template("my_conferences.html", confs=confs, ended_confs=ended_confs, admin_bool=admin_bool, session=session)
    return redirect(url_for('login'))
