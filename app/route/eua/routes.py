from flask import abort, jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import get_role, verify_SUPERADMIN, verify_SUPERADMIN_or_ADMIN, verify_body, verify_token, verify_user
from app.models import Account, EUA, User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import EUASchema, UserSchema
from . import eua_bp

@eua_bp.route("/")
def index_eua():
    return "This is The waiting list eua route"


@eua_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_eua(request_data, session):
    try:
        schema = EUASchema()
        eua_data = schema.load(request_data)
        eua_name = eua_data.value

        existing_eua = EUA.query.filter_by(value=eua_name).first()
        if existing_eua:
            jsonify({"message":f"EUA '{eua_name}' already exists"}),400

        eua_data.set_created(session.account_id)
        db.session.add(eua_data)
        db.session.commit()

        current_app.logger.info(f"EUA created: {eua_name}")
        return jsonify({"message": f"EUA created: {eua_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating eua: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@eua_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_eua(request_data, session):
    """
    Route to create a new eua.

    Only SUPERADMIN users can create a eua.
    """
    try:
        schema = EUASchema(many=True)
        euas_data = schema.load(request_data)

        for eua_data in euas_data:
            eua_name = eua_data.value

            existing_eua = EUA.query.filter_by(value=eua_name).first()
            if existing_eua:
                current_app.logger.info(f"EUA '{eua_name}' already exists")
                continue
            try:
                eua_data.set_created(session.account_id)

                db.session.add(eua_data)
                db.session.commit()
                current_app.logger.info(f"EUA created: {eua_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating eua: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All eua created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating eua: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@eua_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_euas():
    """
    Route to get all euas.
    """
    try:
        schema = EUASchema(many=True)
        euas = EUA.query.all()
        return schema.jsonify(euas), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@eua_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_euas():
    """
    Route to get all inactive euas.
    """
    try:
        schema = EUASchema(many=True)
        euas = EUA.query.filter_by(deleted=1).all()
        return schema.jsonify(euas), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@eua_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_euas(account):
    """
    Route to get all active euas.
    """
    try:
        schema = EUASchema(many=True)
        euas = EUA.query.filter_by(deleted=0).all()
        return schema.jsonify(euas), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@eua_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_eua(id):
    """
    Route to get a specific eua by ID.
    """
    schema = EUASchema()
    eua = EUA.query.filter_by(id=id).first_or_404()
    return schema.jsonify(eua), 200


@eua_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_eua(value):
    """
    Route to get a specific eua by value.
    """
    schema = EUASchema()
    eua = EUA.query.filter_by(value=value).first_or_404()

    return schema.jsonify(eua), 200


@eua_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_eua(request_data, session):
    """
    Route to update a eua.

    Only ADMIN users can update a eua.
    """
    schema = EUASchema()

    try:
        eua_data = schema.load(request_data)
        eua = EUA.query.get(eua_data.id)
        if not eua:
            return jsonify({"message":f"EUA {eua_data.id} not found"}),404

        eua.value = eua_data.value  # Update other fields as needed

        eua.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "EUA updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating EUA: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@eua_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_eua(session, id):
    """
    Route to delete a single eua by ID.

    Only ADMIN users can delete a eua.
    """
    eua = EUA.query.filter_by(id=id).first_or_404()
    if eua.isDeleted():
        return jsonify({"message":f"EUA {id} is already deleted"}),400

    eua.set_deleted(session.account_id)
    eua.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "EUA deleted successfully"}), 200


@eua_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_euas(session):
    """
    Route to delete all euas.

    Only ADMIN users can delete all euas.
    """
    euas = EUA.query.all()
    for eua in euas:
        eua.set_deleted(session.account_id)
        eua.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All euas deleted successfully"}), 200


@eua_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_eua(session, id):
    """
    Route to restore a single eua by ID.

    Only ADMIN users can restore a eua.
    """
    eua = EUA.query.filter_by(id=id).first_or_404()

    if eua.isDeleted():
        eua.set_restore(session.account_id)
        eua.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "EUA restore successfully"}), 200
    else:
        return jsonify({"message": "EUA is already restored"}), 400


@eua_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_eua(session):
    """
    Route to restore all eua.

    Only ADMIN users can restore all eua.
    """
    eua = EUA.query.all()
    for eua in eua:
        if eua.isDeleted():
            eua.set_restore(session.account_id)
            eua.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All eua restore successfully"}), 200


