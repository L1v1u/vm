from vm.models import Role
from vm.extensions import ma, db


class RoleSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)

    class Meta:
        model = Role
