from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from vm.extensions import apispec
from vm.api.resources import UserResource, UserList, ProductResource, ProductList, \
    DepositResource, ResetResource, BuyResource
from vm.api.schemas import UserSchema, ProductSchema, UserRegisterSchema


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)


api.add_resource(UserResource, "/users/<int:user_id>", endpoint="user_by_id")
api.add_resource(UserList, "/users", endpoint="users")

api.add_resource(ProductResource, "/products/<int:product_id>", endpoint="product_by_id")
api.add_resource(ProductList, "/products", endpoint="products")

api.add_resource(DepositResource, "/deposit", endpoint="deposit")
api.add_resource(ResetResource, "/reset", endpoint="reset")
api.add_resource(BuyResource, "/buy", endpoint="buy")


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.components.schema("UserRegisterSchema", schema=UserRegisterSchema)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)
    apispec.spec.components.schema("ProductSchema", schema=ProductSchema)
    apispec.spec.path(view=ProductResource, app=current_app)
    apispec.spec.path(view=ProductList, app=current_app)

    apispec.spec.path(view=DepositResource, app=current_app)
    apispec.spec.path(view=ResetResource, app=current_app)
    apispec.spec.path(view=BuyResource, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
