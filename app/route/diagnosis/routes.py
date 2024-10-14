from flask import jsonify,current_app
from marshmallow import ValidationError

from app.decorator import verify_SUPERADMIN, verify_body, verify_token, verify_user
from app.models import Diagnosis
from app.extension import db

from flask import jsonify

from app.schema import DiagnosisSchema
from . import diagnosis_bp

@diagnosis_bp.route("/")
def index_diagnosis():
    return "This is The waiting list diagnosis route"


@diagnosis_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_diagnosis(request_data, session):
    try:
        schema = DiagnosisSchema()
        errors = schema.validate(request_data)
        if errors:
            return jsonify({"message":errors}),400
        diagnosis_data = schema.load(request_data)
        diagnosis_name = diagnosis_data.value

        existing_diagnosis = Diagnosis.query.filter_by(value=diagnosis_name).first()
        if existing_diagnosis:
            jsonify({"message":f"Diagnosis '{diagnosis_name}' already exists"}),400

        diagnosis_data.set_created(session.account_id)
        db.session.add(diagnosis_data)
        db.session.commit()

        current_app.logger.info(f"Diagnosis created: {diagnosis_name}")
        return jsonify({"message": f"Diagnosis created: {diagnosis_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating diagnosis: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@diagnosis_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_diagnosis(request_data, session):
    """
    Route to create a new diagnosis.

    Only SUPERADMIN users can create a diagnosis.
    """
    try:
        schema = DiagnosisSchema(many=True)
        errors = schema.validate(request_data)
        if errors:
            return jsonify({"message":errors}),400

        diagnosiss_data = schema.load(request_data)

        for diagnosis_data in diagnosiss_data:
            diagnosis_name = diagnosis_data.value

            existing_diagnosis = Diagnosis.query.filter_by(value=diagnosis_name).first()
            if existing_diagnosis:
                current_app.logger.info(f"Diagnosis '{diagnosis_name}' already exists")
                continue
            try:
                diagnosis_data.set_created(session.account_id)

                db.session.add(diagnosis_data)
                db.session.commit()
                current_app.logger.info(f"Diagnosis created: {diagnosis_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating diagnosis: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All diagnosis created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating diagnosis: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@diagnosis_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_diagnosiss():
    """
    Route to get all diagnosiss.
    """
    try:
        schema = DiagnosisSchema(many=True)
        diagnosiss = Diagnosis.query.all()
        return schema.jsonify(diagnosiss), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@diagnosis_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_diagnosiss():
    """
    Route to get all inactive diagnosiss.
    """
    try:
        schema = DiagnosisSchema(many=True)
        diagnosiss = Diagnosis.query.filter_by(deleted=1).all()
        return schema.jsonify(diagnosiss), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@diagnosis_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_diagnosiss(account):
    """
    Route to get all active diagnosiss.
    """
    try:
        schema = DiagnosisSchema(many=True)
        diagnosiss = Diagnosis.query.filter_by(deleted=0).all()
        return schema.jsonify(diagnosiss), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@diagnosis_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_diagnosis(id):
    """
    Route to get a specific diagnosis by ID.
    """
    schema = DiagnosisSchema()
    diagnosis = Diagnosis.query.filter_by(id=id).first_or_404()
    return schema.jsonify(diagnosis), 200


@diagnosis_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_diagnosis(value):
    """
    Route to get a specific diagnosis by value.
    """
    schema = DiagnosisSchema()
    diagnosis = Diagnosis.query.filter_by(value=value).first_or_404()

    return schema.jsonify(diagnosis), 200


@diagnosis_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_diagnosis(request_data, session):
    """
    Route to update a diagnosis.

    Only ADMIN users can update a diagnosis.
    """
    schema = DiagnosisSchema()

    try:
        diagnosis_data = schema.load(request_data)
        diagnosis = Diagnosis.query.get(diagnosis_data.id)
        if not diagnosis:
            return jsonify({"message":f"Diagnosis {diagnosis_data.id} not found"}),404

        diagnosis.value = diagnosis_data.value  # Update other fields as needed

        diagnosis.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Diagnosis updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Diagnosis: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@diagnosis_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_diagnosis(session, id):
    """
    Route to delete a single diagnosis by ID.

    Only ADMIN users can delete a diagnosis.
    """
    diagnosis = Diagnosis.query.filter_by(id=id).first_or_404()
    if diagnosis.isDeleted():
        return jsonify({"message":f"Diagnosis {id} is already deleted"}),400

    diagnosis.set_deleted(session.account_id)
    diagnosis.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "Diagnosis deleted successfully"}), 200


@diagnosis_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_diagnosiss(session):
    """
    Route to delete all diagnosiss.

    Only ADMIN users can delete all diagnosiss.
    """
    diagnosiss = Diagnosis.query.all()
    for diagnosis in diagnosiss:
        diagnosis.set_deleted(session.account_id)
        diagnosis.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All diagnosiss deleted successfully"}), 200


@diagnosis_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_diagnosis(session, id):
    """
    Route to restore a single diagnosis by ID.

    Only ADMIN users can restore a diagnosis.
    """
    diagnosis = Diagnosis.query.filter_by(id=id).first_or_404()

    if diagnosis.isDeleted():
        diagnosis.set_restore(session.account_id)
        diagnosis.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "Diagnosis restore successfully"}), 200
    else:
        return jsonify({"message": "Diagnosis is already restored"}), 400


@diagnosis_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_diagnosis(session):
    """
    Route to restore all diagnosis.

    Only ADMIN users can restore all diagnosis.
    """
    diagnosis = Diagnosis.query.all()
    for diagnosis in diagnosis:
        if diagnosis.isDeleted():
            diagnosis.set_restore(session.account_id)
            diagnosis.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All diagnosis restore successfully"}), 200


