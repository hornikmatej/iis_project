from src.modules import *


@app.route('/nr_all_conf', methods=['GET', 'POST'])
def nr_all_conf():
    """Overview of all current conferences.
    Loads the table of all currrent conferences.
    """
    if 'loggedin' in session:
        return redirect(url_for('all_conferences'))

    # Loads the data of all conferences
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT * FROM konferencia WHERE do_datum > % s ORDER BY od_datum"
    params = ((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    cursor.close()
    return render_template("nr_all_conf.html", rows=rows)
