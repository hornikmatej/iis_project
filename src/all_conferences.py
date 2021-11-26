from src.modules import *


@app.route("/all_conferences", methods=['GET', 'POST'])
def all_conferences():
    """Endpoint for all conferences in system.
    Accesible only for logged users, else redirected for login page
    """
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        sql = "SELECT * FROM konferencia WHERE do_datum > % s ORDER BY od_datum"
        params = ((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),)
        cursor.execute(sql, params)
        confs = cursor.fetchall()

        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'],)
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        cursor.close()

        return render_template("all_conferences.html", confs=confs, admin_bool=admin_bool, session=session)
    return redirect(url_for('login'))
