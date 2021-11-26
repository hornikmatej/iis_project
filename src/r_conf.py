from src.modules import *


def make_short_content(applications):
    if len(applications['obsah']) >= 15:
        applications['kratky_obsah'] = applications['obsah'][0:15] + "..."
    else:
        applications['kratky_obsah'] = applications['obsah']
    return applications


@app.route('/r_conf/<conf_id>', methods=['GET', 'POST'])
def r_conf(conf_id):
    """Overview of given conference for registered user which does not belong to him.
    Loads the data of conference and handle reservations and applications made by registered user.

    Arguments:
        conf_id - gives the function knowledge of which conference should be loaded
    """
    past_bool = False
    if 'loggedin' in session:
        msg = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Loads conference and its data
        sql = "SELECT * FROM konferencia WHERE id_kon = % s"
        params = (conf_id,)
        cursor.execute(sql, params)
        conf = cursor.fetchone()
        conf['miestnosti'] = conf['miestnosti'].split(",")
        conf = make_short_content(conf)

        # Loads presentations that belong to given conference
        sql = "SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s ORDER BY p.cas"
        params = (conf_id,)
        cursor.execute(sql, params)
        lecs = cursor.fetchall()

        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'],)
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        # Handle reservation input 
        if request.method == 'POST' and 'pocet' in request.form:
            pocet = request.form['pocet']
            uzivatel = session['id_uziv']
            sql = "INSERT INTO rezervacia VALUES (NULL, % s, % s, % s, % s, % s, % s)"
            params = (uzivatel, conf_id, pocet, "nie", "In progress",
                      (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
            cursor.execute(sql, params)
            mysql.connection.commit()
            msg = 'You have successfully ordered ' + \
                str(pocet)+' ticket/s to conference ! Please pay tickets the next 24 hours, otherwise reservation will be Declined. Pay in:'
        
        # Handle application input
        elif request.method == 'POST' and 'nazov' in request.form and 'obsah' in request.form:
            nazov = request.form['nazov']
            obsah = request.form['obsah']
            sql = "INSERT INTO prednaska VALUES (NULL, % s, NULL, %s, % s, % s, % s, 'In progress')"
            params = (conf_id, (datetime.now()).strftime(
                "%Y-%m-%d %H:%M:%S"), session['login'], nazov, obsah,)
            cursor.execute(sql, params)
            mysql.connection.commit()
            msg = 'You have successfully applied presentation on conference, now wait for confirmation!'
        cursor.close()

        # Redirect if clicked conference is mine
        if conf['login'] == session['login']:
            return redirect(url_for('my_conf', conf_id=conf_id))
        else:
            if ((datetime.now()) > conf['do_datum']):
                past_bool = True

            return render_template("r_conf.html", conf=conf, lecs=lecs, msg=msg, conf_id=conf_id, admin_bool=admin_bool, past_bool=past_bool, session=session)
    return redirect(url_for('login'))
