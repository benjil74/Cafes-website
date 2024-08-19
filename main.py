from flask import Flask, render_template, redirect, url_for, jsonify, request, flash
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    img_url = StringField('Picture Link', validators=[DataRequired(), URL()])
    map_url = StringField('Cafe Location on Google Maps (URL)', validators=[DataRequired(), URL()])
    location = StringField("Cafe Location", validators=[DataRequired()])
    seats = StringField("Number of seats ?", validators=[DataRequired()])
    toilet = BooleanField("Has toilet ?", validators=[DataRequired()])
    wifi = BooleanField("Has Wifi ?", validators=[DataRequired()])
    sockets = BooleanField("Has sockets ?", validators=[DataRequired()])
    calls = BooleanField("Can take calls ?", validators=[DataRequired()])
    coffee_price = StringField("Coffee Price", validators=[DataRequired()])
    submit = SubmitField('Submit')


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=request.form.get("cafe"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    list_of_rows = []
    for cafe in all_cafes:
        row = [
            cafe.name,
            cafe.img_url,
            cafe.map_url,
            cafe.location,
            cafe.seats,
            "Yes" if cafe.has_toilet else "No",
            "Yes" if cafe.has_wifi else "No",
            "Yes" if cafe.has_sockets else "No",
            "Yes" if cafe.can_take_calls else "No",
            cafe.coffee_price,
            cafe.id
        ]
        list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


@app.route("/search", methods=["GET", "POST"])
def get_cafe_at_location():
    if request.method == "POST":
        query_location = request.form["location"]
        result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
        all_cafes = result.scalars().all()
        list_of_rows = []
        for cafe in all_cafes:
            row = [
                cafe.name,
                cafe.img_url,
                cafe.map_url,
                cafe.location,
                cafe.seats,
                "Yes" if cafe.has_toilet else "No",
                "Yes" if cafe.has_wifi else "No",
                "Yes" if cafe.has_sockets else "No",
                "Yes" if cafe.can_take_calls else "No",
                cafe.coffee_price,
                cafe.id
            ]
            list_of_rows.append(row)
        if all_cafes:
            return render_template("cafes.html", cafes=list_of_rows)
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404
    return render_template("search.html")


@app.route("/update-price", methods=["GET", "POST"])
def patch_new_price():
    if request.method == "POST":
        cafe_id = request.form["id"]
        cafe_to_update = db.get_or_404(Cafe, cafe_id)
        cafe_to_update.coffee_price = request.form["new_price"]
        db.session.commit()
        return redirect(url_for('cafes'))
    cafe_id = request.args.get('cafe_id')
    cafe_selected = db.session.query(Cafe).get(cafe_id)
    return render_template('edit_price.html', cafe=cafe_selected)


@app.route("/reports-closed/<int:cafe_id>", methods=["DELETE", "POST", "GET"])
def delete_cafes(cafe_id):
    cafe_to_delete = db.session.query(Cafe).get(cafe_id)
    if cafe_to_delete:
        db.session.delete(cafe_to_delete)
        db.session.commit()
        flash("Cafe deleted successfully!", "success")
    else:
        flash("Cafe not found.", "error")

    return redirect(url_for('cafes'))


if __name__ == '__main__':
    app.run(debug=True)
