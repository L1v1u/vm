from sqlalchemy.orm import backref
from vm.extensions import db


class Product(db.Model):
    """Basic product model"""

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(80), unique=True, nullable=False)
    cost = db.Column(db.Integer, nullable=False, default=0)
    amount_available = db.Column(db.Integer, nullable=False, default=0)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seller = db.relationship("User", backref=backref("user", uselist=False))

    def __repr__(self):
        return "<Product %s>" % self.product_name
