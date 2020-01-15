from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, ExerciseForm, ProgressionFormStrength, ProgressionFormEndurance, ProgressionFormMental
from app.models import User, Exercise, Progression
# from app.translate import translate
from app.main import bp
from app.auth.email import new_admin_email


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

@bp.route('/', methods=['GET', 'POST'])
def start_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return redirect(url_for('auth.login'))


@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    current_user.visits += 1
    db.session.commit()
    exercises = current_user.get_exercises().all()

    form = ExerciseForm()
    if form.validate_on_submit():
        exercise = Exercise(name=form.name.data.replace(' ','_'), author=current_user, type=form.type.data)
        db.session.add(exercise)
        db.session.commit()
        flash(_('Exercise added succesfully'))
        return redirect(url_for('main.exercise', exercise_name=exercise.name))

    return render_template('index.html',title=_('Home'), form=form, exercises=exercises, user=current_user)

@bp.route('/exercise/<exercise_name>', methods = ['GET','POST'])
@login_required
def exercise(exercise_name):

    exercise = Exercise.query.filter_by(user_id=current_user.id).filter_by(name=exercise_name).first_or_404()
    type = exercise.type
    print(type)
    if type == 'mental':
        form = ProgressionFormMental()
    elif type == 'endurance':
        form = ProgressionFormEndurance()
    else:
        form = ProgressionFormStrength()

    if form.validate_on_submit():
        progression = Progression(exercise=exercise, exercise_id=exercise.id)
        if type == 'mental':
            description = form.description.data
            progression.description = description
        elif type == 'endurance':
            sets = form.sets.data
            duration = form.duration.data
            progression.sets = sets
            progression.duration = duration
        else:
            reps = form.reps.data
            sets = form.sets.data
            weight = form.weight.data
            print(reps, sets, weight)
            progression.reps = reps
            progression.sets = sets
            progression.weight = weight
            print(progression.sets, progression.reps, progression.weight)

        print(progression.sets, progression.reps, progression.weight)
        db.session.add(progression)
        db.session.commit()
        flash(_('Entry added!'))

        return redirect(url_for('main.exercise', exercise_name = exercise_name))

    fields = []
    for field in form:
        if field.name != 'submit' and 'csrf' not in field.name:
            fields += [field.name]
    return render_template('exercise.html',exercise=exercise,form = form,fields = fields)

@bp.route('/delete_exercise',methods=['GET', 'POST'])
@login_required
def delete():
    exercise_name = request.args.get('exercise_name')

    exercise = Exercise.query.filter_by(user_id=current_user.id).filter_by(name=exercise_name)
    exercise.first().progression.delete()
    exercise.delete()
    db.session.commit()
    flash('Exercise succesfully deleted!')
    return url_for('main.index')


@bp.route('/complete_progression', methods = ['GET', 'POST'])
@login_required
def complete_progression():
    progression_id = request.args.get('progression_id').split('-')[-1]
    progression = Progression.query.filter_by(id=progression_id).first()
    if progression.progression_status == '-completed':
        progression.progression_status = ''
    else:
        progression.progression_status = '-completed'
    db.session.commit()
    return progression_id

@bp.route('/delete_progression', methods = ['GET', 'POST'])
@login_required
def delete_progression():
    toDelete_ids = request.args.getlist('toDelete_ids[]')
    exercise_name = request.args.get('exercise')
    ids = []
    for _id in toDelete_ids:
        ids += [_id.split('-')[-1]]
    for _id in ids:
        progression = Progression.query.filter_by(id = _id)
        progression.delete()
        db.session.commit()
    return 'success'

@bp.route('/user_stats')
@login_required
def user_stats():
    current_user_email = current_user.email
    if current_user_email in current_app.config['ADMINS']:
        users = User.query.all()
        num_users = len(users)
        total_visits = 0
        for user in users:
            total_visits += user.visits
        return render_template('user_stats.html', users = users, num_users=num_users, total_visits=total_visits)
    flash('This page is currently unavailable!')
    return redirect(url_for('main.index'))

@bp.route('/delete_user')
@login_required
def delete_user():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    response = user.delete()
    return response

@bp.route('/make_admin')
@login_required
def make_admin():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    response = user.make_admin()
    new_admin_email(user)
    return response



# @bp.route('/edit_profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm(current_user.username)
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.about_me = form.about_me.data
#         db.session.commit()
#         flash(_('Your changes have been saved.'))
#         return redirect(url_for('main.edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', title=_('Edit Profile'),
#                            form=form)

