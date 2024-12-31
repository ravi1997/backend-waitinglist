import traceback
from flask import jsonify,current_app
from marshmallow import ValidationError

from app.decorator import verify_SUPERADMIN, verify_body, verify_token, verify_user
from app.models import Cadre
from app.extension import db

from flask import jsonify

from app.schema import CadreSchema
from . import cadre_bp

@cadre_bp.route("/")
def index_cadre():
    return "This is The waiting list cadre route"


@cadre_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_cadre(request_data, session):
    try:
        schema = CadreSchema()
        errors = schema.validate(request_data)
        if errors:
            return jsonify({"message":errors}),400

        cadre_data = schema.load(request_data)
        cadre_name = cadre_data.name

        existing_cadre = Cadre.query.filter_by(name=cadre_name).first()
        if existing_cadre:
            jsonify({"message":f"Cadre '{cadre_name}' already exists"}),400

        cadre_data.set_created(session.account_id)
        db.session.add(cadre_data)
        db.session.commit()

        current_app.logger.info(f"Cadre created: {cadre_name}")
        return jsonify({"message": f"Cadre created: {cadre_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        current_app.logger.error(f"Error creating cadre: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@cadre_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_cadre(request_data, session):
    """
    Route to create a new cadre.

    Only SUPERADMIN users can create a cadre.
    """
    try:
        schema = CadreSchema(many=True)
        errors = schema.validate(request_data)
        if errors:
            return jsonify({"message":errors}),400
        cadres_data = schema.load(request_data)

        for cadre_data in cadres_data:
            cadre_name = cadre_data.name

            existing_cadre = Cadre.query.filter_by(name=cadre_name).first()
            if existing_cadre:
                current_app.logger.info(f"Cadre '{cadre_name}' already exists")
                continue
            try:
                cadre_data.set_created(session.account_id)

                db.session.add(cadre_data)
                db.session.commit()
                current_app.logger.info(f"Cadre created: {cadre_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating cadre: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All cadre created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        current_app.logger.error(f"Error creating cadre: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@cadre_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_cadres():
    """
    Route to get all cadres.
    """
    try:
        schema = CadreSchema(many=True)
        cadres = Cadre.query.all()
        return schema.jsonify(cadres), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@cadre_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_cadres():
    """
    Route to get all inactive cadres.
    """
    try:
        schema = CadreSchema(many=True)
        cadres = Cadre.query.filter_by(deleted=1).all()
        return schema.jsonify(cadres), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@cadre_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_cadres(account):
    """
    Route to get all active cadres.
    """
    try:
        schema = CadreSchema(many=True)
        cadres = Cadre.query.filter_by(deleted=0).all()
        return schema.jsonify(cadres), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@cadre_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_cadre(id):
    """
    Route to get a specific cadre by ID.
    """
    schema = CadreSchema()
    cadre = Cadre.query.filter_by(id=id).first_or_404()
    return schema.jsonify(cadre), 200


@cadre_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_cadre(value):
    """
    Route to get a specific cadre by value.
    """
    schema = CadreSchema()
    cadre = Cadre.query.filter_by(value=value).first_or_404()

    return schema.jsonify(cadre), 200


@cadre_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_cadre(request_data, session):
    """
    Route to update a cadre.

    Only ADMIN users can update a cadre.
    """
    schema = CadreSchema()

    try:
        cadre_data = schema.load(request_data)
        cadre = Cadre.query.get(cadre_data.id)
        if not cadre:
            return jsonify({"message":f"Cadre {cadre_data.id} not found"}),404

        cadre.value = cadre_data.value  # Update other fields as needed

        cadre.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Cadre updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Cadre: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@cadre_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_cadre(session, id):
    """
    Route to delete a single cadre by ID.

    Only ADMIN users can delete a cadre.
    """
    cadre = Cadre.query.filter_by(id=id).first_or_404()
    if cadre.isDeleted():
        return jsonify({"message":f"Cadre {id} is already deleted"}),400

    cadre.set_deleted(session.account_id)
    cadre.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "Cadre deleted successfully"}), 200


@cadre_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_cadres(session):
    """
    Route to delete all cadres.

    Only ADMIN users can delete all cadres.
    """
    cadres = Cadre.query.all()
    for cadre in cadres:
        cadre.set_deleted(session.account_id)
        cadre.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All cadres deleted successfully"}), 200


@cadre_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_cadre(session, id):
    """
    Route to restore a single cadre by ID.

    Only ADMIN users can restore a cadre.
    """
    cadre = Cadre.query.filter_by(id=id).first_or_404()

    if cadre.isDeleted():
        cadre.set_restore(session.account_id)
        cadre.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "Cadre restore successfully"}), 200
    else:
        return jsonify({"message": "Cadre is already restored"}), 400


@cadre_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_cadre(session):
    """
    Route to restore all cadre.

    Only ADMIN users can restore all cadre.
    """
    cadre = Cadre.query.all()
    for cadre in cadre:
        if cadre.isDeleted():
            cadre.set_restore(session.account_id)
            cadre.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All cadre restore successfully"}), 200


