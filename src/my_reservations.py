from src.modules import *

@app.route("/my_reservations", methods = ['GET', 'POST'])
def my_reservations():
    """Overview of reservations that belong to logged in user.
    Loads three different tables:
    1. Reservations in progress - there are reservations that needs to be paid to be accepted
                                  or reservations that are already paid and are waiting to confirm
    2. Reservations accepted - there are reservations that are accepted
    3. Reservations declined - there are reservations that are declined, if there is reservation that
                               was already paid, money will by automaticky refunded to your bank account
    """
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s "
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        # Reservations in progress
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

        # Reservations accepted
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

        # Reservations declined
        sql = "SELECT * FROM rezervacia r JOIN konferencia k ON k.id_kon = r.id_konferencie WHERE id_uzivatela = % s AND r.stav = 'Declined'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        reservations_declined = cursor.fetchall()
                
        cursor.close()
        return render_template("my_reservations.html", reservations_in_progress=reservations_in_progress, reservations_accepted=reservations_accepted, reservations_declined=reservations_declined, admin_bool = admin_bool, session = session)
    return redirect(url_for('login'))  