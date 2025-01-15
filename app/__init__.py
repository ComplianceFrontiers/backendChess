from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Allow requests from specific origins
    CORS(app, origins="*")

    from app.database import init_db
    init_db(app)

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.images import images_bp
    from app.routes.students import students_bp
    from app.routes.sessions import sessions_bp
    from app.routes.email import email_bp
    from app.routes.courses import courses_bp
    from app.routes.tournaments import tournaments_bp
    from app.routes.users import users_bp
    from app.routes.upcomingActivities import upcomming_bp
    from app.routes.schoolform import schoolform_bp
    from app.routes.Learn_chess import learn_bp
    from app.routes.inschool import inschool_bp
    from app.routes.app_chess import appchess_bp
    from app.routes.bulkemail import bulkemail_bp
    from app.routes.email_request import email_request_bp
    from app.routes.online_sell import online_Sell_bp
    from app.routes.forms.form_chess_club import form_chess_club_bp
    from app.routes.forms.form_Wilmington_Chess_Coaching import form_Wilmington_Chess_Coaching_bp
    from app.routes.forms.form_Bear_Middletown_Chess_Tournament import form_Bear_Middletown_Chess_Tournament_bp
    from app.routes.forms.form_Bear_Middletown_Chess_Coaching import form_Bear_Middletown_Chess_Coaching_bp
    from app.routes.forms.form_New_Jersey_Chess_Tournament import form_New_Jersey_Chess_Tournament_bp
    from app.routes.forms.form_Basics_Of_Chess import form_Basics_Of_Chess_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(images_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(tournaments_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(upcomming_bp)
    app.register_blueprint(schoolform_bp)
    app.register_blueprint(learn_bp)
    app.register_blueprint(inschool_bp)
    app.register_blueprint(appchess_bp)
    app.register_blueprint(bulkemail_bp)
    app.register_blueprint(email_request_bp)
    app.register_blueprint(online_Sell_bp)
    app.register_blueprint(form_chess_club_bp)
    app.register_blueprint(form_Wilmington_Chess_Coaching_bp)
    app.register_blueprint(form_Bear_Middletown_Chess_Tournament_bp)
    app.register_blueprint(form_Bear_Middletown_Chess_Coaching_bp)
    app.register_blueprint(form_New_Jersey_Chess_Tournament_bp)
    app.register_blueprint(form_Basics_Of_Chess_bp)
    return app
