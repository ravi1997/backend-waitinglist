from sqlalchemy import DateTime
from app.extension import db,bcrypt
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.types import DateTime

from app.util import generate_random_dob, generate_random_phone_number, randomword
# MODELS
# ABSTRACT MODELS

class BaseAttributes(db.Model):
	__abstract__ = True

	deleted = db.Column(db.Integer, server_default="0")
	deleted_date = db.Column(
		DateTime, server_default=func.now()
	)
	deleted_by = db.Column(db.Integer,nullable=True)

	created_date = db.Column(
		DateTime, server_default=func.now()
	)
	created_by = db.Column(db.Integer, server_default="0")

	updated_date = db.Column(
		DateTime, server_default=func.now()
	)
	updated_by = db.Column(db.Integer,nullable=False, server_default="0")

	def __init__(self) :
		self.deleted = 0

	def isDeleted(self):
		return self.deleted == 1

	def set_created(self, account_id):
		self.created_by = account_id
		self.created_date = datetime.now()

	def set_updated(self, account_id):
		self.updated_by = account_id
		self.updated_date = datetime.now()

	def set_deleted(self, account_id):
		if self.deleted == 1:
			raise ValueError("Object is already deleted.")
		
		self.deleted = 1
		self.deleted_by = account_id
		self.deleted_date = datetime.now()
	
	def set_restore(self):
		if self.deleted == 0:
			raise ValueError("Object is already restored.")
		
		self.deleted = 0

class StringValue(BaseAttributes):
	__abstract__ = True
	value = db.Column(db.String(30), unique=True, index=True,nullable=False)
	def __init__(self,value,derived):
		super().__init__()
		self.value = value.upper()
		self.derived = derived

	def __repr__(self):
		return f"<{self.derived.__name__}(id={self.id}, value='{self.value}')>"

# STRING MODELS

class Diagnosis(StringValue):
	__tablename__ = "diagnosises"
	id = db.Column(db.Integer,primary_key=True)
	
	def __init__(self, value):
		super().__init__(value,self.__class__)

class Plan(StringValue):
	__tablename__ = "plans"
	id = db.Column(db.Integer,primary_key=True)
	
	def __init__(self, value):
		super().__init__(value,self.__class__)

class Eye(StringValue):
	__tablename__ = "eyes"
	id = db.Column(db.Integer,primary_key=True)
	
	def __init__(self, value):
		super().__init__(value,self.__class__)

class Priority(StringValue):
	__tablename__ = "priorities"
	id = db.Column(db.Integer,primary_key=True)
	
	def __init__(self, value):
		super().__init__(value,self.__class__)

class Anesthesia(StringValue):
	__tablename__ = "anesthesias"
	id = db.Column(db.Integer,primary_key=True)
	
	def __init__(self, value):
		super().__init__(value,self.__class__)

class EUA(StringValue):
	__tablename__ = "euas"
	id = db.Column(db.Integer,primary_key=True)
	
	def __init__(self, value):
		super().__init__(value,self.__class__)

class Short(StringValue):
	__tablename__ = "shorts"
	id = db.Column(db.Integer,primary_key=True)
	
	def __init__(self, value):
		super().__init__(value,self.__class__)

# MAIN MODELS
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    pathname = db.Column(db.String(500), nullable=False)
    lineno = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class PatientDemographic(db.Model):
	__tablename__ = 'patient_demographics'
	id = db.Column(db.Integer, primary_key=True)
	fname = db.Column(db.String(100))
	mname = db.Column(db.String(100))
	lname = db.Column(db.String(100))
	dob   = db.Column(DateTime, server_default=func.now())
	gender = db.Column(db.String(10))
	phoneNo = db.Column(db.String(12))
	phoneNo1 = db.Column(db.String(12),nullable=True)
	uhid = db.Column(db.String(30), unique=True,nullable=False)
	
	def __init__(self, fname, mname, lname, gender, phoneNo, uhid, dob,phoneNo1 = None):
		self.fname = fname
		self.mname = mname
		self.lname = lname
		self.gender = gender
		self.phoneNo = phoneNo
		self.phoneNo1 = phoneNo1
		self.uhid = uhid
		self.dob = dob

	def __repr__(self):
		return f"<PatientDemographic(fname='{self.fname}', lname='{self.lname}', uhid='{self.uhid}')>"

	@classmethod
	def get_object(cls):
		return cls(
			fname = randomword(10),
			mname = randomword(10),
			lname = randomword(10),
			gender = "MALE",
			phoneNo = generate_random_phone_number(),
			uhid = randomword(10),
			dob = generate_random_dob()
		)

class TokenList(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	jwt = db.Column(db.String(64), unique=True, index=True)
	account_id = db.Column(db.Integer, index=True)
	create_date = db.Column(DateTime, server_default=func.now())

	def __init__(self, jwt, account_id):
		self.jwt = jwt
		self.account_id = account_id

class PatientEntry(BaseAttributes):
	__tablename__ = 'patient_entries'
	id = db.Column(db.Integer, primary_key=True)
	patientdemographic_id = db.Column(db.Integer, nullable = False)
	diagnosis_id = db.Column(db.Integer, nullable = False)
	plan_id = db.Column(db.Integer, nullable = False)
	eye_id = db.Column(db.Integer, nullable = False)
	priority_id = db.Column(db.Integer, nullable = False)
	anesthesia_id = db.Column(db.Integer, nullable = False)
	eua_id = db.Column(db.Integer, nullable = False)
	short_id = db.Column(db.Integer, nullable = False)
	cabin_id = db.Column(db.Integer, nullable = False)
	adviceBy_id = db.Column(db.Integer, nullable = False)
	initialDate = db.Column(DateTime, server_default=func.now(), nullable = False)
	finalDate = db.Column(DateTime, server_default=func.now(), nullable = False)
	user_id = db.Column(db.Integer, nullable = False)
	ptSurgery = db.Column(db.String(10), nullable = False)
	remark = db.Column(db.String(255))

	def __init__(self, patientdemographic_id, diagnosis_id, plan_id, eye_id, priority_id, anesthesia_id,
				 cabin_id, adviceBy_id, eua_id, short_id,user_id,ptSurgery, remark=None,initialDate = None,finalDate = None):
		self.patientdemographic_id = patientdemographic_id
		self.diagnosis_id = diagnosis_id
		self.plan_id = plan_id
		self.eye_id = eye_id
		self.priority_id = priority_id
		self.anesthesia_id = anesthesia_id
		self.cabin_id = cabin_id
		self.adviceBy_id = adviceBy_id
		self.eua_id = eua_id
		self.short_id = short_id
		self.remark = remark
		self.user_id = user_id
		if initialDate is not None:
			self.initialDate = initialDate
		if finalDate is not None:
			self.finalDate = finalDate
		self.ptSurgery = ptSurgery

	def __repr__(self):
		return f"<PatientEntry(id={self.id}, patientdemographic={self.patientdemographic_id}, diagnosis={self.diagnosis_id}, plan={self.plan_id})>"

class Building(BaseAttributes):
	__tablename__ = "buildings"
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30), unique=True, index=True,nullable=False)
	abbr = db.Column(db.String(10), unique=True, index=True,nullable=True)
	centre_id = db.Column(db.Integer, nullable=True)
	block_id = db.Column(db.Integer, nullable=True)

	def __init__(self, name, abbr = None, centre_id=None, block_id=None):
		self.name = name.upper()
		if abbr is not None:
			self.abbr = abbr.upper()
		self.centre_id = centre_id
		self.block_id = block_id

	def __repr__(self):
		return f'Building({self.id}, {self.name}, {self.abbr})'

class Floor(BaseAttributes):
	__tablename__ = "floors"
	id = db.Column(db.Integer,primary_key=True)
	number = db.Column(db.Integer, unique=True, index=True,nullable=False)
	name = db.Column(db.String(30), nullable=True, index=True)
	abbr = db.Column(db.String(10), nullable=True, index=True)

	def __init__(self, number, name=None, abbr=None):
		self.number = number
		if name is not None:
			self.name = name.upper()
		if abbr is not None:
			self.abbr = abbr.upper()
		
	def __repr__(self):
		return f'Floor({self.id}, {self.number}, {self.name})'

class Room(BaseAttributes):
	__tablename__ = "rooms"
	id = db.Column(db.Integer,primary_key=True)
	number = db.Column(db.Integer, unique=True, index=True)
	name = db.Column(db.String(30), nullable=True, index=True)
	abbr = db.Column(db.String(10), nullable=True, index=True)

	def __init__(self, number, name=None, abbr=None):
		self.number = number
		if name is not None:
			self.name = name.upper()
		if abbr is not None:
			self.abbr = abbr.upper()
		
	def __repr__(self):
		return f'Room({self.id}, {self.number}, {self.name})'

class Account(BaseAttributes):
	__tablename__ = "accounts"
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(30), unique=True, index=True, nullable = False)
	password= db.Column(db.String(120), nullable = False)

	verified_by = db.Column(db.Integer, nullable=True)
	verified_date = db.Column(
		DateTime, server_default=func.now()
	)
	status = db.Column(db.Integer, server_default="0")
	user_id = db.Column(db.Integer, nullable = False,index=True)
	wrongAttempt = db.Column(db.Integer, server_default="0")

	def __init__(self, username, password, user_id = None, verified_by=None, status=0, wrongAttempt=0):
		self.username = username
		self.password = password
		self.verified_by = verified_by
		self.status = status
		self.user_id = user_id
		self.wrongAttempt = wrongAttempt

	def __repr__(self):
		return f'Account(ID: {self.id}, Name: "{self.username}", Password : "{self.password}" )'

	def check_password(self, password):
		return bcrypt.check_password_hash(self.password, password)

	def isVerified(self):
		return self.status == 1

	def verify(self,verified_by):
		self.status = 1
		self.verified_by = verified_by
		self.verified_date = datetime.now()

	def isNotVerified(self):
		return self.status == 0

	def isBlocked(self):
		return self.status == 2

	def blockAccount(self):
		self.status = 2

class Role(BaseAttributes):
	__tablename__ = "roles"
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30), index=True,nullable=False)

	def __init__(self, name):
		self.name = name.upper()

	def __repr__(self):
		return f'Role({self.id}, "{self.name}")'

class Department(BaseAttributes):
	__tablename__ = "departments"
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(50), unique=True, index=True,nullable=False)
	abbr = db.Column(db.String(30), nullable=True, index=True)

	def __init__(self, name, abbr=None):
		self.name = name.upper()
		if abbr is not None:
			self.abbr = abbr.upper()
		
	def __repr__(self):
		return f'Department({self.id}, "{self.name}")'

class Unit(BaseAttributes):
	__tablename__ = "units"
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30), unique=True, index=True,nullable=False)
	abbr = db.Column(db.String(10), nullable=True, index=True)

	def __init__(self, name, abbr=None):
		self.name = name.upper()
		if abbr is not None:
			self.abbr = abbr.upper()

	def __repr__(self):
		return (
			f"UNIT: (id = {self.id}, name = {self.name}, abbr = {self.abbr}"
		)

class Designation(BaseAttributes):
	__tablename__ = "designations"
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30), unique=True, index=True,nullable=False)
	abbr = db.Column(db.String(10), nullable=True, index=True)
	cadre_id = db.Column(db.Integer,index = True,nullable=False)

	def __init__(self, name, cadre_id, abbr=None):
		self.name = name.upper()
		if abbr is not None:
			self.abbr = abbr.upper()
		self.cadre_id = cadre_id

	def __repr__(self):
		return (
			f'DESIGNATION: (id = {self.id}, name = "{self.name}"'
		)

class Cadre(BaseAttributes):
	__tablename__ = "cadres"
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30), unique=True, index=True,nullable=False)
	abbr = db.Column(db.String(10), nullable=True, index=True)

	def __init__(self, name, abbr=None):
		self.name = name.upper()
		if abbr is not None:
			self.abbr = abbr.upper()

	def __repr__(self):
		return f'CADRE: ({self.id}, "{self.name}")'

class User(BaseAttributes):
	__tablename__ = "users"
	id = db.Column(db.Integer,primary_key=True)
	firstname = db.Column(db.String(30), index=True,nullable=False)
	middlename = db.Column(db.String(30), index=True,nullable=True)
	lastname = db.Column(db.String(30),  index=True,nullable=True)
	employee_id = db.Column(db.String(30), unique=True, index=True,nullable=False)
	email = db.Column(db.String(30), nullable = False)
	mobile = db.Column(db.String(30), nullable = False)
	email2 = db.Column(db.String(30),nullable=True)
	email3 = db.Column(db.String(30),nullable=True)
	mobile2 = db.Column(db.String(30),nullable=True)
	mobile3 = db.Column(db.String(30),nullable=True)
	officeAddress_id = db.Column(db.Integer, index=True, nullable = False)
	department_id = db.Column(db.Integer,  index=True, nullable = False)
	unit_id = db.Column(db.Integer, index=True, nullable = False)
	designation_id = db.Column(db.Integer, index=True, nullable = False)
	cadre_id = db.Column(db.Integer, index=True, nullable = False)
	status = db.Column(db.Integer, server_default="0")
	parent_id = db.Column(db.Integer, index=True, nullable = True)		
	parent_status = db.Column(db.Integer, server_default="0")

	verified_by = db.Column(db.Integer)
	verified_date = db.Column(
		DateTime, server_default=func.now()
	)

	def isVerified(self):
		return self.status == 1

	def isNotVerified(self):
		return self.status == 0

	def verify(self,verified_by):
		self.status = 1
		self.verified_by = verified_by
		self.verified_date = datetime.now()

	def __init__(self, firstname,employee_id, email, mobile, middlename = None, lastname = None, 
				 email2=None, email3=None, mobile2=None, mobile3=None, officeAddress_id=None,
				 department_id=None, unit_id=None, designation_id=None, cadre_id=None, status=0,
				 verified_by=None):
		self.firstname = firstname.upper()
		if middlename is not None:
			self.middlename = middlename.upper()
		if lastname is not None:
			self.lastname = lastname.upper()

		self.employee_id = employee_id
		self.email = email
		self.mobile = mobile
		self.email2 = email2
		self.email3 = email3
		self.mobile2 = mobile2
		self.mobile3 = mobile3
		self.officeAddress_id = officeAddress_id
		self.department_id = department_id
		self.unit_id = unit_id
		self.designation_id = designation_id
		self.cadre_id = cadre_id
		self.status = status
		self.verified_by = verified_by

	def __repr__(self):
		return f"USER: (id = {self.id}, fullname = {self.firstname}, employee_id = {self.employee_id}, " \
			   f"userCadre = {self.cadre_id}, userDepartment = {self.department_id})"

class Block(BaseAttributes):
	__tablename__ = "blocks"
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(50), unique=True, index=True,nullable=False)
	abbr = db.Column(db.String(30), nullable=True, index=True)

	def __init__(self, name, abbr=None):
		self.name = name.upper()
		if abbr is not None:
			self.abbr = abbr.upper()

	def __repr__(self):
		return f'Block({self.id}, "{self.name}")'

class Centre(BaseAttributes):
	__tablename__ = "centres"
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(50), unique=True, index=True,nullable=False)
	abbr = db.Column(db.String(30), nullable=True, index=True)

	def __init__(self, name, abbr=None):
		self.name = name.upper()
		if abbr is not None:
			self.abbr = abbr.upper()

	def __repr__(self):
		return f'Centre({self.id}, "{self.name}")'

# SUPPORT MODELS
class FloorRooms(db.Model):
	__tablename__ = "floor_rooms_table"
	floor_id = db.Column(db.Integer, primary_key=True)
	room_id = db.Column(db.Integer, primary_key=True)
	def __init__(self,floor_id,room_id):
		self.floor_id = floor_id
		self.room_id = room_id

class BuildingFloors(db.Model):
	__tablename__ = "building_floors_table"
	building_id = db.Column(db.Integer, primary_key=True)
	floor_id = db.Column(db.Integer, primary_key=True)
	def __init__(self,building_id,floor_id):
		self.building_id = building_id
		self.floor_id = floor_id

class AccountRoles(db.Model):
	__tablename__ = "account_roles_table"
	account_id = db.Column(db.Integer, primary_key=True)
	role_id = db.Column(db.Integer, primary_key=True)
	def __init__(self,account_id,role_id):
		self.account_id = account_id
		self.role_id = role_id

class DepartmentBlocks(db.Model):
	__tablename__ = "department_blocks_table"
	department_id = db.Column(db.Integer, primary_key=True)
	block_id = db.Column(db.Integer, primary_key=True)

class DepartmentUnits(db.Model):
	__tablename__ = "department_units_table"
	department_id = db.Column(db.Integer, primary_key=True)
	unit_id = db.Column(db.Integer, primary_key=True)
	def __init__(self,departmet_id,unit_id):
		self.department_id = departmet_id
		self.unit_id = unit_id

class DepartmentHead(db.Model):
	__tablename__ = "department_head_table"
	department_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, primary_key=True)

class UnitHead(db.Model):
	__tablename__ = "unit_head_table"
	unit_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, primary_key=True)

class BlockHead(db.Model):
	__tablename__ = "block_head_table"
	block_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, primary_key=True)

class CentreHead(db.Model):
	__tablename__ = "centre_head_table"
	centre_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, primary_key=True)

class BlockUsers(db.Model):
	__tablename__ = "block_users_table"
	block_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, primary_key=True)

class CentreUsers(db.Model):
	__tablename__ = "centre_users_table"
	centre_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, primary_key=True)

class BlockCentres(db.Model):
	__tablename__ = "block_centres_table"
	block_id = db.Column(db.Integer, primary_key=True)
	centre_id = db.Column(db.Integer, primary_key=True)

class DepartmentCentres(db.Model):
	__tablename__ = "department_centres_table"
	centre_id = db.Column(db.Integer, primary_key=True)
	department_id = db.Column(db.Integer, primary_key=True)

	def __init__(self,centre_id,department_id):
		self.centre_id = centre_id
		self.department_id = department_id
