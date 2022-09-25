from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from vm.api.schemas import UserSchema, ProductSchema, UserDepositSchema, BuyProductSchema
from vm.models import User, Product
from vm.extensions import db
from vm.commons.pagination import paginate
from vm.commons.decorators_helper import error_handler_jwt_extended, check_is_role
from marshmallow import ValidationError


class BuyResource(Resource):
    """Single object resource

    ---
   post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              type: array
              items:
                BuyProductSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Product created
                  Products:
                    type: object
                  total_spent:
                    type: integer
                  change_to_return:
                    type: object

    """

    @error_handler_jwt_extended
    @jwt_required()
    @check_is_role(role_name='BUYER')
    def post(self):
        try:
            schema = BuyProductSchema(many=True)
            products_to_buy = schema.load(request.json)
        except ValidationError as e:
            return {"msg": str(e)}, 400
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        total_spent = 0
        products_bought = []

        for product_buy in products_to_buy:
            product = Product.query.get(product_buy.id)
            if product is None:
                return {"msg": f"Product {product_buy.id} does not exist"}
            if product.amount_available < product_buy.amount_to_buy :
                return {"msg": f"Product {product_buy.id} not available in this quantity"}
            total_spent += product_buy.amount_to_buy * product.cost
            products_bought.append(product.product_name)
            product.amount_available = product.amount_available - product_buy.amount_to_buy
            db.session.add(product)
        current_user.deposit -= total_spent
        if current_user.deposit < 0:
            return {"msg": "Deposit not sufficient for this product(s)"}
        db.session.add(current_user)
        db.session.commit()

        change_to_return = {}
        for coins in [100, 50, 20, 10, 5]:
            if current_user.deposit / coins > 0:
                change_to_return[coins] = int(current_user.deposit / coins)
                current_user.deposit -= coins * change_to_return[coins]

        return {"msg": "Order created", "change_to_return": change_to_return,
                "Products": products_bought, "total_spent": total_spent}, 201


class DepositResource(Resource):
    """Deposit resource api

    ---
   post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              UserDepositSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Deposit added
                  current_deposit:
                    type: integer
                    example: 10

    """

    @error_handler_jwt_extended
    @jwt_required()
    @check_is_role(role_name='BUYER')
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            current_user = User.query.get_or_404(current_user_id)
            schema = UserDepositSchema()
            user = schema.load(request.json)
            current_app.logger.warning(user)
            current_user.deposit += user.deposit

            db.session.add(current_user)
            db.session.commit()
        except ValidationError as e:
            return {"msg": str(e)}, 400
        return {"msg": "Deposit added", "current_deposit": current_user.deposit}, 201


class ResetResource(Resource):
    """Reset resource api

    ---
   get:
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Deposit reset
                  change_to_return:
                    type: object
    """

    @error_handler_jwt_extended
    @jwt_required()
    @check_is_role(role_name='BUYER')
    def get(self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)

        deposit = current_user.deposit
        current_user.deposit = 0

        db.session.add(current_user)
        db.session.commit()
        change_to_return = {}

        for coins in [100, 50, 20, 10, 5]:
            if deposit / coins > 0:
                change_to_return[coins] = int(deposit / coins)
                deposit -= coins * change_to_return[coins]

        return {"msg": "Deposit reset", "change_to_return": change_to_return}, 201
