from modules import *

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

        return render_template("all_conferences.html", confs=confs, admin_bool = admin_bool, session = session)
    return redirect(url_for('login'))