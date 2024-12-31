from flask import abort, jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import get_role, verify_SUPERADMIN, verify_SUPERADMIN_or_ADMIN, verify_body, verify_token, verify_user
from app.models import Account, Priority, User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import PrioritySchema, UserSchema
from . import priority_bp

@priority_bp.route("/")
def index_priority():
    return "This is The waiting list priority route"


@priority_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_priority(request_data, session):
    try:
        schema = PrioritySchema()
        priority_data = schema.load(request_data)
        priority_name = priority_data.value

        existing_priority = Priority.query.filter_by(value=priority_name).first()
        if existing_priority:
            jsonify({"message":f"Priority '{priority_name}' already exists"}),400

        priority_data.set_created(session.account_id)
        db.session.add(priority_data)
        db.session.commit()

        current_app.logger.info(f"Priority created: {priority_name}")
        return jsonify({"message": f"Priority created: {priority_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating priority: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@priority_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_priority(request_data, session):
    """
    Route to create a new priority.

    Only SUPERADMIN users can create a priority.
    """
    try:
        schema = PrioritySchema(many=True)
        prioritys_data = schema.load(request_data)

        for priority_data in prioritys_data:
            priority_name = priority_data.value

            existing_priority = Priority.query.filter_by(value=priority_name).first()
            if existing_priority:
                current_app.logger.info(f"Priority '{priority_name}' already exists")
                continue
            try:
                priority_data.set_created(session.account_id)

                db.session.add(priority_data)
                db.session.commit()
                current_app.logger.info(f"Priority created: {priority_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating priority: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All priority created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating priority: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@priority_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_prioritys():
    """
    Route to get all prioritys.
    """
    try:
        schema = PrioritySchema(many=True)
        prioritys = Priority.query.all()
        return schema.jsonify(prioritys), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@priority_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_prioritys():
    """
    Route to get all inactive prioritys.
    """
    try:
        schema = PrioritySchema(many=True)
        prioritys = Priority.query.filter_by(deleted=1).all()
        return schema.jsonify(prioritys), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@priority_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_prioritys(account):
    """
    Route to get all active prioritys.
    """
    try:
        schema = PrioritySchema(many=True)
        prioritys = Priority.query.filter_by(deleted=0).all()
        return schema.jsonify(prioritys), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@priority_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_priority(id):
    """
    Route to get a specific priority by ID.
    """
    schema = PrioritySchema()
    priority = Priority.query.filter_by(id=id).first_or_404()
    return schema.jsonify(priority), 200


@priority_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_priority(value):
    """
    Route to get a specific priority by value.
    """
    schema = PrioritySchema()
    priority = Priority.query.filter_by(value=value).first_or_404()

    return schema.jsonify(priority), 200


@priority_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_priority(request_data, session):
    """
    Route to update a priority.

    Only ADMIN users can update a priority.
    """
    schema = PrioritySchema()

    try:
        priority_data = schema.load(request_data)
        priority = Priority.query.get(priority_data.id)
        if not priority:
            return jsonify({"message":f"Priority {priority_data.id} not found"}),404

        priority.value = priority_data.value  # Update other fields as needed

        priority.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Priority updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Priority: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@priority_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_priority(session, id):
    """
    Route to delete a single priority by ID.

    Only ADMIN users can delete a priority.
    """
    priority = Priority.query.filter_by(id=id).first_or_404()
    if priority.isDeleted():
        return jsonify({"message":f"Priority {id} is already deleted"}),400

    priority.set_deleted(session.account_id)
    priority.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "Priority deleted successfully"}), 200


@priority_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_prioritys(session):
    """
    Route to delete all prioritys.

    Only ADMIN users can delete all prioritys.
    """
    prioritys = Priority.query.all()
    for priority in prioritys:
        priority.set_deleted(session.account_id)
        priority.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All prioritys deleted successfully"}), 200


@priority_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_priority(session, id):
    """
    Route to restore a single priority by ID.

    Only ADMIN users can restore a priority.
    """
    priority = Priority.query.filter_by(id=id).first_or_404()

    if priority.isDeleted():
        priority.set_restore(session.account_id)
        priority.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "Priority restore successfully"}), 200
    else:
        return jsonify({"message": "Priority is already restored"}), 400


@priority_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_priority(session):
    """
    Route to restore all priority.

    Only ADMIN users can restore all priority.
    """
    priority = Priority.query.all()
    for priority in priority:
        if priority.isDeleted():
            priority.set_restore(session.account_id)
            priority.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All priority restore successfully"}), 200


