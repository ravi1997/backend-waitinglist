from flask import abort, jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import verify_SUPERADMIN, verify_body, verify_token, verify_user
from app.models import Daycare
from app.extension import db

from flask import jsonify

from app.schema import DaycareSchema
from . import daycare_bp

@daycare_bp.route("/")
def index_daycare():
    return "This is The waiting list daycare route"


@daycare_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_daycare(request_data, session):
    try:
        schema = DaycareSchema()
        daycare_data = schema.load(request_data)
        daycare_name = daycare_data.value

        existing_daycare = Daycare.query.filter_by(value=daycare_name).first()
        if existing_daycare:
            jsonify({"message":f"Daycare '{daycare_name}' already exists"}),400

        daycare_data.set_created(session.account_id)
        db.session.add(daycare_data)
        db.session.commit()

        current_app.logger.info(f"Daycare created: {daycare_name}")
        return jsonify({"message": f"Daycare created: {daycare_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating daycare: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@daycare_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_daycare(request_data, session):
    """
    Route to create a new daycare.

    Only SUPERADMIN users can create a daycare.
    """
    try:
        schema = DaycareSchema(many=True)
        daycares_data = schema.load(request_data)

        for daycare_data in daycares_data:
            daycare_name = daycare_data.value

            existing_daycare = Daycare.query.filter_by(value=daycare_name).first()
            if existing_daycare:
                current_app.logger.info(f"Daycare '{daycare_name}' already exists")
                continue
            try:
                daycare_data.set_created(session.account_id)

                db.session.add(daycare_data)
                db.session.commit()
                current_app.logger.info(f"Daycare created: {daycare_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating daycare: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All daycare created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating daycare: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@daycare_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_daycares():
    """
    Route to get all daycares.
    """
    try:
        schema = DaycareSchema(many=True)
        daycares = Daycare.query.all()
        return schema.jsonify(daycares), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@daycare_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_daycares():
    """
    Route to get all inactive daycares.
    """
    try:
        schema = DaycareSchema(many=True)
        daycares = Daycare.query.filter_by(deleted=1).all()
        return schema.jsonify(daycares), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@daycare_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_daycares(account):
    """
    Route to get all active daycares.
    """
    try:
        schema = DaycareSchema(many=True)
        daycares = Daycare.query.filter_by(deleted=0).all()
        return schema.jsonify(daycares), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@daycare_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_daycare(id):
    """
    Route to get a specific daycare by ID.
    """
    schema = DaycareSchema()
    daycare = Daycare.query.filter_by(id=id).first_or_404()
    return schema.jsonify(daycare), 200


@daycare_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_daycare(value):
    """
    Route to get a specific daycare by value.
    """
    schema = DaycareSchema()
    daycare = Daycare.query.filter_by(value=value).first_or_404()

    return schema.jsonify(daycare), 200


@daycare_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_daycare(request_data, session):
    """
    Route to update a daycare.

    Only ADMIN users can update a daycare.
    """
    schema = DaycareSchema()

    try:
        daycare_data = schema.load(request_data)
        daycare = Daycare.query.get(daycare_data.id)
        if not daycare:
            return jsonify({"message":f"Daycare {daycare_data.id} not found"}),404

        daycare.value = daycare_data.value  # Update other fields as needed

        daycare.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Daycare updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Daycare: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@daycare_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_daycare(session, id):
    """
    Route to delete a single daycare by ID.

    Only ADMIN users can delete a daycare.
    """
    daycare = Daycare.query.filter_by(id=id).first_or_404()
    if daycare.isDeleted():
        return jsonify({"message":f"Daycare {id} is already deleted"}),400

    daycare.set_deleted(session.account_id)
    daycare.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "Daycare deleted successfully"}), 200


@daycare_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_daycares(session):
    """
    Route to delete all daycares.

    Only ADMIN users can delete all daycares.
    """
    daycares = Daycare.query.all()
    for daycare in daycares:
        daycare.set_deleted(session.account_id)
        daycare.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All daycares deleted successfully"}), 200


@daycare_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_daycare(session, id):
    """
    Route to restore a single daycare by ID.

    Only ADMIN users can restore a daycare.
    """
    daycare = Daycare.query.filter_by(id=id).first_or_404()

    if daycare.isDeleted():
        daycare.set_restore(session.account_id)
        daycare.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "Daycare restore successfully"}), 200
    else:
        return jsonify({"message": "Daycare is already restored"}), 400


@daycare_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_daycare(session):
    """
    Route to restore all daycare.

    Only ADMIN users can restore all daycare.
    """
    daycare = Daycare.query.all()
    for daycare in daycare:
        if daycare.isDeleted():
            daycare.set_restore(session.account_id)
            daycare.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All daycare restore successfully"}), 200


