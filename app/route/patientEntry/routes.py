from datetime import datetime
from flask import jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import verify_body, verify_user
from app.models import EUA, Anesthesia, Cadre, Daycare, Diagnosis, Eye, PatientDemographic, PatientEntry, Plan, Priority, Short, User
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
			patientEntries = PatientEntry.query.filter(PatientEntry.user_id==current_user.user_id,PatientEntry.deleted==0,PatientEntry.finalDate >= today).all()
		else:
			patientEntries = PatientEntry.query.filter(PatientEntry.user_id==user.parent_id,PatientEntry.deleted==0,func.date(PatientEntry.finalDate) >= today).all()
		peJsons = schema.dump(patientEntries)
		patients = []
  
		for peJson in peJsons:
			pe = {}
			if 'patientdemographic_id' in peJson:
				patientDemographic = PatientDemographic.query.filter_by(id=peJson['patientdemographic_id']).first()
				if patientDemographic is not None:
					pe["patientDemographic"]=pdschema.dump(patientDemographic)

			if 'diagnosis_id' in peJson and peJson['diagnosis_id'] is not None:
				diagnosis = Diagnosis.query.filter_by(id=peJson['diagnosis_id']).first()
				if diagnosis is not None:
					pe["diagnosis"]=diagnosis.value
	
			if 'plan_id' in peJson and peJson['plan_id'] is not None:
				plan = Plan.query.filter_by(id=peJson['plan_id']).first()
				if plan is not None:
					pe["plan"]=plan.value
			
			if 'eye_id' in peJson and peJson['eye_id'] is not None:
				eye = Eye.query.filter_by(id=peJson['eye_id']).first()
				if eye is not None:
					pe["eye"]=eye.value
			
			if 'priority_id' in peJson and peJson['priority_id'] is not None:
				priority = Priority.query.filter_by(id=peJson['priority_id']).first()
				if priority is not None:
					pe["priority"]=priority.value

			if 'anesthesia_id' in peJson and peJson['anesthesia_id'] is not None:
				anesthesia = Anesthesia.query.filter_by(id=peJson['anesthesia_id']).first()
				if anesthesia is not None:
					pe["anesthesia"]=anesthesia.value

			if 'eua_id' in peJson and peJson['eua_id'] is not None:
				eua = EUA.query.filter_by(id=peJson['eua_id']).first()
				if eua is not None:
					pe["eua"]=eua.value
			
			if 'short_id' in peJson and peJson['short_id'] is not None:
				short = Short.query.filter_by(id=peJson['short_id']).first()
				if short is not None:
					pe["short"]=short.value

			if 'daycare_id' in peJson and peJson['daycare_id'] is not None:
				daycare = Daycare.query.filter_by(id=peJson['daycare_id']).first()
				if daycare is not None:
					pe["daycare"]=daycare.value


			if 'cabin_id' in peJson and peJson['cabin_id'] is not None:
				cabin = User.query.filter_by(id=peJson['cabin_id']).first()
				if cabin is not None:
					pe["cabin_id"]=peJson["cabin_id"]
					pe["cabin"] = f"{cabin.firstname} {cabin.middlename} {cabin.lastname}"
					
			if 'adviceBy_id' in peJson and peJson['adviceBy_id'] is not None:
				advice = User.query.filter_by(id=peJson['adviceBy_id']).first()
				if advice is not None:
					pe["adviceBy_id"]=peJson["adviceBy_id"]
					pe["adviceBy"] = f"{advice.firstname} {advice.middlename} {advice.lastname}"
					
			pe["id"]=peJson["id"]
			pe["initialDate"]=peJson["initialDate"]
			pe["finalDate"]=peJson["finalDate"]
			pe["user_id"]=peJson["user_id"]
			pe["remark"]=peJson["remark"]
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