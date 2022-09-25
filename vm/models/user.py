from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref
from vm.extensions import db, pwd_context

class User(db.Model):
    """Basic user model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password = db.Column("password", db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship("Role", backref=backref("role", uselist=False))
    deposit = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = pwd_context.hash(value)

    def __repr__(self):
        return "<User %s>" % self.username
