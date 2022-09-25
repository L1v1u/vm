from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from vm.api.schemas import ProductSchema
from vm.models import Product
from vm.extensions import db
from vm.commons.pagination import paginate
from vm.commons.decorators_helper import error_handler_jwt_extended, check_is_role
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError



class ProductResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: product_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  Product: ProductSchema
        404:
          description: Product does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: product_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              ProductSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Product updated
                  Product: ProductSchema
        404:
          description: Product does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: product_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Product deleted
        404:
          description: Product does not exists
    """

    def get(self, product_id):
        schema = ProductSchema()
        product = Product.query.get_or_404(product_id)
        return {"Product": schema.dump(product)}

    @error_handler_jwt_extended
    @jwt_required()
    @check_is_role(role_name='SELLER')
    def put(self, product_id):
        schema = ProductSchema(partial=True)
        product = Product.query.get_or_404(product_id)
        current_user_id = get_jwt_identity()
        if product.seller_id != current_user_id:
            return {"msg": "not authorized to perform this action"}, 401
        product = schema.load(request.json, instance=product)

        db.session.commit()

        return {"msg": "Product updated", "Product": schema.dump(product)}

    @error_handler_jwt_extended
    @jwt_required()
    @check_is_role(role_name='SELLER')
    def delete(self, product_id):
        product = Product.query.get_or_404(product_id)
        current_user_id = get_jwt_identity()
        if product.seller_id != current_user_id:
            return {"msg": "not authorized to perform this action"}, 401
        db.session.delete(product)
        db.session.commit()

        return {"msg": "Product deleted"}


class ProductList(Resource):
    """Creation and get_all

    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/ProductSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              ProductSchema
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
                  Product: ProductSchema
    """

    def get(self):
        schema = ProductSchema(many=True)
        query = Product.query
        return paginate(query, schema)

    @error_handler_jwt_extended
    @jwt_required()
    @check_is_role(role_name='SELLER')
    def post(self):
        try:
            schema = ProductSchema()
            product = schema.load(request.json)
            product.seller_id = get_jwt_identity()
            db.session.add(product)
            db.session.commit()
        except IntegrityError as e:
            return {"msg": "product exist with this name"}, 400
        except ValidationError as e:
            return {"msg": str(e)}, 400

        return {"msg": "Product created", "Product": schema.dump(product)}, 201
