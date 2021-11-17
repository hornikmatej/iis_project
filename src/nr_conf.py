from src.modules import *

@app.route('/nr_conf/<conf_id>', methods =['GET', 'POST'])
def nr_conf(conf_id):
    if 'loggedin' in session:
        return redirect(url_for('r_conf', conf_id = conf_id))
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT * FROM konferencia WHERE id_kon = % s"
    params = (conf_id,)
    cursor.execute(sql, params)
    conf = cursor.fetchone()
    conf['miestnosti'] = conf['miestnosti'].split(",")
    
    sql = "SELECT * FROM prednaska p JOIN miestnost m ON m.id_miestnosti = p.id_miestnosti WHERE p.id_konferencie = % s AND p.stav = %s ORDER BY cas"
    params = (conf_id, "Accepted")
    cursor.execute(sql, params)
    presentations = cursor.fetchall()
    cursor.close()

    if request.method == 'POST' and 'email' in request.form and 'meno' in request.form and 'priezvisko' in request.form and 'pocet' in request.form:
        meno = request.form['meno']
        priezvisko = request.form['priezvisko']
        email = request.form['email']
        pocet = request.form['pocet']
        
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "INSERT INTO uzivatel VALUES (NULL, % s, % s, % s)"
        params = (meno, priezvisko, email,)
        cursor2.execute(sql, params)
        mysql.connection.commit()
        
        sql = "SELECT * FROM uzivatel WHERE meno = % s AND priezvisko = % s AND email = % s"
        params = (meno, priezvisko, email,)
        cursor2.execute(sql, params)
        uzivatel = cursor2.fetchone()
        
        sql = "INSERT INTO rezervacia VALUES (NULL, % s, % s, % s, % s, % s, % s)"
        params = (uzivatel['id_uziv'], conf_id, pocet, "ano", "In progress", (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
        cursor2.execute(sql, params)
        mysql.connection.commit()
        cursor2.close()
        
        msg = 'You have successfully ordered and paid '+str(pocet)+' ticket/s to conference ! Wait for the confirmation email, if your reservation is declined, money will be returned to your bank account.'
    
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    
    return render_template("nr_conf.html", conf=conf, lecs=presentations, msg=msg, conf_id=conf_id)
