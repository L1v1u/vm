from vm.extensions import db


class Role(db.Model):
    """Basic role model"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return "<Role %s>" % self.name
