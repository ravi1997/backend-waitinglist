from datetime import datetime
import uuid
from flask import jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import verify_body, verify_token
from app.models import Account, TokenList, User
from app.extension import db,scheduler
from app.schema import AccountSchema, LoginAccoutSchema, UserSchema
from . import auth_bp

@auth_bp.route("/")
def index():
    return "This is The waiting list auth route"


def delete_session(jwt):
    with current_app.app_context():
        # print(jwt)
        token = TokenList.query.filter(
            jwt == str(jwt).lower()
        ).first()
        if token:
            db.session.delete(token)
            db.session.commit()
        else:
            print("Not Found")


@auth_bp.route("/login", methods=["POST"])
@verify_body
def login(request_data):
    schema = LoginAccoutSchema()
    user_schema = UserSchema()
    account_schema = AccountSchema()
    try:
        errors = schema.validate(request_data)
        if errors:
            return jsonify({"message":errors}),400
            

        # Convert validated request schema into a User object
        useraccount_data = schema.load(request_data)

        userAccount = Account.query.filter_by(
            username=useraccount_data.username
        ).one_or_none()
        if not userAccount:
            return jsonify({"message":"Wrong username"}),401

        if userAccount.isDeleted():
            return jsonify({"message":"Account is deleted."}),401

        if userAccount.isVerified() == False:
            return jsonify({"message":"Account is not verfied. Please try again."}),401

        if userAccount.isBlocked():
            return jsonify({"message":"Account is blocked. Please contact admin."}),401

        if not userAccount.check_password(useraccount_data.password):
            userAccount.wrongAttempt = useraccount_data.wrongAttempt + 1
            attempt = 5 - userAccount.wrongAttempt
            db.session.commit()

            if attempt == 0:
                userAccount.blockAccount()
                db.session.commit()
                return jsonify({"message":"Wrong password. Account blocked"}),401
            else:
                return jsonify({"message":f"Wrong password. {attempt} left"}),401

        useraccount_data.wrongAttempt = 0
        db.session.commit()

        access_token = str(uuid.uuid4())

        db.session.add(TokenList(jwt=access_token, account_id=userAccount.id))
        db.session.commit()

        job_id = access_token

        delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]

        scheduler.add_job(
            str(job_id),
            delete_session,
            trigger="date",
            run_date=datetime.now() + delta,
            args=[access_token],
        )
        user = User.query.filter_by(id=userAccount.user_id).first_or_404()
        return jsonify(
            access_token=access_token,
            user=user_schema.dump(user),
            account=account_schema.dump(userAccount),
        )
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify({"message":err.messages}),400


@auth_bp.route("/logout", methods=["GET"])
@verify_token
def logout(session):
    current_user = session.account_id
    db.session.delete(session)
    db.session.commit()
    return jsonify(logged_in_as=current_user), 200
