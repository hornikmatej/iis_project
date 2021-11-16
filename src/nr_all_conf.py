from src.modules import *

@app.route('/nr_all_conf', methods = ['GET', 'POST'])
def nr_all_conf():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM konferencia')
    rows = cursor.fetchall()
    cursor.close()
    return render_template("nr_all_conf.html", rows=rows)