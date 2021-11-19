from src.modules import *


@app.route("/user_management", methods =['GET', 'POST'])
def user_management():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin')
        admin = cursor.fetchall()
        admin = [id for id_list in admin for id in id_list.values()]
        if session['id_uziv'] in admin:
            if request.method == 'POST' and 'admin_rights_add' in request.form:
                for getid in request.form.getlist('mycheckbox'):
                    try:
                        cursor.execute("INSERT INTO admin VALUES (% s)", (getid, ))
                        mysql.connection.commit()
                    except (MySQLdb._exceptions.IntegrityError):
                        # vlozenie uz admina do tabulky
                        pass

                # if list(request.form.keys())[0] == 'button1':
                #     try:        
                #         cursor.execute('INSERT INTO admin VALUES (% s)', (request.form['button1'], ))
                #         mysql.connection.commit()
                #     except (MySQLdb._exceptions.IntegrityError):
                #         # vlozenie uz admina do tabulky
                #         pass

                # if list(request.form.keys())[0] == 'button2':
                #     cursor.execute('DELETE FROM admin WHERE id_uzivatela = (% s)', (request.form['button2'], ))
                #     mysql.connection.commit()
                # if list(request.form.keys())[0] == 'button3':
                #     #print(request.form['button3'])
                #     return redirect(url_for('um_edit', conf_id = request.form['button3']))
            elif request.method == 'POST' and 'admin_rights_remove' in request.form:
                for getid in request.form.getlist('mycheckbox'):
                    cursor.execute("DELETE FROM admin WHERE id_uzivatela = % s", (getid, ))
                    mysql.connection.commit()

            

            cursor.execute('SELECT * FROM reg_uzivatel ru JOIN uzivatel u ON u.id_uziv = ru.id_uziv')
            users = cursor.fetchall()

            cursor.execute('SELECT * FROM admin')
            admin = cursor.fetchall()
            admin = [id for id_list in admin for id in id_list.values()]
            
            users = tuple(filter(lambda x: x['login'] != session['login'], users))
            for user in users:
                if user['id_uziv'] in admin:
                    user['admin'] = "Yes"
                else:
                    user['admin'] = "No"
            admin_bool = True
            
            cursor.close()
            return render_template("user_management.html", admin_bool = admin_bool, users = users, session = session)
        else:
            return redirect(url_for('index'), session = session)
    return redirect(url_for('login'))


@app.route('/user_management/edit/<conf_id>', methods = ['GET', 'POST'])
def um_edit(conf_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin')
        admin = cursor.fetchall()
        admin = [id for id_list in admin for id in id_list.values()]
        if session['id_uziv'] in admin:
            admin_bool = True

            sql = "SELECT * FROM uzivatel WHERE id_uziv = % s"
            params = (conf_id,)
            cursor.execute(sql, params)
            account = cursor.fetchone()

            if request.method == 'POST' and 'meno' in request.form and request.form['meno'] != "":
                meno = request.form['meno']
                sql = "UPDATE uzivatel SET  meno =% s WHERE id_uziv =% s"
                params = (meno, conf_id,)
                cursor.execute(sql, params)
                mysql.connection.commit()
            if request.method == 'POST' and 'priezvisko' in request.form and request.form['priezvisko'] != "":
                priezvisko = request.form['priezvisko']
                sql = "UPDATE uzivatel SET  priezvisko =% s WHERE id_uziv =% s"
                params = (priezvisko, conf_id,)
                cursor.execute(sql, params)
                mysql.connection.commit()
                
            if request.method == 'POST' and 'email' in request.form and request.form['email'] != "":
                email = request.form['email']
                if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    # TODO osetrit normalne nie jak autik..
                    pass
                else:
                    sql = "UPDATE uzivatel SET  email =% s WHERE id_uziv =% s"
                    params = (email, conf_id,)
                    cursor.execute(sql, params)
                    mysql.connection.commit()
            if request.method == 'POST':
                return redirect(url_for('user_management'))

            cursor.close()
            return render_template("um_edit.html", admin_bool = admin_bool, account = account, conf_id=conf_id, session = session)
        else:
            cursor.close()
            return render_template("index.html", session = session)
    return redirect(url_for('login'))