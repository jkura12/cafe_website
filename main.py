from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, func, insert, update
import requests
from pathlib import Path 

app = Flask(__name__)
app.secret_key = "dev-change-me"

# Create DB 
class Base(DeclarativeBase): 
    pass

# Connect to DB 
BASE_DIR = Path(__file__).resolve().parent 
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'instance' / 'cafes.db'}"
db = SQLAlchemy(model_class=Base)
db.init_app(app) 
Bootstrap5(app)


class Cafe(db.Model): 
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[int] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    city: Mapped[str] = mapped_column(String(250), nullable=False, default="London, UK")
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False) 
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=False)

    def to_dict(self): 
        return { 
            "id": self.id,
            "name": self.name,
            "map_url": self.map_url,
            "img_url": self.img_url,
            "location": self.location,
            "city": self.city,
            "seats": self.seats,
            "has_toilet": self.has_toilet,
            "has_wifi": self.has_wifi,
            "has_sockets": self.has_sockets,
            "can_take_calls": self.can_take_calls,
            "coffee_price": self.coffee_price,
        } 

with app.app_context(): 
    db.create_all() 


@app.route("/")
def home(): 
    all_cafes = db.session.execute(
    db.select(Cafe).order_by(Cafe.name)
    ).scalars().all() 
    
    return render_template('index.html', cafes=[cafe.to_dict() for cafe in all_cafes]) 


# HTTP GET - Read Record 
@app.route('/random')
def random(): 
    random_cafe = db.session.execute(
        db.select(Cafe).order_by(func.random()) 
    ).first()

    if random_cafe is None: 
        return jsonify(error={"Not Found" : "No cafes available"}), 404
    return render_template('index.html', cafes=[cafe.to_dict() for cafe in random_cafe])

# HTTP GET - Query string
@app.route('/search')
def search(): 
    loc = request.args.get('search', ' ').strip()

    if not loc: 
        return redirect(url_for(home))
    
    loc_cafes = db.session.execute(
        db.select(Cafe)
        .where(Cafe.location.ilike(f"%{loc}%"))
        .order_by(Cafe.name) 
    ).scalars().all()

    return render_template('index.html', 
                           cafes=[cafe.to_dict() for cafe in loc_cafes],
                           search_term=loc)


# HTTP POST - Create Record
@app.route('/add', methods=['GET', 'POST'])
def add(): 
    if request.method == 'POST':
        new_cafe = Cafe(
            name=request.form.get('name'), 
            map_url=request.form.get('map_url'),
            img_url=request.form.get('img_url'), 
            location=request.form.get('location'),
            city=request.form.get('city') or "London, UK",
            seats=request.form.get('seats'),
            has_toilet=bool(request.form.get('has_toilet')),
            has_wifi=bool(request.form.get('has_wifi')),
            has_sockets=bool(request.form.get('has_sockets')),
            can_take_calls=bool(request.form.get('can_take_calls')),
            coffee_price=request.form.get('coffee_price')
            )

        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('add.html')
    # return jsonify(response={"Success!" : f"{new_cafe.name} was successfully added."})

# HTTP PUT/PATCH - Update Record 
@app.route('/update-cafe/<int:id>', methods=['GET', 'POST'])
def update(id): 
    cafe = db.get_or_404(Cafe, id) 

    if request.method == 'POST':
        cafe.name=request.form.get('name')
        cafe.map_url=request.form.get('map_url')
        cafe.img_url=request.form.get('img_url')
        cafe.location=request.form.get('location')
        cafe.city=request.form.get('city') or "London, UK"
        cafe.seats=request.form.get('seats')
        cafe.has_toilet=bool(request.form.get('has_toilet'))
        cafe.has_wifi=bool(request.form.get('has_wifi'))
        cafe.has_sockets=bool(request.form.get('has_sockets'))
        cafe.can_take_calls=bool(request.form.get('can_take_calls'))
        cafe.coffee_price=request.form.get('coffee_price')
        db.session.commit() 
        flash(f"{cafe.name} updated.")
        return redirect(url_for('home'))

    return render_template('add.html', cafe=cafe)

# HTTP DELETE - Delete Record 
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cafe = db.get_or_404(Cafe, id)

    db.session.delete(cafe)
    db.session.commit()

    flash(f"{cafe.name} deleted.")
    return redirect(url_for('home'))

if __name__ == '__main__': 
    app.run(debug=True)
