from src.modules import *

def make_short_content(applications):
    """If content is too long to show on html, this funtion will cut to 15 characters

    Arguments:
        applications -- dictionary where are stored items to show on website
    """
    try:
        if len(applications['obsah']) >= 15:
            applications['kratky_obsah'] = applications['obsah'][0:15] + "..."
        else:
            applications['kratky_obsah'] = applications['obsah']
        return applications
    except:
        for application in applications:
            if len(application['obsah']) >= 15:
                application['kratky_obsah'] = application['obsah'][0:15] + "..."
            else:
                application['kratky_obsah'] = application['obsah']
        return applications

@app.route("/my_applications", methods = ['GET', 'POST'])
def my_applications():
    """Endpoint for applications that you submitted
    If user is logged in already, he is redirected to index page
    Data are being pulled from db to show on html
    """
    if 'loggedin' in session:
        msg = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "SELECT * FROM admin WHERE id_uzivatela = % s"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        admin = cursor.fetchone()
        admin_bool = True if admin else False

        sql = "SELECT * FROM prednaska p JOIN reg_uzivatel r ON p.login = r.login JOIN konferencia k ON p.id_konferencie = k.id_kon WHERE r.id_uziv = % s AND p.stav = 'In progress'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        applications_in_progress = cursor.fetchall()
        applications_in_progress = make_short_content(applications_in_progress)

        sql = "SELECT * FROM prednaska p JOIN reg_uzivatel r ON p.login = r.login JOIN konferencia k ON p.id_konferencie = k.id_kon JOIN miestnost m ON p.id_miestnosti = m.id_miestnosti WHERE r.id_uziv = % s AND p.stav = 'Accepted'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        applications_accepted = cursor.fetchall()
        applications_accepted = make_short_content(applications_accepted)

        sql = "SELECT * FROM prednaska p JOIN reg_uzivatel r ON p.login = r.login JOIN konferencia k ON p.id_konferencie = k.id_kon WHERE r.id_uziv = % s AND p.stav = 'Declined'"
        params = (session['id_uziv'], )
        cursor.execute(sql, params)
        applications_declined = cursor.fetchall()
        applications_declined = make_short_content(applications_declined)

        cursor.close()
        
        return render_template("my_applications.html", msg=msg, applications_in_progress=applications_in_progress, applications_accepted=applications_accepted, applications_declined=applications_declined, admin_bool=admin_bool, session = session)
    return redirect(url_for('login'))