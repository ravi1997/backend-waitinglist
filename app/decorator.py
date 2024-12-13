#decorator
from functools import wraps

from flask import jsonify, request

from app.models import Account, AccountRoles, Role, TokenList

def verify_user(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth_header = request.headers.get('Authorization')

		if auth_header and auth_header.startswith('Bearer '):
			token = auth_header.split(' ')[1]

		session = TokenList.query.filter_by(jwt=token).first()

		if session is None:
			return jsonify({"message":"Session expired."}),401

		current_account = Account.query.filter_by(id=session.account_id).first_or_404()

		if current_account.isDeleted():
			return jsonify({"message":"Account is DELETED"}),400

		if current_account.isBlocked():
			return jsonify({"message":"Account is BLOCKED"}),400
				
		if current_account.isNotVerified():
			return jsonify({"message":"Account is not ACTIVE"}),400
		
		account_roles = AccountRoles.query.filter_by(account_id = current_account.id)
		for account_role in account_roles:
			role = Role.query.filter_by(id=account_role.role_id).first()
			if role:
				if role.name == "SUPERADMIN" or role.name == "ADMIN":
					return jsonify({"message":"Account doesn't have USER role"}),400
		
		return f(current_account,*args, **kwargs)
	return decorated_function

def verify_token(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth_header = request.headers.get('Authorization')

		if auth_header and auth_header.startswith('Bearer '):
			token = auth_header.split(' ')[1]

		session = TokenList.query.filter_by(jwt=token).first()

		if session is None:
			return jsonify({"message":"Invalid user. Session not found"}),401

		return f(session,*args, **kwargs)
	return decorated_function
 
def verify_ADMIN(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth_header = request.headers.get('Authorization')

		if auth_header and auth_header.startswith('Bearer '):
			token = auth_header.split(' ')[1]

		session = TokenList.query.filter_by(jwt=token).first()

		if session is None:
			return jsonify({"message":"Invalid user. Session not found"}),401

		current_account = Account.query.filter_by(id=session.account_id).first_or_404()

		if current_account.isDeleted():
			return jsonify({"message":"Account is DELETED"}),400

		if current_account.isBlocked():
			return jsonify({"message":"Account is BLOCKED"}),400
				
		if current_account.isNotVerified():
			return jsonify({"message":"Account is not ACTIVE"}),400

		account_roles = AccountRoles.query.filter_by(account_id = current_account.id)
		for account_role in account_roles:
			role = Role.query.filter_by(id=account_role.role_id)
			if role:
				if role.name == "ADMIN":
					return f(*args, **kwargs)
			
		return jsonify({"message":"Account is not ADMIN"}),403
	return decorated_function

def verify_SUPERADMIN(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth_header = request.headers.get('Authorization')

		if auth_header and auth_header.startswith('Bearer '):
			token = auth_header.split(' ')[1]

		session = TokenList.query.filter_by(jwt=token).first()

		if session is None:
			return jsonify({"message":"Invalid user. Session not found"}),401

		current_account = Account.query.filter_by(id=session.account_id).first_or_404()

		if current_account.isDeleted():
			return jsonify({"message":"Account is DELETED"}),400

		if current_account.isBlocked():
			return jsonify({"message":"Account is BLOCKED"}),400
				
		if current_account.isNotVerified():
			return jsonify({"message":"Account is not ACTIVE"}),400

		account_roles = AccountRoles.query.filter_by(account_id = current_account.id)
		for account_role in account_roles:
			role = Role.query.filter_by(id=account_role.role_id).first()
			if role:
				if role.name == "SUPERADMIN":
					return f(*args, **kwargs)
			
		return jsonify({"message":"Account is not SUPERADMIN"}),403
	return decorated_function

def verify_SUPERADMIN_or_ADMIN(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth_header = request.headers.get('Authorization')

		if auth_header and auth_header.startswith('Bearer '):
			token = auth_header.split(' ')[1]

		session = TokenList.query.filter_by(jwt=token).first()

		if session is None:
			return jsonify({"message":"Invalid user. Session not found"}),401

		current_account = Account.query.filter_by(id=session.account_id).first_or_404()

		if current_account.isDeleted():
			return jsonify({"message":"Account is DELETED"}),400

		if current_account.isBlocked():
			return jsonify({"message":"Account is BLOCKED"}),400
				
		if current_account.isNotVerified():
			return jsonify({"message":"Account is not ACTIVE"}),400

		account_roles = AccountRoles.query.filter_by(account_id = current_account.id)
		for account_role in account_roles:
			role = Role.query.filter_by(id=account_role.role_id).first()
			if role:
				if role.name == "SUPERADMIN" or role.name == "ADMIN":
					return f(*args, **kwargs)
			
		return jsonify({"message":"Account is not SUPERADMIN or ADMIN"}),403
	return decorated_function

def get_role(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth_header = request.headers.get('Authorization')

		if auth_header and auth_header.startswith('Bearer '):
			token = auth_header.split(' ')[1]

		session = TokenList.query.filter_by(jwt=token).first()

		if session is None:
			return jsonify({"message":"Invalid user. Session not found"}),401

		current_account = Account.query.filter_by(id=session.account_id).first_or_404()

		if current_account.isDeleted():
			return jsonify({"message":"Account is DELETED"}),400

		if current_account.isBlocked():
			return jsonify({"message":"Account is BLOCKED"}),400
				
		if current_account.isNotVerified():
			return jsonify({"message":"Account is not ACTIVE"}),400

		account_roles = AccountRoles.query.filter_by(account_id = current_account.id)
		role_str = "USER"
		for account_role in account_roles:
			role = Role.query.filter_by(id=account_role.role_id).first()
			if role:
				if role.name == "SUPERADMIN":
					role_str = "SUPERADMIN"
				elif role.name == "ADMIN":
					role_str = "ADMIN"

		return f(role_str,*args, **kwargs)
	return decorated_function

def verify_body(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		request_data = request.json
		
		if request_data is None:
			return jsonify({"message":"Invalid request data format"}),400
		
		return f(request_data,*args, **kwargs)
	return decorated_function

