from flask import current_app
from vm.models import Product
from vm.extensions import ma, db
from marshmallow import validates, ValidationError


class ProductSchema(ma.SQLAlchemyAutoSchema):
    id = ma.Int(dump_only=True)
    cost = ma.Int(required=True)
    amount_available = ma.Int(required=True)

    class Meta:
        model = Product
        sqla_session = db.session
        load_instance = True
        exclude = ("seller_id", )

    @validates("cost")
    def validate_cost(self, cost):
        if cost % 5 != 0 or cost == 0:
            raise ValidationError("cost must be  multiples of 5")
        return cost

    @validates("amount_available")
    def validate_amount_available(self, amount_available):
        if amount_available <= 0:
            raise ValidationError("amount_available must be  positive")
        return amount_available


class BuyProductSchema(ma.SQLAlchemyAutoSchema):
    id = ma.Int(required=True)
    amount_to_buy = ma.Int(required=True)

    class Meta:
        model = Product
        sqla_session = db.session
        load_instance = True
        exclude = ("seller_id", "amount_available", "cost", "product_name")

    @validates("amount_to_buy")
    def validate_amount_to_buy(self, amount_to_buy):
        if amount_to_buy <= 0:
            raise ValidationError("amount_to_buy must be  positive")
        return amount_to_buy
