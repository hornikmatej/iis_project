from src.modules import *

@app.route('/nr_all_conf', methods = ['GET', 'POST'])
def nr_all_conf():
    if 'loggedin' in session:
        return redirect(url_for('all_conferences'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM konferencia')
    rows = cursor.fetchall()
    cursor.close()
    return render_template("nr_all_conf.html", rows=rows)