import traceback
from flask import jsonify,current_app
from marshmallow import ValidationError

from app.decorator import verify_SUPERADMIN, verify_body, verify_token, verify_user
from app.models import Designation
from app.extension import db

from flask import jsonify

from app.schema import DesignationSchema
from . import designation_bp

@designation_bp.route("/")
def index_designation():
    return "This is The waiting list designation route"


@designation_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_designation(request_data, session):
    try:
        schema = DesignationSchema()
        errors = schema.validate(request_data)
        if errors:
            return jsonify({"message":errors}),400

        designation_data = schema.load(request_data)
        designation_name = designation_data.name

        existing_designation = Designation.query.filter_by(name=designation_name).first()
        if existing_designation:
            jsonify({"message":f"Designation '{designation_name}' already exists"}),400

        designation_data.set_created(session.account_id)
        db.session.add(designation_data)
        db.session.commit()

        current_app.logger.info(f"Designation created: {designation_name}")
        return jsonify({"message": f"Designation created: {designation_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        current_app.logger.error(f"Error creating designation: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@designation_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_designation(request_data, session):
    """
    Route to create a new designation.

    Only SUPERADMIN users can create a designation.
    """
    try:
        schema = DesignationSchema(many=True)
        errors = schema.validate(request_data)
        if errors:
            return jsonify({"message":errors}),400
        designations_data = schema.load(request_data)

        for designation_data in designations_data:
            designation_name = designation_data.name

            existing_designation = Designation.query.filter_by(name=designation_name).first()
            if existing_designation:
                current_app.logger.info(f"Designation '{designation_name}' already exists")
                continue
            try:
                designation_data.set_created(session.account_id)

                db.session.add(designation_data)
                db.session.commit()
                current_app.logger.info(f"Designation created: {designation_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating designation: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All designation created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        current_app.logger.error(f"Error creating designation: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@designation_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_designations():
    """
    Route to get all designations.
    """
    try:
        schema = DesignationSchema(many=True)
        designations = Designation.query.all()
        return schema.jsonify(designations), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@designation_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_designations():
    """
    Route to get all inactive designations.
    """
    try:
        schema = DesignationSchema(many=True)
        designations = Designation.query.filter_by(deleted=1).all()
        return schema.jsonify(designations), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@designation_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_designations(account):
    """
    Route to get all active designations.
    """
    try:
        schema = DesignationSchema(many=True)
        designations = Designation.query.filter_by(deleted=0).all()
        return schema.jsonify(designations), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@designation_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_designation(id):
    """
    Route to get a specific designation by ID.
    """
    schema = DesignationSchema()
    designation = Designation.query.filter_by(id=id).first_or_404()
    return schema.jsonify(designation), 200


@designation_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_designation(value):
    """
    Route to get a specific designation by value.
    """
    schema = DesignationSchema()
    designation = Designation.query.filter_by(value=value).first_or_404()

    return schema.jsonify(designation), 200


@designation_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_designation(request_data, session):
    """
    Route to update a designation.

    Only ADMIN users can update a designation.
    """
    schema = DesignationSchema()

    try:
        designation_data = schema.load(request_data)
        designation = Designation.query.get(designation_data.id)
        if not designation:
            return jsonify({"message":f"Designation {designation_data.id} not found"}),404

        designation.value = designation_data.value  # Update other fields as needed

        designation.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Designation updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Designation: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@designation_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_designation(session, id):
    """
    Route to delete a single designation by ID.

    Only ADMIN users can delete a designation.
    """
    designation = Designation.query.filter_by(id=id).first_or_404()
    if designation.isDeleted():
        return jsonify({"message":f"Designation {id} is already deleted"}),400

    designation.set_deleted(session.account_id)
    designation.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "Designation deleted successfully"}), 200


@designation_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_designations(session):
    """
    Route to delete all designations.

    Only ADMIN users can delete all designations.
    """
    designations = Designation.query.all()
    for designation in designations:
        designation.set_deleted(session.account_id)
        designation.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All designations deleted successfully"}), 200


@designation_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_designation(session, id):
    """
    Route to restore a single designation by ID.

    Only ADMIN users can restore a designation.
    """
    designation = Designation.query.filter_by(id=id).first_or_404()

    if designation.isDeleted():
        designation.set_restore(session.account_id)
        designation.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "Designation restore successfully"}), 200
    else:
        return jsonify({"message": "Designation is already restored"}), 400


@designation_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_designation(session):
    """
    Route to restore all designation.

    Only ADMIN users can restore all designation.
    """
    designation = Designation.query.all()
    for designation in designation:
        if designation.isDeleted():
            designation.set_restore(session.account_id)
            designation.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All designation restore successfully"}), 200


