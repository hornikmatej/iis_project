# DONE


from flask.helpers import flash
from src.modules import *


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

        cursor.execute("SELECT * FROM konferencia WHERE id_kon = % s", (conf_id, ))
        conf = cursor.fetchone()
        conf['miestnosti'] = conf['miestnosti'].split(",")

        if session['login'] == conf['login']:
            cursor.execute("SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s AND p.stav = 'Accepted' ORDER BY cas", (conf_id, ))
            presentations = cursor.fetchall()

            cursor.execute("SELECT * FROM prednaska WHERE id_konferencie = % s AND stav = 'In progress'", (conf_id, ))
            applications = cursor.fetchall()
            applications = make_short_content(applications)

            cursor.execute("SELECT * FROM admin WHERE id_uzivatela = % s", (session['id_uziv'], ))
            admin = cursor.fetchone()
            admin_bool = True if admin else False

            if request.method == 'POST' and 'id_pred' in request.form and 'rooms' in request.form and 'datetime' in request.form and 'submit' in request.form and request.form['submit'] == 'Accept':
                cursor.execute("SELECT * FROM miestnost ")
                rooms = cursor.fetchall()
                room_id = ""
                for room in rooms:
                    if room['nazov'] == str(request.form['rooms']):
                        room_id = int(room['id_miestnosti'])

                cursor.execute("SELECT od_datum, do_datum FROM konferencia WHERE id_kon = % s", (conf_id,))
                conference_from_to = cursor.fetchall()

                start = conference_from_to[0]['od_datum']
                end = conference_from_to[0]['do_datum'] - timedelta(hours=1)
                date = datetime.strptime(request.form['datetime'],"%Y-%m-%dT%H:%M")

                if start <= date <= end:
                    cursor.execute("SELECT * FROM prednaska WHERE id_miestnosti = % s AND cas = %s AND stav = 'Accepted'", (room_id, request.form['datetime'], ))
                    same_time_applicaton = cursor.fetchall()
                    if(same_time_applicaton):
                        msg = 'Another application at same time and room already exist!' 

                    else:
                        cursor.execute("UPDATE prednaska SET id_miestnosti = % s, cas = % s, stav = 'Accepted' WHERE id_pred = % s", (room_id, request.form['datetime'], request.form['id_pred'], ))
                
                else:
                    msg = 'Application does not take place at the time of the conference!'

            elif request.method == 'POST' and 'id_pred' in request.form and 'submit' in request.form and request.form['submit'] == 'Decline':
                cursor.execute("UPDATE prednaska SET stav = 'Declined' WHERE id_pred = % s", (request.form['id_pred'], ))

            cursor.execute("SELECT * FROM prednaska WHERE id_konferencie = % s AND stav = 'In progress'", (conf_id, ))
            applications = cursor.fetchall()

            cursor.execute("SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s AND p.stav = 'Accepted' ORDER BY cas", (conf_id, ))
            presentations = cursor.fetchall()

            cursor.execute("SELECT * FROM rezervacia r JOIN uzivatel u ON r.id_uzivatela = u.id_uziv WHERE r.id_konferencie = % s AND r.stav = 'In progress'", (conf_id, ))
            incoming_reservations = cursor.fetchall()

            if request.method == 'POST' and 'reservation_submit_accept' in request.form:
                potentional_sum = 0
                for getid in request.form.getlist('mycheckbox'):
                    cursor.execute("SELECT pocet_listkov FROM rezervacia WHERE id_rez = % s", (getid, ))
                    temp = cursor.fetchone()
                    potentional_sum += temp['pocet_listkov']

                cursor.execute("SELECT celkova_kapacita FROM konferencia WHERE id_kon = % s", (conf_id, ))
                conf_capacity_info = cursor.fetchone()
                mysql.connection.commit()

                cursor.execute("SELECT SUM(pocet_listkov) FROM rezervacia WHERE stav = 'Accepted' AND id_konferencie = % s AND uhradene = 'ano'", (conf_id, ))
                tickets_sum = cursor.fetchone()
                mysql.connection.commit()

                maximal_capacity = conf_capacity_info['celkova_kapacita']
                try:
                    capacity_after_accept = tickets_sum['SUM(pocet_listkov)'] + potentional_sum
                except TypeError:
                    capacity_after_accept = potentional_sum

                if (capacity_after_accept) > maximal_capacity:
                    msg = 'Reservation cannot be accepted because the maximum capacity would be exceeded.'
                    flash('Reservation cannot be accepted because the maximum capacity would be exceeded.')
                    # return redirect(url_for('my_conf', conf_id=conf_id))
                    
                else:
                    for getid in request.form.getlist('mycheckbox'):
                        cursor.execute("UPDATE rezervacia SET stav = 'Accepted' WHERE id_rez = % s", (getid, ))
                        mysql.connection.commit()

                    cursor.execute("UPDATE konferencia SET aktualna_zaplnenost = % s, od_datum = od_datum WHERE id_kon = % s", (capacity_after_accept, conf_id, ))
                    mysql.connection.commit()

                    if (capacity_after_accept) == maximal_capacity:
                        msg = 'Conference is full! other reservations are Declined.'

                        sql = "UPDATE rezervacia r JOIN uzivatel u ON r.id_uzivatela = u.id_uziv SET stav = 'Declined' WHERE r.id_konferencie = % s AND r.stav = 'In progress'"
                        params = (conf_id, )
                        cursor.execute(sql, params)
                        mysql.connection.commit()

            elif request.method == 'POST' and 'reservation_submit_decline' in request.form:
                for getid in request.form.getlist('mycheckbox'):
                    cursor.execute("UPDATE rezervacia SET stav = 'Declined' WHERE id_rez = % s", (getid, ))
                    mysql.connection.commit()

            cursor.execute("SELECT * FROM rezervacia r JOIN uzivatel u ON r.id_uzivatela = u.id_uziv WHERE r.id_konferencie = % s AND r.stav = 'In progress' AND r.uhradene = 'ano'", (conf_id, ))
            incoming_reservations = cursor.fetchall()

            cursor.execute("SELECT * FROM rezervacia r JOIN uzivatel u ON r.id_uzivatela = u.id_uziv WHERE r.id_konferencie = % s AND ( r.stav = 'Accepted' OR r.stav = 'Declined')", (conf_id, ))
            decided_reservations = cursor.fetchall()

            cursor.execute("SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s AND p.stav = %s ORDER BY cas", (conf_id, "Accepted"))
            presentations = cursor.fetchall()

            cursor.execute("SELECT * FROM konferencia WHERE id_kon = % s", (conf_id, ))
            conf = cursor.fetchone()
            conf['miestnosti'] = conf['miestnosti'].split(",")

            mysql.connection.commit()
            cursor.close() 
        else:
            cursor.close()
            return render_template("my_conf.html", session = session)
        return render_template("my_conf.html", conf=conf, lecs=presentations, applications=applications, incoming_reservations=incoming_reservations, decided_reservations=decided_reservations, admin_bool = admin_bool, msg = msg, session = session)
    return redirect(url_for('login'))
