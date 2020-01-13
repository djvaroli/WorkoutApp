from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
import inspect
from math import ceil

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(20))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    exercise = db.relationship('Exercise', backref='author',lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    visits = db.Column(db.Integer)
    is_confirmed = db.Column(db.Boolean, default=False)
    units = db.Column(db.String(10))
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def make_admin(self):
        if self.email in current_app.config['ADMINS']:
            self.is_admin = True

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_exercises(self):
        exercises = Exercise.query.filter_by(user_id=self.id)
        return exercises

    def get_confirm_email_token(self,):
        return jwt.encode(
            {'confirm_email': self.id},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def delete(self):
        status = User.query.filter_by(username=self.username).delete()
        if status > 0:
            db.session.commit()
            return 'Successfully Deleted'
        else:
            return 'Something Went Wrong'

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_confirm_email_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['confirm_email']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(15))
    progression = db.relationship('Progression', backref='exercise', lazy='dynamic')

    def __repr__(self):
        params = {'id': self.id,
                  'name': self.name,
                  'user_id': self.user_id,
                }
        repr = ''
        for param in params.keys():
            repr += "< {}: {} >".format(param,params[param])
        return repr


    def ordered_progressions(self):
        """
        order the progressions in increasing of order of reps*sets and also in increasing order of weight
        :return:array of sorted progressions
        """
        sorted_prg = []
        weights = [w[0] for w in db.session.query(Progression.weight.distinct())]

        for w in weights:
            weight_progressions_sorted = Progression.query.filter_by(weight = w,exercise_id = self.id).order_by(Progression.product.asc())
            sorted_prg += weight_progressions_sorted.all()

        return sorted_prg

class Progression(db.Model):
    """
    Progression for an exercise
    """
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)
    product = db.Column(db.Float)
    duration = db.Column(db.Float)
    description = db.Column(db.String(500))
    progression_status = db.Column(db.String(20))

    def __repr__(self):
        return '<Exercise id : {}. Product: {} >'.format(self.exercise_id, self.product)



# def calc_progression(self):
    #     prog = Progression.query.filter_by(exercise_id = self.id)
    #     if prog is not None:
    #         prog.delete()
    #         db.session.commit()
    #
    #     count = 0
    #     progression = {count: [int(self.start_reps), int(self.start_sets), float(self.start_weight)]}
    #     current_product = int(self.start_reps) * int(self.start_sets) * float(self.start_weight)
    #     target_product = int(self.target_reps) * int(self.target_sets) * float(self.target_weight)
    #
    #     for i in range(5):
    #         count += 1
    #         sets = int(self.start_reps) + i
    #         reps = int(self.start_sets) + i
    #         weight = float(self.start_weight) + 5*i
    #         product = sets * reps
    #         progression[count] = [sets, reps, weight]
    #         new_progression = Progression(exercise = self, exercise_id=self.id, sets = sets, reps=reps, weight=weight,
    #                                       product = product)
    #         db.session.add(new_progression)
    #         db.session.commit()
        # while current_product != target_product:
        #     current_reps, current_sets, current_weight = progression[count]
        #     current_product = current_reps * current_sets * current_weight
        #
        #     print(current_sets, current_reps, current_weight)
        #
        #     new_sets = 0
        #     if current_sets == 3:
        #         new_sets = 4
        #     elif current_sets == 4:
        #         new_sets = 3
        #     elif current_sets < 3:
        #         new_sets += 1
        #
        #     print(current_product, new_sets)
        #
        #     new_reps = ceil(current_product / (new_sets * current_weight))
        #     count += 1
        #     if new_sets == self.target_sets and new_reps == self.target_reps:
        #         new_sets = 3
        #         new_reps = 6
        #         new_weight = current_weight + 2.5
        #     else:
        #         new_weight = current_weight
        #
        #     current_product = new_reps * new_sets * new_weight
        #     progression[count] = [new_reps, new_sets, new_weight]

        # return progression

