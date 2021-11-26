from src.modules import *
from src.log import *
from src.register import *
from src.nr_all_conf import *
from src.nr_conf import *
from src.index import *
from src.user_management import *
from src.your_account import *
from src.my_conf import *
from src.create_conference import *
from src.my_conferences import *
from src.my_reservations import *
from src.all_conferences import *
from src.r_conf import *
from src.my_applications import *

@app.before_request
def before_request():
    """Inicializacia aplikacie, nastavenie trvanie platnej session
    """
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)
    session.modified = True 

if __name__ == "__main__":
    app.run(host ="localhost", port = int("5000"))