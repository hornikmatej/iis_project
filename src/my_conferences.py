from src.modules import *

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
        
        return render_template("my_conferences.html", confs=confs, admin_bool = admin_bool, session = session)
    return redirect(url_for('login'))