import re
from vm.models import User
from vm.extensions import ma, db
from .role import RoleSchema
from marshmallow import validates, ValidationError


class UserSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)
    password = ma.String(load_only=True, required=True)


    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        exclude = ("_password", "deposit", )

    @validates("password")
    def validate_password(self, password):
        if not re.match("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
            raise ValidationError("Minimum eight characters, at least one letter and one number")

        return password


class UserRegisterSchema(UserSchema):
    role_name = ma.String(load_only=True, required=True)

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        exclude = ("_password", "active", )

    @validates("role_name")
    def validate_role_name(self, role_name):
        if role_name.upper() not in ["BUYER", "SELLER"]:
            raise ValidationError("wrong role name, accepted BUYER or SELLER")
        return role_name


class UserDepositSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)
    deposit = ma.Int(required=True)

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        exclude = ("_password", "active", "username", )

    @validates("deposit")
    def validate_deposit(self, deposit):
        if deposit not in [5, 10, 20, 50, 100]:
            raise ValidationError("deposit must be 5 or 10 or 20 or 50 or 100 ")
        return deposit
