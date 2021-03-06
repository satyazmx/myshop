import secrets
import os
from flask import render_template, redirect, request, url_for,flash, session, current_app
from shop import db, app, photos, search
from .models import Brand, Category, Addproduct
from .forms import AddproductsForm


def brands():
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return brands

def categories():
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/')
def home():
    page = request.args.get('page',1,type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page = page, per_page=8)
    return render_template('products/index.html', products = products, brands = brands(),categories = categories())

@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name','description'], limit=3)
    return render_template('products/result.html', products = products, brands = brands(),categories = categories())

@app.route('/product/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html', product = product, brands = brands(),categories = categories())

@app.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page', 1, type= int)
    get_brand = Addproduct.query.filter_by(id = id).first_or_404()
    brand = Addproduct.query.filter_by(brand = get_brand).paginate(page = page, per_page=8)
    return render_template('products/index.html',brand = brand, brands= brands(),categories = categories(),
                           get_brand = get_brand)

@app.route('/category/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Addproduct.query.filter_by(id= id).first_or_404()
    category = Addproduct.query.filter_by( category = get_cat).paginate(page = page, per_page=8)
    return render_template('products/index.html', category = category, categories = categories(),brands = brands(),
                           get_cat = get_cat)

@app.route('/addbrand', methods = ['GET', 'POST'])
def addbrand():
    if request.method == "POST":
        getbrand = request.form.get('brand')
        brand = Brand(name = getbrand)
        db.session.add(brand)
        db.session.commit()
        flash(f"Brand { getbrand } added to your database",'success')
        return redirect(url_for('addbrand'))
    return render_template('products/addbrand.html', brands = 'brands')

@app.route('/updatebrand/<int:id>',methods=['GET','POST'])
def updatebrand(id):
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method =="POST":
        updatebrand.name = brand
        flash(f'The brand {updatebrand.name} was changed to {brand}','success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html', title='UPdate brand',brands='brands',updatebrand=updatebrand)

@app.route('/deletebrand/<int:id>',methods=['GET','POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    try:
        if request.method == 'POST':
            db.session.delete(brand)
            db.session.commit()
            flash(f'The brand {brand.name} deleted successfully', 'success')
            return redirect(url_for('admin'))
    except:
        flash(f"The brand {brand.name} can't be  deleted from your database", "warning")
        return redirect(url_for('admin'))


@app.route('/addcategory', methods = ['GET', 'POST'])
def addcategory():
    if request.method == "POST":
        getcategory= request.form.get('category')
        category = Category(name = getcategory)
        db.session.add(category)
        db.session.commit()
        flash(f"Category {getcategory} added to your database",'success')
        return redirect(url_for('addbrand'))
    return render_template('products/addbrand.html')

@app.route('/updatecategory/<int:id>',methods=['GET','POST'])
def updatecategory(id):
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method =="POST":
        updatecategory.name = category
        flash(f'The brand {updatecategory.name} was changed to {category}','success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('products/updatebrand.html', title='UPdate brand',updatecategory=updatecategory)

@app.route('/deletecatgory/<int:id>',methods=['GET','POST'])
def deletecatgory(id):
    category = Category.query.get_or_404(id)
    try:
        if request.method == 'POST':
            db.session.delete(category)
            db.session.commit()
            flash(f'The Category {category.name} deleted successfully', 'success')
            return redirect(url_for('admin'))
    except:
        flash(f"The Category {category.name} can't be  deleted from your database", "warning")
        return redirect(url_for('admin'))

@app.route('/addproduct', methods = ['GET', 'POST'])
def addproduct():
    brands = Brand.query.all()
    categories = Category.query.all()
    form = AddproductsForm(request.form)
    if request.method =='POST':
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name = secrets.token_hex(10) + '.')
        image_2 = photos.save(request.files.get('image_2'),name = secrets.token_hex(10) + '.')
        image_3 = photos.save(request.files.get('image_3'), name = secrets.token_hex(10) + '.')

        addproduct = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors,
                                description=description,
                                category_id=category,brand_id=brand, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addproduct)
        db.session.commit()
        flash(f"Product {name} added to your database", 'success')
        return redirect(url_for('admin'))

    return render_template('products/addproduct.html', title="Add Product", form = form,
                           brands = brands, categories = categories)

@app.route('/updateproduct/<int:id>', methods = ['GET', 'POST'])
def updateproduct(id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = AddproductsForm(request.form)
    if request.method == 'POST':
        product.name = form.name.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.discount = form.discount.data
        product.description = form.description.data
        product.colors = form.colors.data
        product.brand_id = brand
        product.category_id = category

        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save( request.files.get('image_1'), name = secrets.token_hex(10) + '.')
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')

        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')

        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')

        db.session.commit()
        flash("Product has been updated successfully", 'success')
        return redirect(url_for('admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.stock.data = product.stock
    form.discount.data = product.discount
    form.description.data = product.description
    form.colors.data = product.colors
    return render_template('products/updateproduct.html', title = 'Update Product', form = form,brands = brands, categories=categories,
                           product = product)

@app.route('/deleteproduct/<int:id>',methods=['GET','POST'])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method == 'POST':
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as e:
            print(e)

        db.session.delete(product)
        db.session.commit()
        flash(f'The Product {product.name} deleted successfully', 'success')
        return redirect(url_for('admin'))
    flash(f"The Product {product.name} can't be  deleted from your database", "warning")
    return redirect(url_for('admin'))