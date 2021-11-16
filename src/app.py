from modules import *
from log import *
from register import *
from nr_all_conf import *
from nr_conf import *
from index import *
from user_management import *
from your_account import *
from my_conf import *
from create_conference import *
from my_conferences import *
from my_reservations import *
from all_conferences import *
from r_conf import *
from my_applications import *

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)
    session.modified = True 

if __name__ == "__main__":
    app.run(host ="localhost", port = int("4999"))