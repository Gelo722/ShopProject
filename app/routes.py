# -*- coding: utf-8 -*-
from app import app, db
from flask import render_template, flash, redirect, url_for, request, send_file
from app.forms import LoginForm, RegistrationForm, NewProduct, EditProduct, ExpensesForm, DeliveriesForm, SellForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Shop, Product, Expenses, Deliveries, Receipt
from sqlalchemy import func
####################################
import excel_export
####################################



@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    shops=Shop.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('home', id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = Shop.query.filter_by(id=form.userid.data).first()
        if user is None:
            flash('Invalid id')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('login')
        return redirect(next_page)
    return render_template('login.html', form=form, shops=shops)


@app.route('/register', methods=['GET', 'POST'])
def register():
    shops = Shop.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Shop(address=form.address.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, shops=shops)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/user/<id>', methods=['GET', 'POST'])
@login_required
def home(id):
    user = Shop.query.filter_by(id=id).first_or_404()
    warehouse= current_user.in_warehouse().all()
    return render_template('home.html', active="home", user=user, warehouse=warehouse)


@app.route('/product', methods=['GET', 'POST'])
@login_required
def product():
    form=NewProduct()
    if form.validate_on_submit():
        new = Product(product=form.product.data, price=form.price.data)
        db.session.add(new)
        db.session.commit()
        flash('Congratulations, you are now a registered product!')
        return redirect(url_for('product'))
    products = Product.query.all()
    return render_template('product.html', active='product', products=products, form=form)


@app.route('/user/<id>/<product>/<price>', methods=['GET', 'POST'])
@login_required
def edit_product(id, product, price):
    form=EditProduct()
    product = Product.query.get(id)
    if form.validate_on_submit():
        product.product= form.product.data
        product.price = form.price.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('product'))
    elif request.method == 'GET':
        form.product.data = product.product
        form.price.data = product.price
    return render_template('edit_product.html', form=form)

###########это теперь качает таблицу#################
@app.route('/product/csv', methods=['GET', 'POST']) #Скачивает таблицу
@login_required
def export_csv():
    excel_export.create_csv(current_user.id)
    p = excel_export.create_csv.csv_path
    return send_file(p, as_attachment=True, mimetype='text/xlsx', download_name='table.xlsx' )

#########################################################



@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    form=ExpensesForm()
    if form.validate_on_submit():
        new = Expenses(rent=form.rent.data, services=form.services.data,  salary=form.salary.data, expenses_in_shop=current_user )
        db.session.add(new)
        db.session.commit()
        flash('Congratulations, you are now a registered expenses!')
        return redirect(url_for('expenses'))
    expenses = current_user.in_expenses().all()
    return render_template('expenses.html',active="expences", expenses=expenses, form=form)

@app.route('/deliveries/<did>', methods=['GET', 'POST'])
@login_required
def deliveries(did):
    form = DeliveriesForm()
    if form.validate_on_submit():
        new = Deliveries(deliveries_price=form.deliveries_price.data,  product_id=did, quantity=form.quantity.data, stock_availability=form.quantity.data, product_in_shop=current_user )
        db.session.add(new)
        db.session.commit()
        flash('Congratulations, you are now a registered deliveries!')
        return redirect(url_for('product'))
    deliveries = current_user.in_deliveries(did).all()
    name=Product.query.get(did)
    return render_template('deliveries.html', form=form, deliveries=deliveries, name=name)


@app.route('/total/<did>', methods=['GET', 'POST'])
@login_required
def total(did):
    all_product=current_user.total_product(did)
    all_product_sell = current_user.total_sell_product(did)
    if not all_product[0] and all_product_sell[0]:
        quantity="error"
    elif all_product[0] and not all_product_sell[0]:
        quantity= all_product[0] - 0
    elif not all_product_sell[0] and not all_product[0]:
        quantity=0
    else:
        quantity = all_product[0] - all_product_sell[0]
    return render_template('total_product.html', all_product_sell=all_product_sell, all_product=all_product, quantity=quantity)


@app.route('/sell/<id>/<receipt_number>', methods=['GET', 'POST'])
@login_required
def sell(id, receipt_number):
    receipt_number=receipt_number
    receipt1 = Receipt.query.filter(Receipt.receipt_number == receipt_number).order_by(Receipt.date.desc()).all()
    form=SellForm()
    if form.validate_on_submit():
        check = Receipt.query.filter(Receipt.receipt_number == receipt_number, Receipt.product_id == form.product_id.data).first()
        if check is not None:
            flash('The product is already in the receipt.')
            return redirect(url_for('sell', id=current_user.id, receipt_number=receipt_number))
        all_product_sell = db.session.query(func.sum(Receipt.quantity)).filter(Receipt.point_id == current_user.id, Receipt.product_id == form.product_id.data)[0]
        all_product = db.session.query(func.sum(Deliveries.quantity)).filter(Deliveries.point_id == current_user.id, Deliveries.product_id == form.product_id.data)[0]
        if not all_product[0] and all_product_sell[0]:
            quantity1 = 0
        elif all_product[0] and not all_product_sell[0]:
            quantity1 = all_product[0] - 0
        elif not all_product_sell[0] and not all_product[0]:
            quantity1 = 0
        else:
            quantity1 = all_product[0] - all_product_sell[0]
        if quantity1 - int(form.quantity.data) < 0 or int(form.quantity.data)==0:
            flash('You do not have this product or 0.')
            return redirect(url_for('sell', id=current_user.id, receipt_number=receipt_number ))

        pr = db.session.query(Product.price).filter(Product.product_id_warehouse == form.product_id.data)[0]
        sale=Receipt(receipt_number=receipt_number, point_id=current_user.id, quantity=form.quantity.data, price=pr[0]*int(form.quantity.data),  product_id=form.product_id.data)
        db.session.add(sale)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('sell', id=current_user.id, receipt_number=receipt_number ))
    warehouse = current_user.in_warehouse().all()
    return render_template('sell.html' ,active="sell" ,receipt_number=receipt_number, form=form, receipt1=receipt1, warehouse=warehouse)
