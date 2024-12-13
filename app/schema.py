from app.extension import ma
from app.models import *
from marshmallow import fields

# SCHEMAS
class LoginAccoutSchema(ma.SQLAlchemySchema):
	class Meta:
		model = Account
		include_fk = True
		include_relationships = True
		load_instance = True
	
	username = fields.String(required=True)
	password = fields.String(required=True)

class AccountSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Account
		include_fk = True
		include_relationships = True
		load_instance = True
	
class UserSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = User
		include_fk = True
		include_relationships = True
		load_instance = True
	
class DiagnosisSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Diagnosis
		include_fk = True
		include_relationships = True
		load_instance = True

class PlanSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Plan
		include_fk = True
		include_relationships = True
		load_instance = True

class EyeSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Eye
		include_fk = True
		include_relationships = True
		load_instance = True

class PrioritySchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Priority
		include_fk = True
		include_relationships = True
		load_instance = True

class AnesthesiaSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Anesthesia
		include_fk = True
		include_relationships = True
		load_instance = True

class EUASchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = EUA
		include_fk = True
		include_relationships = True
		load_instance = True

class ShortSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Short
		include_fk = True
		include_relationships = True
		load_instance = True

class PatientDemographicSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = PatientDemographic
		include_fk = True
		include_relationships = True
		load_instance = True

class PatientEntrySchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = PatientEntry
		include_fk = True
		include_relationships = True
		load_instance = True

class BuildingSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Building
		include_fk = True
		include_relationships = True
		load_instance = True

class FloorSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Floor
		include_fk = True
		include_relationships = True
		load_instance = True

class RoomSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Room
		include_fk = True
		include_relationships = True
		load_instance = True

class RoleSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Role
		include_fk = True
		include_relationships = True
		load_instance = True

class DepartmentSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Department
		include_fk = True
		include_relationships = True
		load_instance = True

class UnitSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Unit
		include_fk = True
		include_relationships = True
		load_instance = True

class DesignationSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Designation
		include_fk = True
		include_relationships = True
		load_instance = True

class CadreSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Cadre
		include_fk = True
		include_relationships = True
		load_instance = True

class BlockSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Block
		include_fk = True
		include_relationships = True
		load_instance = True

class CentreSchema(ma.SQLAlchemyAutoSchema):
	class Meta:
		model = Centre
		include_fk = True
		include_relationships = True
		load_instance = True

