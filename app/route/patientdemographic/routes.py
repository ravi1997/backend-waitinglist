from datetime import datetime
from app.util import send_ehospital_uhid
from flask import jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import verify_user
from app.models import PatientDemographic, PatientEntry, User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import  PatientDemographicSchema
from . import patientdemographic_bp



@patientdemographic_bp.route('/')
def index():
	return 'This is The waiting list patient demographic route'

# Create patient route
@patientdemographic_bp.route("/fetch/<uhid>", methods=["GET"])
@verify_user
def create_patient(user,uhid):
	
	schema = PatientDemographicSchema()
	
	patientdemographic = PatientDemographic.query.filter_by(uhid = uhid).one_or_none()
	if patientdemographic is None:
		patientDetails = send_ehospital_uhid(uhid)
		if patientDetails is None:
			return jsonify({"message":"UHID not found "}),404
		
		obj = PatientDemographic(
			uhid=uhid,
			fname=patientDetails["p_fname"],
			mname=patientDetails["p_mname"],
			lname=patientDetails["p_lname"],
			gender=patientDetails["gender"],
			phoneNo=patientDetails["mobile_no"],
			phoneNo1="",
			dob=datetime.strptime(patientDetails["dob"], "%Y-%m-%d")
		)
		db.session.add(obj)
		db.session.commit()
		return jsonify(schema.dump(obj)), 200
	else:
		return jsonify(schema.dump(patientdemographic)), 200

