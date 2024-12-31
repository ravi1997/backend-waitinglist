from flask import jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import get_role, verify_SUPERADMIN_or_ADMIN, verify_body, verify_token
from app.models import Account, AccountRoles, Building, BuildingFloors, Cadre, Department, DepartmentUnits, Designation, Floor, FloorRooms, Role, Room, Unit,  User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import AccountSchema, BuildingSchema, CadreSchema, DepartmentSchema, DesignationSchema, FloorSchema, RoomSchema, UnitSchema, UserSchema
from app.util import generate_strong_password
from . import adminSuperAdmin_bp



@adminSuperAdmin_bp.route("/")
def index():
    return "This is The waiting list admin route"


@adminSuperAdmin_bp.route("/verifyUser/<id>", methods=["POST"])
@verify_SUPERADMIN_or_ADMIN
@verify_token
def verifyUserAdmin(session, id):
    user = User.query.filter_by(id=id).first_or_404()

    if user.isDeleted():
        return jsonify({"message":"User is deleted."}),401

    if user.isVerified():
        return jsonify({"message":"User is already verified."}),401

    user.verify(session.account_id)
    user.set_updated(session.account_id)
    db.session.commit()
    return jsonify({"message": "User is verified"}), 200


@adminSuperAdmin_bp.route("/verifyAccount/<id>", methods=["POST"])
@verify_SUPERADMIN_or_ADMIN
@verify_token
@get_role
def verifyAccountAdmin(role, session, id):
    account = Account.query.filter_by(id=id).first_or_404()

    if account.isDeleted():
        return jsonify({"message":"Account is deleted."}),401

    if account.isVerified():
        return jsonify({"message":"Account is already verified."}),401

    if role == "SUPERADMIN":
        account_roles = AccountRoles.query.filter_by(account_id=id)
        if account_roles is None:
            return jsonify({"message":f"Account cannot activate the id {id}"}),401

        for account_role in account_roles:
            role = Role.query.filter_by(id=account_role.role_id).first()
            if role.name == "ADMIN":
                account.verify(session.account_id)
                account.set_updated(session.account_id)
                db.session.commit()
                return jsonify({"message": "Account is verified"}), 200
        return jsonify({"message":f"Account cannot activate the id {id}"}),401
    elif role == "ADMIN":
        account_roles = AccountRoles.query.filter_by(account_id=id).all()
        if account_roles is None or account_roles == []:
            account.verify(session.account_id)
            account.set_updated(session.account_id)
            db.session.commit()
            return jsonify({"message": "Account is verified"}), 200
        current_app.logger.info(f"we came here : {account_roles}")
        return jsonify({"message":f"Account cannot activate the id {id}"}),401
    return jsonify({"message":f"Account is not authorised."}),401

@adminSuperAdmin_bp.route("/deleteAccount/<id>", methods=["DELETE"])
@verify_token
@verify_SUPERADMIN_or_ADMIN
def delete_account(session, id):
    account = Account.query.filter_by(id=id).one_or_none()

    if account.isNotVerified():
        return jsonify({"message":f"Account is not Activated : {id}"}),401

    if account.isDeleted():
        return jsonify({"message":f"Account is already deleted : {id}"}),401

    account.set_deleted(session.account_id)
    account.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "Account is deleted"}), 200


@adminSuperAdmin_bp.route("/restoreAccount/<id>", methods=["DELETE"])
@verify_token
@verify_SUPERADMIN_or_ADMIN
def restore_account(sesssion, id):

    account = Account.query.filter_by(id=id).one_or_none()
    if account.isNotVerified():
        return jsonify({"message":f"Account is not Activated : {id}"}),401

    if account.isDeleted() == False:
        return jsonify({"message":f"Account is already restored : {id}"}),401

    account.deleted = 0
    account.set_updated(sesssion.account_id)
    db.session.commit()

    return jsonify({"message": "Account is restored"}), 200


@adminSuperAdmin_bp.route("/deleteUser/<id>", methods=["DELETE"])
@verify_token
@verify_SUPERADMIN_or_ADMIN
def delete_user(session, id):

    user = User.query.filter_by(id=id).one_or_none()

    if user.isNotVerified():
        return jsonify({"message":f"User is not Activated : {id}"}),401

    if user.isDeleted():
        return jsonify({"message":f"User is already deleted : {id}"}),401

    user.set_deleted(session.account_id)
    user.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "User is deleted"}), 200


@adminSuperAdmin_bp.route("/restoreUser/<id>", methods=["DELETE"])
@verify_token
@verify_SUPERADMIN_or_ADMIN
def restore_user(session, id):
    user = User.query.filter_by(id=id).one_or_none()

    if user.isNotVerified():
        return jsonify({"message":f"User is not Activated : {id}"}),401

    if user.isDeleted() == False:
        return jsonify({"message":f"User is already restored : {id}"}),401

    user.deleted = 0
    user.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "User is restored"}), 200

