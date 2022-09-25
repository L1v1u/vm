from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from vm.api.schemas import UserSchema, UserRegisterSchema
from vm.models import User, Role
from vm.extensions import db
from vm.commons.pagination import paginate
from vm.commons.decorators_helper import error_handler_jwt_extended, check_is_role
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError


class UserResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - api
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  user: UserSchema
        404:
          description: user does not exists
    put:
      tags:
        - api
      parameters:
        - in: path
          name: user_id
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              UserSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user updated
                  user: UserSchema
        404:
          description: user does not exists
    delete:
      tags:
        - api
      parameters:
        - in: path
          name: user_id
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
                    example: user deleted
        404:
          description: user does not exists
    """

    @error_handler_jwt_extended
    @jwt_required()
    def get(self, user_id):
        schema = UserSchema()
        user = User.query.get_or_404(user_id)
        current_user_id = get_jwt_identity()
        if user.id != current_user_id:
            return {"msg": "user not authorized to perform this action"}, 400
        return {"user": schema.dump(user)}

    @error_handler_jwt_extended
    @jwt_required()
    def put(self, user_id):
        try:
            schema = UserSchema(partial=True)
            user = User.query.get_or_404(user_id)
            current_user_id = get_jwt_identity()
            if user.id != current_user_id:
                return {"msg": "user not authorized to perform this action"}, 400
            user = schema.load(request.json, instance=user)
            db.session.commit()
        except ValidationError as e:
            return {"msg": str(e)}, 400

        return {"msg": "user updated", "user": schema.dump(user)}, 201

    @error_handler_jwt_extended
    @jwt_required()
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        current_user_id = get_jwt_identity()
        if user.id != current_user_id:
            return {"msg": "user not authorized to perform this action"}, 400
        db.session.delete(user)
        db.session.commit()

        return {"msg": "user deleted"}


class UserList(Resource):
    """Creation and get_all

    ---
    # get:
    #   tags:
    #     - api
    #   responses:
    #     200:
    #       content:
    #         application/json:
    #           schema:
    #             allOf:
    #               - $ref: '#/components/schemas/PaginatedResult'
    #               - type: object
    #                 properties:
    #                   results:
    #                     type: array
    #                     items:
    #                       $ref: '#/components/schemas/UserSchema'
    post:
      tags:
        - api
      requestBody:
        content:
          application/json:
            schema:
              UserRegisterSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user created
                  user: UserSchema
    """

    # @error_handler_jwt_extended
    # @jwt_required()
    # @check_is_role(role_name='ADMIN')
    # def get(self):
    #     schema = UserSchema(many=True)
    #     query = User.query
    #     return paginate(query, schema)

    def post(self):
        schema = UserRegisterSchema()
        try:
            user = schema.load(request.json)
            role = Role.query.filter_by(name=request.json['role_name'].upper()).first()
            user.role_id = role.id
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            return {"msg": "user exist with this username"}, 400
        except ValidationError as e:
            return {"msg": str(e)}, 400

        return {"msg": "user created", "user": schema.dump(user)}, 201
