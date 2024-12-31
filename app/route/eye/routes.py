from flask import abort, jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import get_role, verify_SUPERADMIN, verify_SUPERADMIN_or_ADMIN, verify_body, verify_token, verify_user
from app.models import Account, Eye, User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import EyeSchema, UserSchema
from . import eye_bp

@eye_bp.route("/")
def index_eye():
    return "This is The waiting list eye route"


@eye_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_eye(request_data, session):
    try:
        schema = EyeSchema()
        eye_data = schema.load(request_data)
        eye_name = eye_data.value

        existing_eye = Eye.query.filter_by(value=eye_name).first()
        if existing_eye:
            jsonify({"message":f"Eye '{eye_name}' already exists"}),400

        eye_data.set_created(session.account_id)
        db.session.add(eye_data)
        db.session.commit()

        current_app.logger.info(f"Eye created: {eye_name}")
        return jsonify({"message": f"Eye created: {eye_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating eye: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@eye_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_eye(request_data, session):
    """
    Route to create a new eye.

    Only SUPERADMIN users can create a eye.
    """
    try:
        schema = EyeSchema(many=True)
        eyes_data = schema.load(request_data)

        for eye_data in eyes_data:
            eye_name = eye_data.value

            existing_eye = Eye.query.filter_by(value=eye_name).first()
            if existing_eye:
                current_app.logger.info(f"Eye '{eye_name}' already exists")
                continue
            try:
                eye_data.set_created(session.account_id)

                db.session.add(eye_data)
                db.session.commit()
                current_app.logger.info(f"Eye created: {eye_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating eye: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All eye created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating eye: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@eye_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_eyes():
    """
    Route to get all eyes.
    """
    try:
        schema = EyeSchema(many=True)
        eyes = Eye.query.all()
        return schema.jsonify(eyes), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@eye_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_eyes():
    """
    Route to get all inactive eyes.
    """
    try:
        schema = EyeSchema(many=True)
        eyes = Eye.query.filter_by(deleted=1).all()
        return schema.jsonify(eyes), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@eye_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_eyes(account):
    """
    Route to get all active eyes.
    """
    try:
        schema = EyeSchema(many=True)
        eyes = Eye.query.filter_by(deleted=0).all()
        return schema.jsonify(eyes), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@eye_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_eye(id):
    """
    Route to get a specific eye by ID.
    """
    schema = EyeSchema()
    eye = Eye.query.filter_by(id=id).first_or_404()
    return schema.jsonify(eye), 200


@eye_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_eye(value):
    """
    Route to get a specific eye by value.
    """
    schema = EyeSchema()
    eye = Eye.query.filter_by(value=value).first_or_404()

    return schema.jsonify(eye), 200


@eye_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_eye(request_data, session):
    """
    Route to update a eye.

    Only ADMIN users can update a eye.
    """
    schema = EyeSchema()

    try:
        eye_data = schema.load(request_data)
        eye = Eye.query.get(eye_data.id)
        if not eye:
            return jsonify({"message":f"Eye {eye_data.id} not found"}),404

        eye.value = eye_data.value  # Update other fields as needed

        eye.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Eye updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Eye: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@eye_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_eye(session, id):
    """
    Route to delete a single eye by ID.

    Only ADMIN users can delete a eye.
    """
    eye = Eye.query.filter_by(id=id).first_or_404()
    if eye.isDeleted():
        return jsonify({"message":f"Eye {id} is already deleted"}),400

    eye.set_deleted(session.account_id)
    eye.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "Eye deleted successfully"}), 200


@eye_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_eyes(session):
    """
    Route to delete all eyes.

    Only ADMIN users can delete all eyes.
    """
    eyes = Eye.query.all()
    for eye in eyes:
        eye.set_deleted(session.account_id)
        eye.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All eyes deleted successfully"}), 200


@eye_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_eye(session, id):
    """
    Route to restore a single eye by ID.

    Only ADMIN users can restore a eye.
    """
    eye = Eye.query.filter_by(id=id).first_or_404()

    if eye.isDeleted():
        eye.set_restore(session.account_id)
        eye.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "Eye restore successfully"}), 200
    else:
        return jsonify({"message": "Eye is already restored"}), 400


@eye_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_eye(session):
    """
    Route to restore all eye.

    Only ADMIN users can restore all eye.
    """
    eye = Eye.query.all()
    for eye in eye:
        if eye.isDeleted():
            eye.set_restore(session.account_id)
            eye.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All eye restore successfully"}), 200


