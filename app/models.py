from app import db, login, app
from datetime import datetime
from flask_login import UserMixin, current_user
from sqlalchemy import PrimaryKeyConstraint, func


class Shop(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(64), index=True, unique=True)
    deliveries_in_shop = db.relationship('Deliveries', backref='product_in_shop', lazy='dynamic')
    expenses_in_shop = db.relationship('Expenses', backref='expenses_in_shop', lazy='dynamic')

    def in_warehouse(self):
        return db.session.query(Deliveries).filter(Deliveries.point_id == self.id).group_by(Deliveries.product_id)

    def in_expenses(self):
        return Expenses.query.filter(
            Expenses.point_id == self.id).order_by(
            Expenses.date.desc())

    def in_deliveries(self, did):
        return Deliveries.query.filter(
            Deliveries.point_id == self.id, Deliveries.product_id == did).order_by(
            Deliveries.deliveries_date.desc())

    def total_product(self, did):
        return db.session.query(func.sum(Deliveries.quantity)).filter(Deliveries.point_id == self.id, Deliveries.product_id == did)[0]

    def total_sell_product(self, did):
        return db.session.query(func.sum(Receipt.quantity)).filter(Receipt.point_id == self.id, Receipt.product_id == did)[0]

    def max_receipt_number(self):
        return db.session.query(func.max(Receipt.receipt_number))[0][0]+1

    @app.template_global()
    def sell(self, did):
        all_product = current_user.total_product(did)
        all_product_sell = current_user.total_sell_product(did)
        if not all_product[0] and all_product_sell[0]:
            quantity = "error"
        elif all_product[0] and not all_product_sell[0]:
            quantity = all_product[0] - 0
        elif not all_product_sell[0] and not all_product[0]:
            quantity = 0
        else:
            quantity = all_product[0] - all_product_sell[0]
        return quantity

    def __repr__(self):
        return '<Address: {}>'.format(self.address)


class Deliveries(db.Model):
    deliveries_id = db.Column(db.Integer, primary_key=True)
    point_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    deliveries_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    deliveries_price = db.Column(db.NUMERIC(9, 2), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id_warehouse'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    stock_availability = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Product information: deliveries_id {}, point_id {}, deliveries_date {}, deliveries_price {}, product_id {}, quantity {}, stock_availability {}>'.format(
            self.deliveries_id, self.point_id, self.deliveries_date, self.deliveries_price, self.product_id,
            self.quantity, self.stock_availability)


class Expenses(db.Model):
    expenses_id = db.Column(db.Integer, primary_key=True)
    point_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    rent = db.Column(db.NUMERIC(9, 2), nullable=False)
    services = db.Column(db.NUMERIC(9, 2), nullable=False)
    salary = db.Column(db.NUMERIC(9, 2), nullable=False)
    date = db.Column(db.Date, index=True, default=datetime.utcnow)


    def __repr__(self):
        return '<Expenses information: expenses_id {}, point_id {}, rent {}, services {}, salary {}, date {}>'.format(
            self.expenses_id, self.point_id, self.rent, self.services, self.salary,
            self.date)


class Product(db.Model):
    product_id_warehouse = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(64), index=True, unique=True)
    price = db.Column(db.NUMERIC(9, 2), nullable=False)
    product_information = db.relationship('Deliveries', backref='information', lazy='dynamic')
    product_sale = db.relationship('Receipt', backref='sale', lazy='dynamic')


    def __repr__(self):
        return '<Product information: product_id_warehouse {}, product {}, price {}>'.format(
            self.product_id_warehouse, self.product, self.price)


class Receipt(db.Model):
    __table_args__ = (PrimaryKeyConstraint('receipt_number', 'product_id', name='receipt'),)
    receipt_number = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id_warehouse'), nullable=False)
    point_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.NUMERIC(9, 2), nullable=False)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)


    def __repr__(self):
        return '<Receipt information: receipt_number {}, product_id {}, point_id {}, quantity {}, price {}, date {}>'.format(
            self.receipt_number, self.product_id, self.point_id, self.quantity, self.price,
            self.date)


@login.user_loader
def load_user(id):
    return Shop.query.get(int(id))
