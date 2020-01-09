from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, ExerciseForm, ProgressionForm
from app.models import User, Exercise, Progression
# from app.translate import translate
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = ExerciseForm()
    if form.validate_on_submit():
        sameNameExercise = Exercise.query.filter_by(user_id = current_user.id, name=form.name.data).first()
        if sameNameExercise is None:
            exercise = Exercise(name=form.name.data, author = current_user)
            db.session.add(exercise)
            db.session.commit()
            flash(_('Exercise added succesfully'))
        else:
            flash('Exercise already exists!')


    exercises = current_user.get_exercises().all()
    return render_template('index.html',title=_('Home'),form=form, exercises=exercises,user=current_user)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@bp.route('/exercises/<exercise_name>', methods = ['GET','POST'])
@login_required
def exercise(exercise_name):
    if '%20' in exercise_name:
        exercise_name = exercise_name.replace('%20', ' ')
    elif '%40' in exercise_name:
        exercise_name = exercise_name.replace('%40', '@')

    exercise = Exercise.query.filter_by(user_id=current_user.id).filter_by(name=exercise_name).first_or_404()
    form = ProgressionForm()

    if form.validate_on_submit():
        sets = form.sets.data
        reps = form.sets.data
        weight = form.weight.data
        duration = form.duration.data
        print('WEIGHT,DURATION',weight,duration)
        sameProgression = Progression.query.filter_by(sets = sets, reps = reps, weight = weight, duration = duration, exercise_id = exercise.id).first()
        if sameProgression is None:
            progression = Progression(exercise = exercise,
                                      exercise_id=exercise.id,
                                      sets = sets,
                                      reps = reps,
                                      weight= weight,
                                      product= float(form.sets.data) * float(form.reps.data))
            db.session.add(progression)
            db.session.commit()
            flash(_('Entry added!'))

    return render_template('exercise.html',exercise=exercise,form = form)

@bp.route('/delete_exercise',methods=['GET', 'POST'])
@login_required
def delete():
    exercise_name = request.args.get('exercise_name')
    if '%20' in exercise_name:
        exercise_name = exercise_name.replace('%20',' ')
    elif '%40' in exercise_name:
        exercise_name = exercise_name.replace('%40','@')

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

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


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
    flash('Tsk Tsk Tsk, trying to acces pages you shouldnt? Santa (and an administrator) have been notified of your misdemeanor.')
    return redirect(url_for('main.index'))

