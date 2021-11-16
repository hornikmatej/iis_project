from modules import *

def make_short_content(applications):
    for application in applications:
        if len(application['obsah']) >= 15:
            application['kratky_obsah'] = application['obsah'][0:15] + "..."
        else:
            application['kratky_obsah'] = application['obsah']
    return applications


@app.route('/my_conf/<conf_id>', methods = ['GET', 'POST'])
def my_conf(conf_id):
    msg = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM konferencia WHERE id_kon = % s"
        params = (conf_id, )
        cursor.execute(sql, params)
        conf = cursor.fetchone()
        conf['miestnosti'] = conf['miestnosti'].split(",")

        if session['login'] == conf['login']:
        
            sql = "SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s AND p.stav = %s ORDER BY cas"
            params = (conf_id, "Accepted")
            cursor.execute(sql, params)
            presentations = cursor.fetchall()

            sql = "SELECT * FROM prednaska WHERE id_konferencie = % s AND stav = %s"
            params = (conf_id, "In progress")
            cursor.execute(sql, params)
            applications = cursor.fetchall()
            applications = make_short_content(applications)

            sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
            params = (session['id_uziv'], )
            cursor.execute(sql, params)
            admin = cursor.fetchone()
            admin_bool = True if admin else False

            if request.method == 'POST' and 'id_pred' in request.form and 'rooms' in request.form and 'datetime' in request.form and 'submit' in request.form and request.form['submit'] == 'Accept':
                sql = "SELECT * FROM miestnost "
                cursor.execute(sql)
                rooms = cursor.fetchall()
                room_id = ""
                for room in rooms:
                    if room['nazov'] == str(request.form['rooms']):
                        room_id = int(room['id_miestnosti'])

                sql = "SELECT od_datum, do_datum FROM konferencia WHERE id_kon = % s"
                params = (conf_id,)
                cursor.execute(sql, params)
                conference_from_to = cursor.fetchall()

                start = conference_from_to[0]['od_datum']
                end = conference_from_to[0]['do_datum'] - timedelta(hours=1)
                date = datetime.strptime(request.form['datetime'],"%Y-%m-%dT%H:%M")

                if start <= date <= end:
                    sql = "SELECT * FROM prednaska WHERE id_miestnosti = % s AND cas = %s AND stav = %s"
                    params = (room_id, request.form['datetime'], "Accepted",)
                    cursor.execute(sql, params)
                    same_time_applicaton = cursor.fetchall()
                    if(same_time_applicaton):
                        msg = 'Another application at same time and room already exist!' 

                    else:
                        sql = "UPDATE prednaska SET id_miestnosti = % s, cas = % s, stav = % s WHERE id_pred = % s"
                        params = (room_id, request.form['datetime'], "Accepted", request.form['id_pred'],)
                        cursor.execute(sql, params)
                
                else:
                    msg = 'Application does not take place at the time of the conference!'

            elif request.method == 'POST' and 'id_pred' in request.form and 'submit' in request.form and request.form['submit'] == 'Decline':
                sql = "UPDATE prednaska SET stav = % s WHERE id_pred = % s"
                params = ("Declined", request.form['id_pred'],)
                cursor.execute(sql, params)

            sql = "SELECT * FROM prednaska WHERE id_konferencie = % s AND stav = %s"
            params = (conf_id, "In progress")
            cursor.execute(sql, params)
            applications = cursor.fetchall()

            sql = "SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s AND p.stav = %s ORDER BY cas"
            params = (conf_id, "Accepted")
            cursor.execute(sql, params)
            presentations = cursor.fetchall()

            sql = "SELECT * FROM rezervacia r JOIN uzivatel u ON r.id_uzivatela = u.id_uziv WHERE r.id_konferencie = % s AND r.stav = 'In progress'"
            params = (conf_id, )
            cursor.execute(sql, params)
            incoming_reservations = cursor.fetchall()

            if request.method == 'POST' and 'id_rez' in request.form and 'reservation_submit' in request.form and request.form['reservation_submit'] == 'Confirm':

                sql = "UPDATE rezervacia SET stav = 'Accepted' WHERE id_rez = % s"
                params = (request.form['id_rez'], )
                cursor.execute(sql, params)
                mysql.connection.commit()

                sql = "SELECT celkova_kapacita FROM konferencia WHERE id_kon = % s"
                params = (conf_id, )
                cursor.execute(sql, params)
                conf_capacity_info = cursor.fetchone()
                mysql.connection.commit()

                sql = "SELECT SUM(pocet_listkov) FROM rezervacia WHERE stav = % s AND id_konferencie = % s AND uhradene = % s"
                params = ('Accepted', conf_id, 'ano', )
                cursor.execute(sql, params)
                tickets_sum = cursor.fetchone()
                mysql.connection.commit()

                maximal_capacity = conf_capacity_info['celkova_kapacita']
                capacity_after_accept = tickets_sum['SUM(pocet_listkov)']
                
                if capacity_after_accept > maximal_capacity:
                    msg = 'Reservation cannot be accepted because the maximum capacity would be exceeded.'

                    sql = "UPDATE rezervacia SET stav = 'In progress' WHERE id_rez = % s"
                    params = (request.form['id_rez'], )
                    cursor.execute(sql, params)
                    mysql.connection.commit()

                elif capacity_after_accept == maximal_capacity:
                    msg = 'Conference is full! other reservations are Declined.'

                    sql = "UPDATE rezervacia r JOIN uzivatel u ON r.id_uzivatela = u.id_uziv SET stav = 'Declined' WHERE r.id_konferencie = % s AND r.stav = 'In progress'"
                    params = (conf_id, )
                    cursor.execute(sql, params)
                    mysql.connection.commit()

                    sql = "UPDATE konferencia SET aktualna_zaplnenost = % s, od_datum = od_datum WHERE id_kon = % s"
                    params = (capacity_after_accept, conf_id, )
                    cursor.execute(sql, params)
                    mysql.connection.commit()  
                else:
                    sql = "UPDATE konferencia SET aktualna_zaplnenost = % s, od_datum = od_datum WHERE id_kon = % s"
                    params = (capacity_after_accept, conf_id, )
                    cursor.execute(sql, params)
                    mysql.connection.commit()

            elif request.method == 'POST' and 'id_rez' in request.form and 'reservation_submit' in request.form and request.form['reservation_submit'] == 'Decline':
                sql = "UPDATE rezervacia SET stav = 'Declined' WHERE id_rez = % s"
                params = (request.form['id_rez'], )
                cursor.execute(sql, params)
                mysql.connection.commit()

            sql = "SELECT * FROM rezervacia r JOIN uzivatel u ON r.id_uzivatela = u.id_uziv WHERE r.id_konferencie = % s AND r.stav = 'In progress' AND r.uhradene = 'ano'"
            params = (conf_id, )
            cursor.execute(sql, params)
            incoming_reservations = cursor.fetchall()

            sql = "SELECT * FROM rezervacia r JOIN uzivatel u ON r.id_uzivatela = u.id_uziv WHERE r.id_konferencie = % s AND ( r.stav = 'Accepted' OR r.stav = 'Declined')"
            params = (conf_id, )
            cursor.execute(sql, params)
            decided_reservations = cursor.fetchall()

            sql = "SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s AND p.stav = %s ORDER BY cas"
            params = (conf_id, "Accepted")
            cursor.execute(sql, params)
            presentations = cursor.fetchall()

            sql = "SELECT * FROM konferencia WHERE id_kon = % s"
            params = (conf_id, )
            cursor.execute(sql, params)
            conf = cursor.fetchone()
            conf['miestnosti'] = conf['miestnosti'].split(",")

            mysql.connection.commit()
            cursor.close() 
        else:
            cursor.close()
            return render_template("my_conf.html", session = session)
        return render_template("my_conf.html", conf=conf, lecs=presentations, applications=applications, incoming_reservations=incoming_reservations, decided_reservations=decided_reservations, admin_bool = admin_bool, msg = msg, session = session)
    return redirect(url_for('login'))