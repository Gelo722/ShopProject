from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, FloatField
from wtforms.validators import ValidationError, DataRequired
from app.models import Shop, Deliveries, Receipt
from flask_login import current_user




class LoginForm(FlaskForm):
    userid = StringField('Userid', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_address(self, address):
        user = Shop.query.filter_by(address=address.data).first()
        if user is not None:
            raise ValidationError('Please use a different address.')


class NewProduct(FlaskForm):
    product = StringField('Product name', validators=[DataRequired()])
    price = FloatField('Product price', validators=[DataRequired()])
    send = SubmitField('To Send')

    def validate_product(self, product):
        product1=Product.query.filter_by(product=product.data).first()
        if product1 is not None:
            raise ValidationError('Error.')
    
    def validate_price(self, price):
        if price.data < 1:
            raise ValidationError('Error.')


class FindProduct(FlaskForm):
    product = StringField('Product name', validators=[DataRequired()])
    find = SubmitField('Find')

    def validate_product(self, product):
        product1=Product.query.filter(Product.product.contains(product.data)).first()
        if product1 is None:
            raise ValidationError('Not found.')


class EditProduct(FlaskForm):
    product = StringField('Product name', validators=[DataRequired()])
    price = FloatField('Product price', validators=[DataRequired()])
    send = SubmitField('To Send')

    def validate_product(self, product):
        product1=Product.query.filter_by(product=product.data).first()
        if product1 is not None:
            raise ValidationError('Error.')
    
    def validate_price(self, price):
        if price.data < 1:
            raise ValidationError('Error.')


class ExpensesForm(FlaskForm):
    rent = FloatField('Rent', validators=[DataRequired()])
    services = FloatField('Services', validators=[DataRequired()])
    salary = FloatField('Salary', validators=[DataRequired()])
    send = SubmitField('To Send')

    def validate_rent(self, rent):
        if rent.data < 1:
            raise ValidationError('Error.')

    def validate_services(self, services):
        if services.data < 1:
            raise ValidationError('Error.')

    def validate_salary(self, salary):
        if salary.data < 1:
            raise ValidationError('Error.')


class DeliveriesForm(FlaskForm):
    deliveries_price = FloatField('Deliveries price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    send = SubmitField('To Send')

    def validate_deliveries_price(self, deliveries_price):
        if deliveries_price.data < 1:
            raise ValidationError('Error.')

    def validate_quantity(self, quantity):
        if quantity.data < 1:
            raise ValidationError('Error.')


class SellForm(FlaskForm):
    product_id = StringField('Product id', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    send = SubmitField('To Send')

    def validate_product_id(self, product_id):
        check = Deliveries.query.filter(Deliveries.point_id ==current_user.id, Deliveries.product_id == product_id.data).first()
        if check is None:
            raise ValidationError('You do not have this product.')

    def validate_quantity(self, quantity):
        if quantity.data < 1:
            raise ValidationError('Error.')

