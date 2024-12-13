import logging
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from app.config import DevConfig
from app.logger import SQLAlchemyHandler
from .extension import db, migrate,ma,bcrypt,scheduler
from .route.main import main_bp
from .route.auth import auth_bp
from .route.cadre import cadre_bp
from .route.department import department_bp
from .route.designation import designation_bp
from .route.diagnosis import diagnosis_bp
from .route.public import public_bp
from .route.adminSuperAdmin import adminSuperAdmin_bp
from .route.user import user_bp
from .route.plan import plan_bp
from .route.eye import eye_bp
from .route.priority import priority_bp
from .route.anesthesia import anesthesia_bp
from .route.eua import eua_bp
from .route.short import short_bp
from .route.account import account_bp
from .route.patientEntry import patiententry_bp
from .route.patientdemographic import patientdemographic_bp
from app.extra import job_listener
from apscheduler.events import EVENT_JOB_EXECUTED
from app.db_initializer import seed_db_command, empty_db_command


def create_app():
    app = Flask(__name__, static_folder='build/web')
    app.config.from_object(DevConfig)
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    bcrypt.init_app(app)
    scheduler.init_app(app)
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED)
    CORS(app)
    scheduler.start()

    app.cli.add_command(seed_db_command)
    app.cli.add_command(empty_db_command)


    # Configure SQLAlchemy logging handler
    sql_handler = SQLAlchemyHandler()
    sql_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    )
    sql_handler.setFormatter(formatter)
    app.logger.addHandler(sql_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Flask app startup")



    @app.errorhandler(404)
    def page_not_found(e):
        # Get the URL that caused the error
        url = request.url
        method = request.method
        app.logger.info(f"main app route : {url} {method}")
        return jsonify({"message":f"Url not found : {url} {method}"}),404
        
    @app.route('/<path:path>')
    def servedefault_static(path):
        app.logger.info(f"main app route : {path}")
        return send_from_directory(app.static_folder, path)

    # Register blueprints
    app.register_blueprint(main_bp, url_prefix="/waitinglist")
    app.register_blueprint(auth_bp, url_prefix="/waitinglist/auth")
    app.register_blueprint(public_bp, url_prefix="/waitinglist/public")
    app.register_blueprint(diagnosis_bp, url_prefix="/waitinglist/diagnosis")
    app.register_blueprint(department_bp, url_prefix="/waitinglist/department")
    app.register_blueprint(adminSuperAdmin_bp, url_prefix="/waitinglist/adminSuperAdmin")
    app.register_blueprint(user_bp, url_prefix="/waitinglist/user")
    app.register_blueprint(account_bp, url_prefix="/waitinglist/account")
    app.register_blueprint(patientdemographic_bp, url_prefix="/waitinglist/patientdemographic")
    app.register_blueprint(patiententry_bp, url_prefix="/waitinglist/patiententry")
    app.register_blueprint(plan_bp, url_prefix="/waitinglist/plan")
    app.register_blueprint(eye_bp, url_prefix="/waitinglist/eye")
    app.register_blueprint(priority_bp, url_prefix="/waitinglist/priority")
    app.register_blueprint(anesthesia_bp, url_prefix="/waitinglist/anesthesia")
    app.register_blueprint(eua_bp, url_prefix="/waitinglist/eua")
    app.register_blueprint(short_bp, url_prefix="/waitinglist/short")
    app.register_blueprint(cadre_bp, url_prefix="/waitinglist/cadre")
    app.register_blueprint(designation_bp, url_prefix="/waitinglist/designation")

    return app
