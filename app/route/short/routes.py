from flask import abort, jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import verify_SUPERADMIN, verify_body, verify_token, verify_user
from app.models import Short
from app.extension import db

from flask import jsonify

from app.schema import ShortSchema
from . import short_bp

@short_bp.route("/")
def index_short():
    return "This is The waiting list short route"


@short_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_short(request_data, session):
    try:
        schema = ShortSchema()
        short_data = schema.load(request_data)
        short_name = short_data.value

        existing_short = Short.query.filter_by(value=short_name).first()
        if existing_short:
            jsonify({"message":f"Short '{short_name}' already exists"}),400

        short_data.set_created(session.account_id)
        db.session.add(short_data)
        db.session.commit()

        current_app.logger.info(f"Short created: {short_name}")
        return jsonify({"message": f"Short created: {short_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating short: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@short_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_short(request_data, session):
    """
    Route to create a new short.

    Only SUPERADMIN users can create a short.
    """
    try:
        schema = ShortSchema(many=True)
        shorts_data = schema.load(request_data)

        for short_data in shorts_data:
            short_name = short_data.value

            existing_short = Short.query.filter_by(value=short_name).first()
            if existing_short:
                current_app.logger.info(f"Short '{short_name}' already exists")
                continue
            try:
                short_data.set_created(session.account_id)

                db.session.add(short_data)
                db.session.commit()
                current_app.logger.info(f"Short created: {short_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating short: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All short created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating short: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@short_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_shorts():
    """
    Route to get all shorts.
    """
    try:
        schema = ShortSchema(many=True)
        shorts = Short.query.all()
        return schema.jsonify(shorts), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@short_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_shorts():
    """
    Route to get all inactive shorts.
    """
    try:
        schema = ShortSchema(many=True)
        shorts = Short.query.filter_by(deleted=1).all()
        return schema.jsonify(shorts), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@short_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_shorts(account):
    """
    Route to get all active shorts.
    """
    try:
        schema = ShortSchema(many=True)
        shorts = Short.query.filter_by(deleted=0).all()
        return schema.jsonify(shorts), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@short_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_short(id):
    """
    Route to get a specific short by ID.
    """
    schema = ShortSchema()
    short = Short.query.filter_by(id=id).first_or_404()
    return schema.jsonify(short), 200


@short_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_short(value):
    """
    Route to get a specific short by value.
    """
    schema = ShortSchema()
    short = Short.query.filter_by(value=value).first_or_404()

    return schema.jsonify(short), 200


@short_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_short(request_data, session):
    """
    Route to update a short.

    Only ADMIN users can update a short.
    """
    schema = ShortSchema()

    try:
        short_data = schema.load(request_data)
        short = Short.query.get(short_data.id)
        if not short:
            return jsonify({"message":f"Short {short_data.id} not found"}),404

        short.value = short_data.value  # Update other fields as needed

        short.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Short updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Short: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@short_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_short(session, id):
    """
    Route to delete a single short by ID.

    Only ADMIN users can delete a short.
    """
    short = Short.query.filter_by(id=id).first_or_404()
    if short.isDeleted():
        return jsonify({"message":f"Short {id} is already deleted"}),400

    short.set_deleted(session.account_id)
    short.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "Short deleted successfully"}), 200


@short_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_shorts(session):
    """
    Route to delete all shorts.

    Only ADMIN users can delete all shorts.
    """
    shorts = Short.query.all()
    for short in shorts:
        short.set_deleted(session.account_id)
        short.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All shorts deleted successfully"}), 200


@short_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_short(session, id):
    """
    Route to restore a single short by ID.

    Only ADMIN users can restore a short.
    """
    short = Short.query.filter_by(id=id).first_or_404()

    if short.isDeleted():
        short.set_restore(session.account_id)
        short.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "Short restore successfully"}), 200
    else:
        return jsonify({"message": "Short is already restored"}), 400


@short_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_short(session):
    """
    Route to restore all short.

    Only ADMIN users can restore all short.
    """
    short = Short.query.all()
    for short in short:
        if short.isDeleted():
            short.set_restore(session.account_id)
            short.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All short restore successfully"}), 200


