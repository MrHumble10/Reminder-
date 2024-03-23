from flask import Flask, render_template, redirect, url_for, request, flash, abort
# from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user
from notification import send_email, send_sms
import os
# from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
import datetime as dt
from datetime import timedelta
import calendar
import requests
import time
import json
import PyPDF2
import collections

di = {'Kannada (India)': '63b4094e241a82001d51c602', 'Telugu (India)': '63b41807241a82001d51df88',
              'Amharic (Ethiopia)': '63b40683241a82001d51b026', 'Arabic (Lebanon)': '63b406a8241a82001d51b08b',
              'Pashto (Afghanistan)': '63b409b7241a82001d51c704', 'Malayalam (India)': '63b40977241a82001d51c668',
              'English (United Kingdom)': '63b4075a241a82001d51b70a', 'Arabic (Libya)': '63b406ad241a82001d51b098',
              'Spanish (Nicaragua)': '63b4085f241a82001d51c366', 'German (Germany)': '63b4070d241a82001d51b5f5',
              'German (Switzerland)': '63b40703241a82001d51b19a', 'Dutch (Netherlands)': '63b409ac241a82001d51c6e6',
              'Portuguese (Brazil)': '63b409c3241a82001d51c722', 'Tamil (Sri Lanka)': '63b417f6241a82001d51df5e',
              'Spanish (Mexico)': '63b40855241a82001d51c34a', 'Swedish (Sweden)': '63b417aa241a82001d51dee1',
              'Arabic (Egypt)': '63b40693241a82001d51b051', 'Hindi (India)': '63b408e9241a82001d51c506',
              'Swahili (Kenya)': '63b417b0241a82001d51def3', 'French (France)': '63b408cf241a82001d51c4b6',
              'Afrikaans (South Africa)': '63b403ee241a82001d51a9c7', 'Spanish (Spain)': '63b4081b241a82001d51c2b6',
              'Italian (Italy)': '63b4090d241a82001d51c566', 'Spanish (Puerto Rico)': '63b4086e241a82001d51c38a',
              'English (United States)': '640f477e2babeb0024be4237', 'Catalan (Spain)': '63b406e9241a82001d51b149',
              'English (Australia)': '63b40744241a82001d51b6c2', 'Filipino (Philippines)': '64e2f75736fe21ca612f1637',
              'English (Philippines)': '63b40792241a82001d51b941', 'Spanish (Ecuador)': '63b40805241a82001d51c263',
              'Irish (Ireland)': '63b408d7241a82001d51c4cc', 'Finnish (Finland)': '63b40899241a82001d51c42c',
              'French (Canada)': '64e2f75c36fe21ca612f1657', 'English (Ireland)': '63b4077b241a82001d51b904',
              'Arabic (Kuwait)': '63b406a1241a82001d51b079', 'Korean (South Korea)': '65c0b9a4eb1a522a539db0e8',
              'Armenian (Armenia)': '63b408f8241a82001d51c52a', 'Ukrainian (Ukraine)': '63b41818241a82001d51dfb2',
              'Dutch (Belgium)': '63b409a4241a82001d51c6d4', 'Gujarati (India)': '63b408e1241a82001d51c4ee',
              'Tamil (India)': '63b417b9241a82001d51df0b', 'Georgian (Georgia)': '63b4093e241a82001d51c5de',
              'Arabic (Iraq)': '63b40698241a82001d51b05e', 'Hebrew (Israel)': '63b408e6241a82001d51c4fa',
              'Somali (Somalia)': '63b4176c241a82001d51de97', 'Japanese (Japan)': '64e2f75436fe21ca612f1627',
              'Indonesian (Indonesia)': '63b408fd241a82001d51c536', 'Estonian (Estonia)': '63b4088d241a82001d51c40a',
              'Nepali (Nepal)': '63b4099b241a82001d51c6c2', 'Portuguese (Portugal)': '63b409e6241a82001d51c770',
              'English (New Zealand)': '63b40790241a82001d51b93b', 'Macedonian (Macedonia)': '63b40975241a82001d51c662',
              'Swahili (Tanzania)': '63b417b5241a82001d51deff', 'Persian (Iran)': '63b40894241a82001d51c420',
              'Persian (Iran) Male': '63b40896241a82001d51c426',
              'Danish (Denmark)': '63b406f7241a82001d51b16d', 'Zulu (South Africa)': '63b41883241a82001d51e1e1',
              'Albanian (Albania)': '63b4179f241a82001d51dec3', 'Welsh (United Kingdom)': '63b406f4241a82001d51b167',
              'Spanish (United States)': '64e2f74b36fe21ca612f15eb', 'Thai (Thailand)': '63b4180b241a82001d51df94',
              'Spanish (Guatemala)': '63b40831241a82001d51c2ec', 'Khmer (Cambodia)': '63b40949241a82001d51c5f6',
              'English (Singapore)': '63b40797241a82001d51b94d', 'Galician (Spain)': '63b408da241a82001d51c4dc',
              'English (South Africa)': '63b407dd241a82001d51b9fb', 'Romanian (Romania)': '63b409e9241a82001d51c776',
              'Bulgarian (Bulgaria)': '63b406d6241a82001d51b118',
              'Burmese (Myanmar [Burma])': '63b4098f241a82001d51c6a4', 'Arabic (Tunisia)': '63b406c5241a82001d51b0dd',
              'Spanish (Bolivia)': '63b407e7241a82001d51ba13',
              'Spanish (Equatorial Guinea)': '63b4082d241a82001d51c2e0', 'English (Canada)': '63b40754241a82001d51b6fe',
              'Turkish (Turkey)': '63b41812241a82001d51dfa6', 'Hungarian (Hungary)': '63b408f0241a82001d51c518',
              'Bosnian (Bosnia and Herzegovina)': '63b406e2241a82001d51b136',
              'Polish (Poland)': '63b409af241a82001d51c6ec', 'Arabic (Qatar)': '63b406b8241a82001d51b0b8',
              'Urdu (India)': '63b4181d241a82001d51dfbe', 'Arabic (Jordan)': '63b4069f241a82001d51b073',
              'Arabic (Bahrain)': '63b4068a241a82001d51b039', 'Spanish (Chile)': '63b407f0241a82001d51ba25',
              'Icelandic (Iceland)': '63b40901241a82001d51c542',
              'Spanish (Dominican Republic)': '63b407fd241a82001d51c023',
              'Russian (Russia)': '63b409ee241a82001d51c788', 'Bengali (India)': '63b406df241a82001d51b130',
              'Spanish (Costa Rica)': '63b407f4241a82001d51ba38', 'Arabic (Morocco)': '63b406b1241a82001d51b0a5',
              'Urdu (Pakistan)': '63b41821241a82001d51dfca', 'Slovak (Slovakia)': '63b409fa241a82001d51c7a6',
              'English (Hong Kong SAR China)': '63b40777241a82001d51b8f8',
              'Norwegian Bokmål (Norway)': '63b40997241a82001d51c6b6',
              'Vietnamese (Vietnam)': '63b41828241a82001d51dfdc', 'Spanish (Argentina)': '63b407e4241a82001d51ba0d',
              'English (India)': '63b40781241a82001d51b916', 'Arabic (Oman)': '63b406b5241a82001d51b0b2',
              'Spanish (El Salvador)': '63b40877241a82001d51c3a2', 'Czech (Czech Republic)': '63b406ed241a82001d51b155',
              'Spanish (Honduras)': '63b40836241a82001d51c2f8', 'Spanish (Paraguay)': '63b40873241a82001d51c396',
              'Sinhala (Sri Lanka)': '63b409f4241a82001d51c79a', 'Croatian (Croatia)': '63b408ee241a82001d51c512',
              'German (Austria)': '63b406fe241a82001d51b189', 'Spanish (Uruguay)': '63b40881241a82001d51c3be',
              'Spanish (Panama)': '63b40864241a82001d51c372', 'Maltese (Malta)': '63b4098d241a82001d51c69e',
              'Spanish (Colombia)': '63b407f3241a82001d51ba32', 'French (Belgium)': '63b408a7241a82001d51c450',
              'French (Switzerland)': '63b408b0241a82001d51c468', 'Arabic (Saudi Arabia)': '63b406bb241a82001d51b0c4',
              'Arabic (United Arab Emirates)': '63b40685241a82001d51b02c', 'Arabic (Yemen)': '63b406ca241a82001d51b0f2',
              'Spanish (Venezuela)': '63b40886241a82001d51c3ca', 'Spanish (Peru)': '63b40869241a82001d51c37e',
              'Basque (Spain)': '63b4088f241a82001d51c414', 'Marathi (India)': '63b40980241a82001d51c680',
              'Latvian (Latvia)': '63b4096e241a82001d51c650', 'Slovenian (Slovenia)': '63b409ff241a82001d51c7b2',
              'Lithuanian (Lithuania)': '63b4096c241a82001d51c64a', 'Malay (Malaysia)': '63b40984241a82001d51c68c',
              'Arabic (Syria)': '63b406c3241a82001d51b0d7', 'Greek (Greece)': '63b40729241a82001d51b655',
              'Bengali (Bangladesh)': '63b406d9241a82001d51b11e', 'Arabic (Algeria)': '63b40690241a82001d51b04b'}

# j_url = "https://api.elevenlabs.io/v1/voices"
URL = "https://api.genny.lovo.ai"
# TODAY = str(dt.datetime.now().strftime('%Y-%m-%d'))
#
# TOMORROW = dt.datetime.now() + timedelta(days=1)
# CURRENT_MONTH = "".join(dt.datetime.now().strftime('%Y-%m-%d')).split('-')[1]
# CURRENT_YEAR = "".join(dt.datetime.now().strftime('%Y-%m-%d')).split('-')[0]
# CURRENT_DAY = "".join(TODAY).split('-')[2].split(" ")[0]
# TIME_TO_SEND_EMAIL = dt.datetime(int(CURRENT_YEAR),
#                                  int(CURRENT_MONTH), int(CURRENT_DAY), 19, 23).timestamp()
# print(TIME_TO_SEND_EMAIL)
EMAIL_SENT_DATE = ''
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///todos.db")
app.config['UPLOAD_FILE'] = './static/files'
# Bootstrap5(app)

db = SQLAlchemy()
db.init_app(app)

# ckeditor = CKEditor(app)

login_manager = LoginManager()
login_manager.init_app(app)


def nav_year():
    all_years = []
    unique_todo_date = []
    unique_done_date = []
    todo_date = []
    done_date = []
    result = db.session.execute(db.select(Todos))
    all_todos = result.scalars().all()
    result = db.session.execute(db.select(Done))
    all_dones = result.scalars().all()

    for i in all_todos:
        # to seperate user's items
        if i.user_id == current_user.id:
            todo_date.append(i.due_date)

            # to get rid of duplicat dates
            unique_todo_date = list(set(todo_date))

    for i in all_dones:
        # to separate user's items
        if i.user_id == current_user.id:
            done_date.append(i.due_date)

            # to get rid of duplicat dates
            unique_done_date = list(set(done_date))

    # to sort years
    for date in unique_todo_date:
        year = "".join(date).split('-')[0]
        all_years.append(year)
    all_years = list(set(all_years))

    for date in unique_done_date:
        year = "".join(date).split('-')[0]
        all_years.append(year)
    all_years = list(set(all_years))
    return sorted(list(set(all_years)))


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# class UploadFileForm(FlaskForm):
#     file = FileField('File', validators=[InputRequired()])
#     submit = SubmitField('Upload File')


class Todos(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    info = db.Column(db.String(50), nullable=True)
    due_date = db.Column(db.String)
    done = db.Column(db.Boolean, nullable=True)
    favorites = db.Column(db.Boolean)


class Done(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    info = db.Column(db.String(50), nullable=True)
    due_date = db.Column(db.String)
    done = db.Column(db.Boolean, nullable=True)
    favorites = db.Column(db.Boolean)


class MultimediaFile(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.LargeBinary, nullable=True)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    age = db.Column(db.String, nullable=False)
    tel = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash('You need to log out to access the register page')
        return redirect(url_for('home'))

    psw_hashed_with_salt = generate_password_hash(f"{request.form.get('pswd')}",
                                                  method='pbkdf2:sha256',
                                                  salt_length=8,
                                                  )
    if request.method == "POST":
        new_user = User(
            username=request.form.get("username"),
            age=request.form.get("age"),
            tel=request.form.get("tel"),
            email=request.form.get("email"),
            password=psw_hashed_with_salt,
        )
        # if username is in DB so direct users in login page
        result = db.session.execute(db.Select(User).where(User.email == new_user.email))
        user = result.scalar()
        if user:
            flash(f"*{user.email}*")
            flash("already exist. Log In instead!")
            return redirect(url_for('login'))
        else:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template("register.html")


@app.route("/email123456789")
def admin_email():
    result = db.session.execute(db.select(Todos))
    all_todos = result.scalars().all()
    tomorrow_todos = []
    for date in all_todos:
        if date.due_date == (dt.datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'):
            tomorrow_todos = db.session.execute(
                db.select(Todos).where(
                    Todos.due_date == (dt.datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))).scalars().all()
    print(tomorrow_todos)

    #  preparing title to send to log in user
    if tomorrow_todos:
        todo_title = ''

        for item in tomorrow_todos:
            user = db.get_or_404(User, item.user_id)

            # todo_title is in html because email message is in html format\.
            todo_title = f"""
                                                    <li class="mb-2">{item.info}.</li>
                                                """
            send_email(user.username, user.email, user.tel, msg=todo_title, item_id=item.id)

            send_sms(f"Hi Dear {user.username}\nYou have already sat plan(s) for tomorrow"
                     f"This Email has been sent to you "
                     f"in order to remember what you are going to do by Tomorrow.\n"
                     f"To know more details https://myreminder.onrender.com Click here."
                     f"Your TODO List:\n"
                     f"{item.info}\n", tel=user.tel)

    return render_template('login.html')


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pswd']
        result = db.session.execute(db.Select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash("Email does not exist.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("The password is wrong.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    # result = db.session.execute(db.select(Todos))
    # all_todos = result.scalars().all()
    # tomorrow_todos = []
    # for date in all_todos:
    #     if date.due_date == TOMORROW.strftime('%Y-%m-%d'):
    #         tomorrow_todos = db.session.execute(
    #             db.select(Todos).where(Todos.due_date == TOMORROW.strftime('%Y-%m-%d'))).scalars().all()
    # print(tomorrow_todos)
    #
    # #  preparing title to send to log in user
    # if tomorrow_todos:
    #     todo_title = ''
    #     users = []
    #     for item in tomorrow_todos:
    #         user = db.get_or_404(User, item.user_id)
    #
    #         # todo_title is in html because email message is in html format\.
    #         todo_title = f"""
    #                                             <li class="mb-2">{item.info}.</li>
    #                                         """
    #         print(f"{user.id}-{todo_title}")
    #         send_email(user.username, user.email, user.tel, msg=todo_title)

    return render_template('login.html', logged_in=current_user.is_authenticated)


@app.route("/home", methods=["GET", "POST"])
def home():
    global EMAIL_SENT_DATE

    all_years = []
    unique_todo_date = []
    unique_done_date = []
    todo_date = []
    done_date = []
    result = db.session.execute(db.select(Todos))
    all_todos = result.scalars().all()
    result = db.session.execute(db.select(Done))
    all_dones = result.scalars().all()

    for i in all_todos:
        # to separate user's items
        if i.user_id == current_user.id:
            if f"{i.due_date.split('-')[0]}-{i.due_date.split('-')[1]}" == f"{''.join(dt.datetime.now().strftime('%Y-%m-%d')).split('-')[0]}-{''.join(dt.datetime.now().strftime('%Y-%m-%d')).split('-')[1]}":
                todo_date.append(i.due_date)

                # to get rid of duplicat dates
                unique_todo_date = list(set(todo_date))

    for i in all_dones:
        # to separate user's items
        if i.user_id == current_user.id:
            if f"{i.due_date.split('-')[0]}-{i.due_date.split('-')[1]}" == f"{''.join(dt.datetime.now().strftime('%Y-%m-%d')).split('-')[0]}-{''.join(dt.datetime.now().strftime('%Y-%m-%d')).split('-')[1]}":
                done_date.append(i.due_date)

                # to get rid of duplicat dates
                unique_done_date = list(set(done_date))

    # in order to sort dates
    if todo_date:
        unique_todo_date.sort(key=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'))

    if done_date:
        unique_done_date.sort(key=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'))

    tomorrow_todos = []
    x = []
    nothing_for_this_month = ''
    for date in all_todos:
        if date.user_id == current_user.id:
            if date.due_date == (dt.datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'):
                tomorrow_todos = db.session.execute(
                    db.select(Todos).where(
                        Todos.due_date == (dt.datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))).scalars().all()
            x.append(f'{"".join(date.due_date).split("-")[0]}-{"".join(date.due_date).split("-")[1]}')

            year = "".join(date.due_date).split('-')[0]
            all_years.append(year)
    # on condition that there is not any date it means there is noting to do
    if not f"{''.join(dt.datetime.now().strftime('%Y-%m-%d')).split('-')[0]}-{''.join(dt.datetime.now().strftime('%Y-%m-%d')).split('-')[1]}" in x:
        nothing_for_this_month = True
    # preparing title to send to log in user
    if tomorrow_todos:
        print(tomorrow_todos)
        todo_title = ''
        for item in tomorrow_todos:
            if item.user_id == current_user.id:
                # todo_title is in html because email message is in html format\.
                todo_title += f"""
                                <li class="mb-2">{item.info}.</li>
                            """
    else:
        pass

    # if toto is done the year num stay in years list
    for date in all_dones:
        year = "".join(date.due_date).split('-')[0]
        all_years.append(year)

    return render_template('index.html', todos=all_todos, dones=all_dones,
                           user=current_user, unique_done_date=unique_done_date, unique_todo_date=unique_todo_date,
                           today=str(dt.datetime.now().strftime('%Y-%m-%d')),
                           nothing_for_this_month=nothing_for_this_month,
                           years=sorted(list(set(all_years))), datetime=dt.datetime)


@app.route("/year<int:year>", methods=["GET", "POST"])
def years(year):
    all_years = []
    all_is_done = False
    unique_todo_date = []
    unique_done_date = []
    todo_date = []
    done_date = []
    result = db.session.execute(db.select(Todos))
    all_todos = result.scalars().all()
    result = db.session.execute(db.select(Done))
    all_dones = result.scalars().all()

    for i in all_todos:
        # to seperate user's items
        if i.user_id == current_user.id:
            todo_date.append(i.due_date)

            # to get rid of duplicat dates
            unique_todo_date = list(set(todo_date))

    for i in all_dones:
        # to separate user's items
        if i.user_id == current_user.id:
            done_date.append(i.due_date)

            # to get rid of duplicat dates
            unique_done_date = list(set(done_date))

    # in order to sort dates
    # if todo_date:
    #     unique_todo_date.sort(key=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'))
    #
    # if done_date:
    #     unique_done_date.sort(key=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'))

    # to sort years
    for date in unique_todo_date:
        year = "".join(date).split('-')[0]
        all_years.append(year)
    all_years = list(set(all_years))

    for date in unique_done_date:
        year = "".join(date).split('-')[0]
        all_years.append(year)
    all_years = list(set(all_years))
    # on condition that there is not any date it means there is noting to do
    if not todo_date:
        no_date = True
    else:
        no_date = False

    if not all_todos and not all_dones:
        pass
    elif not all_todos:
        all_is_done = True

    # with app.app_context():
    #     # sending email if there is date of tomorrow in Todo
    #     result = db.session.execute(db.select(Todos))
    #     all_todos = result.scalars().all()
    #     items_for_tomorrow = [todo for todo in all_todos if todo.due_date == TOMORROW.strftime('%Y-%m-%d')]
    #     items = []
    #     for item in items_for_tomorrow:
    #         user = db.get_or_404(User, item.user_id)
    #         if user.id == item.user_id:
    #             items.append(item.user_id)
    #     print(items)

    # email_counts = Counter(emails)
    # # Print the results
    # for email, count in email_counts.items():
    #     print(f"{email} ({count})")

    # db.create_all()

    return render_template('years.html', todos=all_todos, dones=all_dones,
                           user=current_user, unique_done_date=sorted(list(set(unique_done_date))),
                           unique_todo_date=sorted(list(set(unique_todo_date))),
                           today=str(dt.datetime.now().strftime('%Y-%m-%d')), no_date=no_date, all_is_done=all_is_done,
                           years=sorted(list(set(all_years))),
                           selected_year=request.url.split('year')[-1], current_month=dt.datetime.now().strftime("%B"),
                           datetime=dt.datetime)


# it will turn month number to its name
@app.template_filter()
def month_name(month_number):
    try:
        month_number = int(month_number)
        return calendar.month_name[month_number]
    except (ValueError, IndexError):
        return month_number  # Return the original input if not a valid month number


# Register the filter
app.jinja_env.filters['month_name'] = month_name


@app.route("/todo<int:item_id>", methods=["GET", "POST"])
def add_to_done(item_id):
    selected_todo = db.get_or_404(Todos, item_id)
    checked_id = selected_todo.id

    selected_todo = db.get_or_404(Todos, checked_id)
    dones(selected_todo)
    db.session.delete(selected_todo)
    db.session.commit()
    return redirect(url_for('years', year="".join(selected_todo.due_date).split('-')[0]))


# returning to todos
@app.route("/d<int:the_id>", methods=["GET", "POST"])
def d(the_id):
    item = db.get_or_404(Done, the_id)
    new_todo = Todos(
        title=item.title,
        due_date=item.due_date,
        user_id=current_user.id,
        info=item.info
    )
    db.session.add(new_todo)
    db.session.commit()
    item_to_del = db.get_or_404(Done, the_id)
    db.session.delete(item_to_del)
    db.session.commit()
    return redirect(url_for('years', year="".join(item.due_date).split('-')[0]))


@app.route("/add", methods=["GET", "POST"])
def new_todo():
    if request.method == 'POST':
        title = request.form['todo']
        is_unique = db.session.execute(db.select(Todos).where(Todos.title == title)).scalar()
        if is_unique:
            flash('title exist!!!')
            return redirect('#')
        elif not request.form['info'] == "":
            new_todo = Todos(
                due_date=request.form['date'],
                user_id=current_user.id,
                info=request.form['info'][0].capitalize() + request.form['info'][1:],
                title=request.form['todo'][0].capitalize() + request.form['todo'][1:],
            )
            db.session.add(new_todo)
            print(dt.datetime.now().strftime('%Y-%m-%d'))
            if new_todo.due_date < dt.datetime.now().strftime('%Y-%m-%d'):
                flash('Date should be set for following days')
                return redirect(url_for('new_todo'))
            db.session.commit()
            return redirect(url_for('years', year="".join(new_todo.due_date).split('-')[0]))
        else:
            flash('Fill the form please!!!')
            return redirect(url_for('new_todo'))

    return render_template('add_todo.html', years=sorted(list(set(nav_year()))))


@app.route("/done", methods=["GET", "POST"])
def dones(item):
    new_done = Done(
        title=item.title,
        due_date=item.due_date,
        user_id=current_user.id,
        info=item.info
    )
    db.session.add(new_done)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/info<int:item_id>", methods=["GET", "POST"])
def info(item_id):
    item = db.get_or_404(Todos, item_id)
    i = item.info
    if request.method == "POST":
        if i is not None:
            item.info = f"{i}\n{request.form.get('info')}"
        else:
            item.info = f"{' '} \n{request.form.get('info')}"
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('info.html', item=item)


@app.route("/edit<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    item = db.get_or_404(Todos, item_id)
    edit_todo = Todos(
        due_date=item.due_date,
        info=item.info,
        title=item.title,
    )

    if request.method == 'POST':
        item.due_date = request.form['date']
        item.info = request.form['info'][0].capitalize() + request.form['info'][1:]
        item.title = request.form['todo'][0].capitalize() + request.form['todo'][1:]
        db.session.commit()
        return redirect(url_for('home', item_id=item.id))
    return render_template('add_todo.html', item=item, is_edit=True, edit_form=edit_todo,
                           years=sorted(list(set(nav_year()))))


@app.route("/details<int:item_id>", methods=["GET", "POST"])
def details(item_id):
    item = db.get_or_404(Todos, item_id)
    detail = Todos(
        due_date=item.due_date,
        info=item.info,
        title=item.title,
    )
    return render_template('add_todo.html', item=item, is_detail=True, detail=detail,
                           years=sorted(list(set(nav_year()))))


@app.route("/edit-info<int:item_id>", methods=["GET", "POST"])
def edit_info(item_id):
    item = db.get_or_404(Todos, item_id)
    if request.method == 'POST':
        edited_info = request.form.get('edit')
        item.info = edited_info
        db.session.commit()
        return redirect(url_for('info', item_id=item.id))
    return render_template('index.html', item=item, edited_info=True)


@app.route("/del<int:item_id>", methods=["GET", "POST"])
def del_item(item_id):
    item_to_del = db.get_or_404(Todos, item_id)
    print(f"Delete item with id num: {item_id}")
    db.session.delete(item_to_del)
    db.session.commit()
    return redirect(f'/home#{item_id - 1}')


@app.route("/favorite<int:fav_id>", methods=["GET", "POST"])
def add_favorite(fav_id):
    db.get_or_404(Todos, fav_id).favorites = 1
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/del_favorite<int:fav_id>", methods=["GET", "POST"])
def del_favorite(fav_id):
    db.get_or_404(Todos, fav_id).favorites = 0
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/text-to-speech", methods=["GET", "POST"])
def tts():
    if current_user.is_authenticated:

        try:
            os.mkdir(f"{os.path.join(os.path.abspath(os.path.dirname('__file__')))}/{app.config['UPLOAD_FILE']}")
        except FileExistsError:
            pass
        t = ''
        # related to file upload
        if 'file' in request.files:
            file = request.files['file']
            if file:
                file.save(
                    os.path.join(os.path.abspath(os.path.dirname('__file__')), app.config['UPLOAD_FILE'],
                                 secure_filename(file.filename)))

                # Open the PDF file
                pdf_file = open(f'./static/files/{file.filename}', 'rb')

                # Create a PDF reader object
                pdf_reader = PyPDF2.PdfFileReader(pdf_file)

                # Get the number of pages in the PDF file
                num_pages = pdf_reader.numPages

                # Loop through all the pages and extract the text
                for page in range(num_pages):
                    page_obj = pdf_reader.getPage(page)
                    # print(page_obj.extractText())
                    t += page_obj.extractText()
                # Close the PDF file
                pdf_file.close()

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-KEY": os.environ.get('X-API-KEY')
            # "X-API-KEY": os.environ.get('X-API-KEY'),
        }

        # GET Speakers
        speakers = requests.get(f"{URL}/api/v1/speakers", headers=headers).json()
        data = speakers['data']

        data_length = int(speakers["totalCount"])



        sound_url = None
        if request.method == 'POST':
            try:
                speaker_id = request.form['voice_num']
            except KeyError:
                flash('please select a voice')
                return redirect(f'/text-to-speech#Select')

            tts_body = {
                "speaker": speaker_id,
                "text": request.form['textarea']
            }

            tts_job = requests.post(f"{URL}/api/v1/tts", headers=headers, data=json.dumps(tts_body)).json()
            try:
                job_id = tts_job['id']
            except KeyError:
                flash('please select a voice')
                return redirect(f'/text-to-speech#Select')

            # GET JOB - Fetch until TTS Job is complete
            job_complete = False
            tts_url = ''
            max_retries = 120
            retry_count = 0

            while not job_complete:
                job_res = requests.get(f'{URL}/api/v1/tts/{job_id}', headers=headers).json()
                status = job_res['status']
                if (status != 'done'):
                    time.sleep(1)
                    retry_count += 1
                else:
                    job_complete = True
                    tts_url = job_res['data'][0]['urls'][0]


            # print(f'TTS file is available at: {tts_url}')
            return render_template('TTS.html', sound_url=tts_url, data=data, data_length=data_length,
                                   di=di, text=t)
        return render_template('TTS.html', data=data, data_length=data_length, sound_url=sound_url,
                               di=di, text=t)
    else:
        flash("login please")
        return redirect(url_for('login'))


@app.route("/pdf-to-speech", methods=['GET', "POST"])
def pdf_to_speech():
    try:
        os.mkdir(f"{os.path.join(os.path.abspath(os.path.dirname('__file__')))}/{app.config['UPLOAD_FILE']}")
    except FileExistsError:
        pass
    # related to file upload
    if 'file' in request.files:
        file = request.files['file']
        if file:
            file.save(
                os.path.join(os.path.abspath(os.path.dirname('__file__')), app.config['UPLOAD_FILE'],
                             secure_filename(file.filename)))

            # Open the PDF file
            pdf_file = open(f'./static/files/{file.filename}', 'rb')

            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)

            # Get the number of pages in the PDF file
            num_pages = pdf_reader.numPages
            t = ''
            # Loop through all the pages and extract the text
            for page in range(num_pages):
                page_obj = pdf_reader.getPage(page)
                # print(page_obj.extractText())
                t += page_obj.extractText()
            # Close the PDF file

            pdf_file.close()
            return render_template('TTS.html', text=t, di=di)

        return flash('No file provided.')
    return render_template('TTS.html')

    # form = UploadFileForm()
    # if form.validate_on_submit():
    #     file = form.file.data
    #     print(file)
    #     # with open(file, mode='rb') as f:
    #     #     file_content = f.read()
    #     # print(file_content)
    #     # file.save(os.path.join(os.path.abspath(os.path.dirname('__file__')), app.config['SQLALCHEMY_DATABASE_URI'],
    #     #                        secure_filename(file.filename)))
    #     print(os.path.join(os.path.abspath(os.path.dirname("__file__"))))
    #     return "File has been Uploaded"
    # return render_template('pdf-to-speech.html', form=form)



if __name__ == "__main__":
    app.run(port=5002, debug=True)
