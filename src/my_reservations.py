from src.modules import *

@app.route("/my_reservations", methods = ['GET', 'POST'])
def my_reservations():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s "
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        sql = "SELECT * FROM rezervacia r JOIN konferencia k ON k.id_kon = r.id_konferencie WHERE id_uzivatela = % s AND r.stav = 'In progress'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        reservations_in_progress = cursor.fetchall()

        now = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        sql = "UPDATE rezervacia SET stav = 'Declined' WHERE cas <  % s"
        params = (now, )
        cursor.execute(sql, params)
        mysql.connection.commit()

        if request.method == 'POST' and 'id_rez' in request.form and 'pay_submit' in request.form and  request.form['pay_submit'] == 'Pay':
            sql = "UPDATE rezervacia SET uhradene = 'ano' WHERE id_rez = % s"
            params = (request.form['id_rez'], )
            cursor.execute(sql, params)
            mysql.connection.commit()


        sql = "SELECT * FROM rezervacia r JOIN konferencia k ON k.id_kon = r.id_konferencie WHERE id_uzivatela = % s AND r.stav = 'In progress'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        reservations_in_progress = cursor.fetchall()

        sql = "SELECT * FROM rezervacia r JOIN konferencia k ON k.id_kon = r.id_konferencie WHERE id_uzivatela = % s AND r.stav = 'Accepted'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        reservations_accepted = cursor.fetchall()

        if request.method == 'POST' and 'id_rez' in request.form and 'pay_submit' in request.form and request.form['pay_submit'] == 'Pay':
            sql = "UPDATE rezervacia SET uhradene = 'ano' WHERE id_rez = % s"
            params = (request.form['id_rez'], )
            cursor.execute(sql, params)
            mysql.connection.commit()

        sql = "SELECT * FROM rezervacia r JOIN konferencia k ON k.id_kon = r.id_konferencie WHERE id_uzivatela = % s AND r.stav = 'Accepted'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        reservations_accepted = cursor.fetchall()

        sql = "SELECT * FROM rezervacia r JOIN konferencia k ON k.id_kon = r.id_konferencie WHERE id_uzivatela = % s AND r.stav = 'Declined'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        reservations_declined = cursor.fetchall()
                
        #print(reservations_in_progress)

        cursor.close()
        return render_template("my_reservations.html", reservations_in_progress=reservations_in_progress, reservations_accepted=reservations_accepted, reservations_declined=reservations_declined, admin_bool = admin_bool, session = session)
    return redirect(url_for('login'))  