from flask import abort, jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import get_role, verify_SUPERADMIN, verify_SUPERADMIN_or_ADMIN, verify_body, verify_token, verify_user
from app.models import Account, Anesthesia, User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import AnesthesiaSchema, UserSchema
from . import anesthesia_bp

@anesthesia_bp.route("/")
def index_anesthesia():
    return "This is The waiting list anesthesia route"


@anesthesia_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_anesthesia(request_data, session):
    try:
        schema = AnesthesiaSchema()
        anesthesia_data = schema.load(request_data)
        anesthesia_name = anesthesia_data.value

        existing_anesthesia = Anesthesia.query.filter_by(value=anesthesia_name).first()
        if existing_anesthesia:
            jsonify({"message":f"Anesthesia '{anesthesia_name}' already exists"}),400

        anesthesia_data.set_created(session.account_id)
        db.session.add(anesthesia_data)
        db.session.commit()

        current_app.logger.info(f"Anesthesia created: {anesthesia_name}")
        return jsonify({"message": f"Anesthesia created: {anesthesia_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating anesthesia: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@anesthesia_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_anesthesia(request_data, session):
    """
    Route to create a new anesthesia.

    Only SUPERADMIN users can create a anesthesia.
    """
    try:
        schema = AnesthesiaSchema(many=True)
        anesthesias_data = schema.load(request_data)

        for anesthesia_data in anesthesias_data:
            anesthesia_name = anesthesia_data.value

            existing_anesthesia = Anesthesia.query.filter_by(value=anesthesia_name).first()
            if existing_anesthesia:
                current_app.logger.info(f"Anesthesia '{anesthesia_name}' already exists")
                continue
            try:
                anesthesia_data.set_created(session.account_id)

                db.session.add(anesthesia_data)
                db.session.commit()
                current_app.logger.info(f"Anesthesia created: {anesthesia_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating anesthesia: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All anesthesia created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating anesthesia: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@anesthesia_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_anesthesias():
    """
    Route to get all anesthesias.
    """
    try:
        schema = AnesthesiaSchema(many=True)
        anesthesias = Anesthesia.query.all()
        return schema.jsonify(anesthesias), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@anesthesia_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_anesthesias():
    """
    Route to get all inactive anesthesias.
    """
    try:
        schema = AnesthesiaSchema(many=True)
        anesthesias = Anesthesia.query.filter_by(deleted=1).all()
        return schema.jsonify(anesthesias), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@anesthesia_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_anesthesias(account):
    """
    Route to get all active anesthesias.
    """
    try:
        schema = AnesthesiaSchema(many=True)
        anesthesias = Anesthesia.query.filter_by(deleted=0).all()
        return schema.jsonify(anesthesias), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@anesthesia_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_anesthesia(id):
    """
    Route to get a specific anesthesia by ID.
    """
    schema = AnesthesiaSchema()
    anesthesia = Anesthesia.query.filter_by(id=id).first_or_404()
    return schema.jsonify(anesthesia), 200


@anesthesia_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_anesthesia(value):
    """
    Route to get a specific anesthesia by value.
    """
    schema = AnesthesiaSchema()
    anesthesia = Anesthesia.query.filter_by(value=value).first_or_404()

    return schema.jsonify(anesthesia), 200


@anesthesia_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_anesthesia(request_data, session):
    """
    Route to update a anesthesia.

    Only ADMIN users can update a anesthesia.
    """
    schema = AnesthesiaSchema()

    try:
        anesthesia_data = schema.load(request_data)
        anesthesia = Anesthesia.query.get(anesthesia_data.id)
        if not anesthesia:
            return jsonify({"message":f"Anesthesia {anesthesia_data.id} not found"}),404

        anesthesia.value = anesthesia_data.value  # Update other fields as needed

        anesthesia.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Anesthesia updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Anesthesia: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@anesthesia_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_anesthesia(session, id):
    """
    Route to delete a single anesthesia by ID.

    Only ADMIN users can delete a anesthesia.
    """
    anesthesia = Anesthesia.query.filter_by(id=id).first_or_404()
    if anesthesia.isDeleted():
        return jsonify({"message":f"Anesthesia {id} is already deleted"}),400

    anesthesia.set_deleted(session.account_id)
    anesthesia.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "Anesthesia deleted successfully"}), 200


@anesthesia_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_anesthesias(session):
    """
    Route to delete all anesthesias.

    Only ADMIN users can delete all anesthesias.
    """
    anesthesias = Anesthesia.query.all()
    for anesthesia in anesthesias:
        anesthesia.set_deleted(session.account_id)
        anesthesia.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All anesthesias deleted successfully"}), 200


@anesthesia_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_anesthesia(session, id):
    """
    Route to restore a single anesthesia by ID.

    Only ADMIN users can restore a anesthesia.
    """
    anesthesia = Anesthesia.query.filter_by(id=id).first_or_404()

    if anesthesia.isDeleted():
        anesthesia.set_restore(session.account_id)
        anesthesia.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "Anesthesia restore successfully"}), 200
    else:
        return jsonify({"message": "Anesthesia is already restored"}), 400


@anesthesia_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_anesthesia(session):
    """
    Route to restore all anesthesia.

    Only ADMIN users can restore all anesthesia.
    """
    anesthesia = Anesthesia.query.all()
    for anesthesia in anesthesia:
        if anesthesia.isDeleted():
            anesthesia.set_restore(session.account_id)
            anesthesia.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All anesthesia restore successfully"}), 200


