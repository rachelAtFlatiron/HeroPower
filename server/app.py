#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

# 🛑 DO NOT FORGET THIS
api = Api(app)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Heroes(Resource):
    def get(self):
        q = Hero.query.all()
        hero_dict = [h.to_dict(only=('id', 'name', 'super_name')) for h in q]
        return make_response(hero_dict, 200)
# 🛑 DONT FORGET add_resource
api.add_resource(Heroes, '/heroes')

class OneHero(Resource):
    def get(self, hero_id):
        q = Hero.query.filter_by(id=hero_id).first()
        if not q: 
            return make_response({"error": "Hero not found"}, 404)
        return make_response(q.to_dict(), 200)

api.add_resource(OneHero, '/heroes/<int:hero_id>')

class Powers(Resource):
    def get(self):
        q = Power.query.all()
        power_dict = [p.to_dict(only=('description', 'id', 'name')) for p in q]
        return make_response(power_dict, 200)
api.add_resource(Powers, '/powers')

class OnePower(Resource):
    def get(self, power_id):
        q = Power.query.filter_by(id=power_id).first()
        if not q: 
            return make_response({"error": "Power not found"}, 404)
        return make_response(q.to_dict(only=('id', 'description', 'name')), 200)
    
    def patch(self, power_id):
        q = Power.query.filter_by(id=power_id).first()
        if not q: 
            return make_response({"error": "Power not found"}, 404)
        try:
            data = request.get_json()
            for attr in data: 
                setattr(q, attr, data.get(attr)) 
            db.session.add(q)
            db.session.commit()
        except: 
            return make_response({"errors": ["validation errors"]}, 400)

        return make_response(q.to_dict(only=('description', 'id', 'name')), 200)

api.add_resource(OnePower, '/powers/<int:power_id>')

class HeroPowers(Resource):
    def post(self):
        data = request.get_json() 
        try: 
            hp = HeroPower(strength=data.get('strength'), power_id=data.get('power_id'), hero_id=data.get('hero_id'))
            db.session.add(hp)
            db.session.commit() 
        except: 
            return make_response({"errors": ["validation errors"]}, 400)

        return make_response(hp.to_dict(), 200)

api.add_resource(HeroPowers, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
