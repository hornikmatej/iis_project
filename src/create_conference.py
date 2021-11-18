from src.modules import *

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

        rooms_trans = "SELECT * FROM miestnost"
        cursor.execute(rooms_trans)
        rooms = cursor.fetchall()

        if request.method == 'POST' and 'nazov' in request.form and 'zaner' in request.form and 'od_datum' in request.form and 'do_datum' in request.form and 'cena' in request.form and 'obsah' in request.form:
            nazov = request.form['nazov']
            zaner = request.form['zaner']
            obsah = request.form['obsah']
            od_datum = request.form['od_datum']
            do_datum = request.form['do_datum']
            cena = request.form['cena']
            now = (datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")
        
            if od_datum < do_datum and now < od_datum:
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
                
                sql = "INSERT INTO konferencia VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s, 0)"
                params = (nazov, zaner, obsah, od_datum, do_datum, cena, login, kapacita, miestnosti,)
                cursor.execute(sql, params)
                mysql.connection.commit()
                kapacita_msg = "Capacity of conference: "+str(kapacita)
                msg = 'You have successfully created conference !'
            else:
                msg = 'Wrong starting date, start date must be earlier than end date and conference cannot start in past'
        elif request.method == 'POST':
            print(request.form)
            msg = 'Please fill out the form !'
        cursor.close()
        return render_template("create_conference.html", msg = msg, admin_bool = admin_bool, kapacita_msg = kapacita_msg, rooms=rooms, session=session)
    return redirect(url_for('login'))