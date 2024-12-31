from flask import abort, jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import func

from app.decorator import get_role, verify_SUPERADMIN, verify_SUPERADMIN_or_ADMIN, verify_body, verify_token, verify_user
from app.models import Account, Plan, User
from app.extension import db,bcrypt

from flask import jsonify

from app.schema import PlanSchema, UserSchema
from . import plan_bp

@plan_bp.route("/")
def index_plan():
    return "This is The waiting list plan route"


@plan_bp.route("/create", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_plan(request_data, session):
    try:
        schema = PlanSchema()
        plan_data = schema.load(request_data)
        plan_name = plan_data.value

        existing_plan = Plan.query.filter_by(value=plan_name).first()
        if existing_plan:
            jsonify({"message":f"Plan '{plan_name}' already exists"}),400

        plan_data.set_created(session.account_id)
        db.session.add(plan_data)
        db.session.commit()

        current_app.logger.info(f"Plan created: {plan_name}")
        return jsonify({"message": f"Plan created: {plan_name}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating plan: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@plan_bp.route("/createAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
@verify_body
def create_all_plan(request_data, session):
    """
    Route to create a new plan.

    Only SUPERADMIN users can create a plan.
    """
    try:
        schema = PlanSchema(many=True)
        plans_data = schema.load(request_data)

        for plan_data in plans_data:
            plan_name = plan_data.value

            existing_plan = Plan.query.filter_by(value=plan_name).first()
            if existing_plan:
                current_app.logger.info(f"Plan '{plan_name}' already exists")
                continue
            try:
                plan_data.set_created(session.account_id)

                db.session.add(plan_data)
                db.session.commit()
                current_app.logger.info(f"Plan created: {plan_name}")
            except Exception as e:
                current_app.logger.error(f"Error creating plan: {str(e)}")
                return jsonify({"message":f"Internal Server Error"}),500

        return jsonify({"message": "All plan created successfully"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error creating plan: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@plan_bp.route("/getAll", methods=["GET"])
@verify_SUPERADMIN
def get_all_plans():
    """
    Route to get all plans.
    """
    try:
        schema = PlanSchema(many=True)
        plans = Plan.query.all()
        return schema.jsonify(plans), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@plan_bp.route("/getAlldeleted", methods=["GET"])
@verify_SUPERADMIN
def get_all_inactive_plans():
    """
    Route to get all inactive plans.
    """
    try:
        schema = PlanSchema(many=True)
        plans = Plan.query.filter_by(deleted=1).all()
        return schema.jsonify(plans), 200

    except Exception as e:
                return jsonify({"message":str(e)}),500


@plan_bp.route("/getAllNondeleted", methods=["GET"])
@verify_user
def get_all_active_plans(account):
    """
    Route to get all active plans.
    """
    try:
        schema = PlanSchema(many=True)
        plans = Plan.query.filter_by(deleted=0).all()
        return schema.jsonify(plans), 200
    except Exception as e:
                return jsonify({"message":str(e)}),500


@plan_bp.route("/get/<id>", methods=["GET"])
@verify_SUPERADMIN
def get_plan(id):
    """
    Route to get a specific plan by ID.
    """
    schema = PlanSchema()
    plan = Plan.query.filter_by(id=id).first_or_404()
    return schema.jsonify(plan), 200


@plan_bp.route("/get/<value>", methods=["GET"])
@verify_SUPERADMIN
def get_by_value_plan(value):
    """
    Route to get a specific plan by value.
    """
    schema = PlanSchema()
    plan = Plan.query.filter_by(value=value).first_or_404()

    return schema.jsonify(plan), 200


@plan_bp.route("/update", methods=["PUT"])
@verify_SUPERADMIN
@verify_token
@verify_body
def update_plan(request_data, session):
    """
    Route to update a plan.

    Only ADMIN users can update a plan.
    """
    schema = PlanSchema()

    try:
        plan_data = schema.load(request_data)
        plan = Plan.query.get(plan_data.id)
        if not plan:
            return jsonify({"message":f"Plan {plan_data.id} not found"}),404

        plan.value = plan_data.value  # Update other fields as needed

        plan.set_updated(session.account_id)

        db.session.commit()

        return jsonify({"message": "Plan updated successfully"}), 200

    except ValidationError as err:
        return jsonify({"message":err.message}),400
    except Exception as e:
        current_app.logger.error(f"Error updating Plan: {str(e)}")
        return jsonify({"message":f"Internal Server Error"}),500


@plan_bp.route("/delete/<id>", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_plan(session, id):
    """
    Route to delete a single plan by ID.

    Only ADMIN users can delete a plan.
    """
    plan = Plan.query.filter_by(id=id).first_or_404()
    if plan.isDeleted():
        return jsonify({"message":f"Plan {id} is already deleted"}),400

    plan.set_deleted(session.account_id)
    plan.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "Plan deleted successfully"}), 200


@plan_bp.route("/deleteAll", methods=["DELETE"])
@verify_SUPERADMIN
@verify_token
def delete_all_plans(session):
    """
    Route to delete all plans.

    Only ADMIN users can delete all plans.
    """
    plans = Plan.query.all()
    for plan in plans:
        plan.set_deleted(session.account_id)
        plan.set_updated(session.account_id)

    db.session.commit()

    return jsonify({"message": "All plans deleted successfully"}), 200


@plan_bp.route("/restore/<id>", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_plan(session, id):
    """
    Route to restore a single plan by ID.

    Only ADMIN users can restore a plan.
    """
    plan = Plan.query.filter_by(id=id).first_or_404()

    if plan.isDeleted():
        plan.set_restore(session.account_id)
        plan.set_updated(session.account_id)
        db.session.commit()
        return jsonify({"message": "Plan restore successfully"}), 200
    else:
        return jsonify({"message": "Plan is already restored"}), 400


@plan_bp.route("/restoreAll", methods=["POST"])
@verify_SUPERADMIN
@verify_token
def restore_all_plan(session):
    """
    Route to restore all plan.

    Only ADMIN users can restore all plan.
    """
    plan = Plan.query.all()
    for plan in plan:
        if plan.isDeleted():
            plan.set_restore(session.account_id)
            plan.set_updated(session.account_id)
    db.session.commit()

    return jsonify({"message": "All plan restore successfully"}), 200


