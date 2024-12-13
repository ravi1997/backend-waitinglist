import traceback
from flask import jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import get_role, verify_SUPERADMIN, verify_SUPERADMIN_or_ADMIN, verify_body, verify_token
from app.models import Account, Department, User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import DepartmentSchema, UserSchema
from . import department_bp

@department_bp.route("/")
def index():
    return "This is The waiting list department route"


@department_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_department(request_data, session):
    try:
        schema = DepartmentSchema()
        errors = schema.validate(request_data)
        if errors:
            return jsonify({"message":errors}),400
        
        department_data = schema.load(request_data)
        department_name = department_data.name.upper()
        if department_data.abbr is not None:
            department_abbr = department_data.abbr.upper()
            department_data.abbr = department_abbr

        department_data.name = department_name

        existing_department = Department.query.filter_by(name=department_name).first()
        if existing_department:
            return jsonify({"message":f"Department '{department_name}' already exists"}),400

        department_data.set_created(session.account_id)
        db.session.add(department_data)
        db.session.commit()

        current_app.logger.info(f"Department created: {department_name}")
        return jsonify({"message": f"Department created: {department_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        current_app.logger.error(f"Error creating department: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@department_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_department(request_data, session):
    """
    Route to create a new department.

    Only SUPERADMIN users can create a department.
    """
    try:
        schema = DepartmentSchema(many=True)
        departments_data = schema.load(request_data)

        for department_data in departments_data:
            department_name = department_data.name.upper()
            if department_data.abbr is not None:
                department_abbr = department_data.abbr.upper()
                department_data.abbr = department_abbr

            department_data.name = department_name

            existing_department = Department.query.filter_by(name=department_name).first()
            if existing_department:
                return jsonify({"message":f"Department '{department_name}' already exists"}),400

            department_data.set_created(session.account_id)

            try:

                db.session.add(department_data)
                db.session.commit()
                current_app.logger.info(f"Department created: {department_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating department: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All department created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating department: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@department_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_departments():
    """
    Route to get all departments.
    """
    try:
        schema = DepartmentSchema(many=True)
        departments = Department.query.all()
        return schema.jsonify(departments), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@department_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_departments():
    """
    Route to get all inactive departments.
    """
    try:
        schema = DepartmentSchema(many=True)
        departments = Department.query.filter_by(deleted=1).all()
        return schema.jsonify(departments), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@department_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_department(id):
    """
    Route to get a specific department by ID.
    """
    schema = DepartmentSchema()
    department = Department.query.filter_by(id=id).first_or_404()
    return schema.jsonify(department), 200


@department_bp.route("/get/<name>", methods=["GET"])
@verify_SUPERADMIN
def get_by_name_department(name):
    """
    Route to get a specific department by name.
    """
    schema = DepartmentSchema()
    department = Department.query.filter_by(name=name).first()
    if department:
        return schema.jsonify(department), 200
    department = Department.query.filter_by(abbr=name).first_or_404()
    return schema.jsonify(department), 200


@department_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_department(request_data, session):
    """
    Route to update a department.

    Only ADMIN users can update a department.
    """
    schema = DepartmentSchema()

    try:
        department_data = schema.load(request_data)
        department = Department.query.get(department_data.id)
        if not department:
            return jsonify({"message": "Department not found"}), 404

        department = department_data  # Update other fields as needed

        department.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Department updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.messages}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Department: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@department_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_department(session, id):
    """
    Route to delete a single department by ID.

    Only ADMIN users can delete a department.
    """
    department = Department.query.filter_by(id=id).first_or_404()
    if department.isDeleted():
        return jsonify({"message": "Department is already deleted"}), 400

    department.set_deleted(session.account_id)

    db.session.commit()

    return jsonify({"message": "Department deleted successfully"}), 200


@department_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_departments(session):
    """
    Route to delete all departments.

    Only ADMIN users can delete all departments.
    """
    departments = Department.query.all()
    for department in departments:
        if department.isDeleted():
            return jsonify({"message": "Department is already deleted"}), 400

        department.set_deleted(session.account_id)

    db.session.commit()

    return jsonify({"message": "All departments deleted successfully"}), 200


@department_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_department(session, id):
    """
    Route to restore a single department by ID.

    Only ADMIN users can restore a department.
    """
    department = Department.query.filter_by(id=id).first_or_404()

    if department.isDeleted():
        department.set_restore(session.account_id)
        db.session.commit()
        return jsonify({"message": "Department restore successfully"}), 200
    else:
        return jsonify({"message": "Department is already restored"}), 400


@department_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_department(session):
    """
    Route to restore all department.

    Only ADMIN users can restore all department.
    """
    department = Department.query.all()
    for department in department:
        if department.isDeleted():
            department.set_restore(session.account_id)
        else:
            return jsonify({"message": "Department is already restored"}), 400

    db.session.commit()

    return jsonify({"message": "All department restore successfully"}), 200
