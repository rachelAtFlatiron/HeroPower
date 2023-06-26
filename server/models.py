from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade="all, delete-orphan")
    all_powers = association_proxy('hero_powers', 'power')
    # add serialization rules
    # Hero.hero_powers <-> HeroPower.hero
    # Hero.all_powers <-> Power.all_heroes

    serialize_rules = ('-hero_powers.hero', '-all_powers.all_heroes', )
    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship("HeroPower", back_populates='power', cascade="all, delete-orphan")
    all_heroes = association_proxy("hero_powers", "hero")

    # add serialization rules
    serialize_rules = ( '-hero_powers.power', '-all_heroes.all_powers',)
    # add validation
    @validates('description')
    def validates_des(self, key, input_des):
        if len(input_des) < 20:
            raise ValueError('no')
        return input_des

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))
    
    # add relationships
    # these two hero_powers are totally different
    power = db.relationship("Power", back_populates="hero_powers") #Power.hero_powers
    hero = db.relationship("Hero", back_populates="hero_powers") #Hero.hero_powers
    
    # add serialization rules
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers', )

    # add validation
    @validates('strength')
    #value is whatever value the user puts in
    def validate_strength(self, key, input_strength):
        print(f'from @validates(strength) {input_strength}')
        # if(input_strength == 'Weak' or input_strength == 'Strong' or input_strength == 'Average'):
        if(input_strength in ['Weak', 'Average', 'Strong']):
            return input_strength
        raise ValueError('no')

    def __repr__(self):
        return f'<HeroPower {self.id}>'
