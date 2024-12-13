from datetime import datetime
from pprint import pprint
from flask import jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import verify_body, verify_user
from app.models import EUA, Anesthesia, Cadre, Diagnosis, Eye, PatientDemographic, PatientEntry, Plan, Priority, Short, User
from app.extension import db

from flask import jsonify

from app.schema import  PatientDemographicSchema, PatientEntrySchema
from app.util import to_date
from . import patiententry_bp

@patiententry_bp.route('/')
def index():
	return 'This is The waiting list patient route'


# Create patient route
@patiententry_bp.route("/create", methods=["POST"])
@verify_user
@verify_body
def create_patient(request_data, user):
	patient_entry_schema = PatientEntrySchema()
	patientDemographic_schema = PatientDemographicSchema()
	try:
		errors = patient_entry_schema.validate(request_data['patient_entry'])
		if errors:
			return jsonify(errors), 400
		
		errors1 = patientDemographic_schema.validate(request_data['demographic'])
		if errors1:
			return jsonify(errors), 400

		patient_data = patient_entry_schema.load(request_data['patient_entry'])
		patientDemographic_data = patientDemographic_schema.load(request_data['demographic'])
		
		pd = PatientDemographic.query.filter_by(uhid = patientDemographic_data.uhid).first()
		if patientDemographic_data.phoneNo1 is not None:
			pd.phoneNo1 = patientDemographic_data.phoneNo1

		patient_data.set_created(user.id)
		db.session.add(patient_data)
		db.session.commit()
		return jsonify(message="Patient created successfully", patient=patient_entry_schema.dump(patient_data)), 200
	
	except ValidationError as err:
		return jsonify(err.messages), 400

@patiententry_bp.route("/update", methods=["PUT"])
@verify_user
@verify_body
def update_patient(request_data,user):	
	schema = PatientEntrySchema()

	try:
		patient = PatientEntry.query.filter_by(id = request_data['id']).one_or_none()
		if patient is None:
			return jsonify({'message': 'patient is not found.'}), 404
		if patient.isDeleted():
			return jsonify({"message": "patient is deleted."}),400

		patient.diagnosis_id = request_data['diagnosis_id']
		patient.plan_id = request_data['plan_id']
		patient.eye_id = request_data['eye_id']
		patient.priority_id = request_data['priority_id']
		patient.anesthesia_id = request_data['anesthesia_id']
		patient.cabin_id = request_data['cabin_id']
		patient.adviceBy_id = request_data['adviceBy_id']
		patient.eua_id = request_data['eua_id']
		patient.short_id = request_data['short_id']
		patient.remark = request_data['remark']

		patient.set_updated(user.id)
		db.session.commit()
		return jsonify(message="Successfull"),200

	except ValidationError as err:
		# Return a nice message if validation fails
		return jsonify(err.messages), 400



@patiententry_bp.route("/redate/<id>", methods=["PUT"])
@verify_user
@verify_body
def redate(request_data,user,id):
	schema = PatientEntrySchema()
	
	try:
		if id is not None:
			patient = PatientEntry.query.filter_by(id = id).one_or_none()
			if patient is None:
				return jsonify({'message': 'patient is not found.'}), 404
			if patient.isDeleted():
				return jsonify({"message": "patient is deleted."}),400
			patient.finalDate = to_date(request_data['date'])
			patient.set_updated(user.id)
			db.session.commit()
			return jsonify(message="Successfull",patient = schema.dump(patient)),200
		else:
			return jsonify({'message': 'patient id is not found.'}), 404
	except ValidationError as err:
		# Return a nice message if validation fails
		return jsonify(err.messages), 400

@patiententry_bp.route("/<id>", methods=["GET"])
@verify_user
def getPatient(account,id):

	schema = PatientEntrySchema()
	
	try:
		if id is not None:
			patient = PatientEntry.query.filter_by(id = id).one_or_none()
			if patient is None:
				return jsonify({'message': 'patient is not found.'}), 404
			if patient.isDeleted():
				return jsonify({"message": "patient is deleted."}),400
			return jsonify(message="Successfull",patient = schema.dump(patient)),200
		else:
			return jsonify({'message': 'patient id is not found.'}), 404
	except ValidationError as err:
		# Return a nice message if validation fails
		return jsonify(err.messages), 400



@patiententry_bp.route("/getAll", methods=["GET"])
@verify_user
def getAllPatient(current_user):
	schema = PatientEntrySchema(many=True)
	pdschema = PatientDemographicSchema()
	today = datetime.today().date()
	try:
		user = User.query.filter_by(id = current_user.user_id).first()
		cadre = Cadre.query.filter_by(id=user.cadre_id).first()
		if cadre.name == "DOCTOR":
			pprint(f"user id : {current_user.user_id}")
			patientEntries = PatientEntry.query.filter(PatientEntry.user_id==current_user.user_id,PatientEntry.deleted==0,PatientEntry.finalDate >= today).all()
		else:
			patientEntries = PatientEntry.query.filter(PatientEntry.user_id==user.parent_id,PatientEntry.deleted==0,func.date(PatientEntry.finalDate) >= today).all()
		peJsons = schema.dump(patientEntries)
		patients = []
		pprint(len(patientEntries))
  
		for peJson in peJsons:
			pprint(peJson)
			patientDemographic = PatientDemographic.query.filter_by(id=peJson['patientdemographic_id']).first()
			diagnosis = Diagnosis.query.filter_by(id=peJson['diagnosis_id']).first()
			plan = Plan.query.filter_by(id=peJson['plan_id']).first()
			eye = Eye.query.filter_by(id=peJson['eye_id']).first()
			priority = Priority.query.filter_by(id=peJson['priority_id']).first()
			anesthesia = Anesthesia.query.filter_by(id=peJson['anesthesia_id']).first()
			eua = EUA.query.filter_by(id=peJson['eua_id']).first()
			short = Short.query.filter_by(id=peJson['short_id']).first()
			cabin = User.query.filter_by(id=peJson['cabin_id']).first()
			advice = User.query.filter_by(id=peJson['adviceBy_id']).first()
			
			pe = {}
			pe["patientDemographic"]=pdschema.dump(patientDemographic)
			pe["diagnosis"]=diagnosis.value
			pe["plan"]=plan.value
			pe["eye"]=eye.value
			pe["priority"]=priority.value
			pe["anesthesia"]=anesthesia.value
			pe["eua"]=eua.value
			pe["short"]=short.value
			pe["id"]=peJson["id"]
			pe["cabin_id"]=peJson["cabin_id"]
			pe["adviceBy_id"]=peJson["adviceBy_id"]
			pe["initialDate"]=peJson["initialDate"]
			pe["finalDate"]=peJson["finalDate"]
			pe["user_id"]=peJson["user_id"]
			pe["remark"]=peJson["remark"]
			pe["adviceBy"] = f"{advice.firstname} {advice.middlename} {advice.lastname}"
			pe["cabin"] = f"{cabin.firstname} {cabin.middlename} {cabin.lastname}"
			pe["ptSurgery"] = peJson["ptSurgery"]
			patients.append(pe)
		return jsonify(message="Successfull",patients = patients),200
	except ValidationError as err:
		# Return a nice message if validation fails
		return jsonify(err.messages), 400



@patiententry_bp.route("/<id>", methods=["DELETE"])
@verify_user
def deletePatient(current_user,id):
	# Access the identity of the current user with get_jwt_identity
	if id is not None:		
		patient = PatientEntry.query.filter_by(id=id).one_or_none()

		if patient is None:
			return jsonify({'message': 'patient is not found.'}), 404
		if patient.deleted == 1:
			return jsonify({"message": "patient is already deleted."}),400
		patient.deleted = 1
		patient.deleted_by = current_user.id
		db.session.commit()
		return jsonify({"message":"Successfull"}),200
	else:
		return jsonify({'message': 'patient id is not found.'}), 404