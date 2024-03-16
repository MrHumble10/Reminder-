from flask import Flask, render_template, redirect, url_for, request, flash, abort
# from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
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
import collections

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

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///todos.db")

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
        # result = requests.get(url=j_url)
        # data = result.json()['voices']
        # data_length = len(data)
        # LANGUAGE_BY_LOCALE = {
        #     "af_NA": "Afrikaans (Namibia)",
        #     "af_ZA": "Afrikaans (South Africa)",
        #     "af": "Afrikaans",
        #     "ak_GH": "Akan (Ghana)",
        #     "ak": "Akan",
        #     "sq_AL": "Albanian (Albania)",
        #     "sq": "Albanian",
        #     "am_ET": "Amharic (Ethiopia)",
        #     "am": "Amharic",
        #     "ar_DZ": "Arabic (Algeria)",
        #     "ar_BH": "Arabic (Bahrain)",
        #     "ar_EG": "Arabic (Egypt)",
        #     "ar_IQ": "Arabic (Iraq)",
        #     "ar_JO": "Arabic (Jordan)",
        #     "ar_KW": "Arabic (Kuwait)",
        #     "ar_LB": "Arabic (Lebanon)",
        #     "ar_LY": "Arabic (Libya)",
        #     "ar_MA": "Arabic (Morocco)",
        #     "ar_OM": "Arabic (Oman)",
        #     "ar_QA": "Arabic (Qatar)",
        #     "ar_SA": "Arabic (Saudi Arabia)",
        #     "ar_SD": "Arabic (Sudan)",
        #     "ar_SY": "Arabic (Syria)",
        #     "ar_TN": "Arabic (Tunisia)",
        #     "ar_AE": "Arabic (United Arab Emirates)",
        #     "ar_YE": "Arabic (Yemen)",
        #     "ar": "Arabic",
        #     "hy_AM": "Armenian (Armenia)",
        #     "hy": "Armenian",
        #     "as_IN": "Assamese (India)",
        #     "as": "Assamese",
        #     "asa_TZ": "Asu (Tanzania)",
        #     "asa": "Asu",
        #     "az_Cyrl": "Azerbaijani (Cyrillic)",
        #     "az_Cyrl_AZ": "Azerbaijani (Cyrillic, Azerbaijan)",
        #     "az_Latn": "Azerbaijani (Latin)",
        #     "az_Latn_AZ": "Azerbaijani (Latin, Azerbaijan)",
        #     "az": "Azerbaijani",
        #     "bm_ML": "Bambara (Mali)",
        #     "bm": "Bambara",
        #     "eu_ES": "Basque (Spain)",
        #     "eu": "Basque",
        #     "be_BY": "Belarusian (Belarus)",
        #     "be": "Belarusian",
        #     "bem_ZM": "Bemba (Zambia)",
        #     "bem": "Bemba",
        #     "bez_TZ": "Bena (Tanzania)",
        #     "bez": "Bena",
        #     "bn_BD": "Bengali (Bangladesh)",
        #     "bn_IN": "Bengali (India)",
        #     "bn": "Bengali",
        #     "bs_BA": "Bosnian (Bosnia and Herzegovina)",
        #     "bs": "Bosnian",
        #     "bg_BG": "Bulgarian (Bulgaria)",
        #     "bg": "Bulgarian",
        #     "my_MM": "Burmese (Myanmar [Burma])",
        #     "my": "Burmese",
        #     "yue_Hant_HK": "Cantonese (Traditional, Hong Kong SAR China)",
        #     "ca_ES": "Catalan (Spain)",
        #     "ca": "Catalan",
        #     "tzm_Latn": "Central Morocco Tamazight (Latin)",
        #     "tzm_Latn_MA": "Central Morocco Tamazight (Latin, Morocco)",
        #     "tzm": "Central Morocco Tamazight",
        #     "chr_US": "Cherokee (United States)",
        #     "chr": "Cherokee",
        #     "cgg_UG": "Chiga (Uganda)",
        #     "cgg": "Chiga",
        #     "zh_Hans": "Chinese (Simplified Han)",
        #     "zh_Hans_CN": "Chinese (Simplified Han, China)",
        #     "zh_Hans_HK": "Chinese (Simplified Han, Hong Kong SAR China)",
        #     "zh_Hans_MO": "Chinese (Simplified Han, Macau SAR China)",
        #     "zh_Hans_SG": "Chinese (Simplified Han, Singapore)",
        #     "zh_Hant": "Chinese (Traditional Han)",
        #     "zh_Hant_HK": "Chinese (Traditional Han, Hong Kong SAR China)",
        #     "zh_Hant_MO": "Chinese (Traditional Han, Macau SAR China)",
        #     "zh_Hant_TW": "Chinese (Traditional Han, Taiwan)",
        #     "zh": "Chinese",
        #     "kw_GB": "Cornish (United Kingdom)",
        #     "kw": "Cornish",
        #     "hr_HR": "Croatian (Croatia)",
        #     "hr": "Croatian",
        #     "cs_CZ": "Czech (Czech Republic)",
        #     "cs": "Czech",
        #     "da_DK": "Danish (Denmark)",
        #     "da": "Danish",
        #     "nl_BE": "Dutch (Belgium)",
        #     "nl_NL": "Dutch (Netherlands)",
        #     "nl": "Dutch",
        #     "ebu_KE": "Embu (Kenya)",
        #     "ebu": "Embu",
        #     "en_AS": "English (American Samoa)",
        #     "en_AU": "English (Australia)",
        #     "en_BE": "English (Belgium)",
        #     "en_BZ": "English (Belize)",
        #     "en_BW": "English (Botswana)",
        #     "en_CA": "English (Canada)",
        #     "en_GU": "English (Guam)",
        #     "en_HK": "English (Hong Kong SAR China)",
        #     "en_IN": "English (India)",
        #     "en_IE": "English (Ireland)",
        #     "en_IL": "English (Israel)",
        #     "en_JM": "English (Jamaica)",
        #     "en_MT": "English (Malta)",
        #     "en_MH": "English (Marshall Islands)",
        #     "en_MU": "English (Mauritius)",
        #     "en_NA": "English (Namibia)",
        #     "en_NZ": "English (New Zealand)",
        #     "en_MP": "English (Northern Mariana Islands)",
        #     "en_PK": "English (Pakistan)",
        #     "en_PH": "English (Philippines)",
        #     "en_SG": "English (Singapore)",
        #     "en_ZA": "English (South Africa)",
        #     "en_TT": "English (Trinidad and Tobago)",
        #     "en_UM": "English (U.S. Minor Outlying Islands)",
        #     "en_VI": "English (U.S. Virgin Islands)",
        #     "en_GB": "English (United Kingdom)",
        #     "en_US": "English (United States)",
        #     "en_ZW": "English (Zimbabwe)",
        #     "en": "English",
        #     "eo": "Esperanto",
        #     "et_EE": "Estonian (Estonia)",
        #     "et": "Estonian",
        #     "ee_GH": "Ewe (Ghana)",
        #     "ee_TG": "Ewe (Togo)",
        #     "ee": "Ewe",
        #     "fa_IR": "()",
        #     "fo_FO": "Faroese (Faroe Islands)",
        #     "fo": "Faroese",
        #     "fil_PH": "Filipino (Philippines)",
        #     "fil": "Filipino",
        #     "fi_FI": "Finnish (Finland)",
        #     "fi": "Finnish",
        #     "fr_BE": "French (Belgium)",
        #     "fr_BJ": "French (Benin)",
        #     "fr_BF": "French (Burkina Faso)",
        #     "fr_BI": "French (Burundi)",
        #     "fr_CM": "French (Cameroon)",
        #     "fr_CA": "French (Canada)",
        #     "fr_CF": "French (Central African Republic)",
        #     "fr_TD": "French (Chad)",
        #     "fr_KM": "French (Comoros)",
        #     "fr_CG": "French (Congo - Brazzaville)",
        #     "fr_CD": "French (Congo - Kinshasa)",
        #     "fr_CI": "French (Côte d’Ivoire)",
        #     "fr_DJ": "French (Djibouti)",
        #     "fr_GQ": "French (Equatorial Guinea)",
        #     "fr_FR": "French (France)",
        #     "fr_GA": "French (Gabon)",
        #     "fr_GP": "French (Guadeloupe)",
        #     "fr_GN": "French (Guinea)",
        #     "fr_LU": "French (Luxembourg)",
        #     "fr_MG": "French (Madagascar)",
        #     "fr_ML": "French (Mali)",
        #     "fr_MQ": "French (Martinique)",
        #     "fr_MC": "French (Monaco)",
        #     "fr_NE": "French (Niger)",
        #     "fr_RW": "French (Rwanda)",
        #     "fr_RE": "French (Réunion)",
        #     "fr_BL": "French (Saint Barthélemy)",
        #     "fr_MF": "French (Saint Martin)",
        #     "fr_SN": "French (Senegal)",
        #     "fr_CH": "French (Switzerland)",
        #     "fr_TG": "French (Togo)",
        #     "fr": "French",
        #     "ff_SN": "Fulah (Senegal)",
        #     "ff": "Fulah",
        #     "gl_ES": "Galician (Spain)",
        #     "gl": "Galician",
        #     "lg_UG": "Ganda (Uganda)",
        #     "lg": "Ganda",
        #     "ka_GE": "Georgian (Georgia)",
        #     "ka": "Georgian",
        #     "de_AT": "German (Austria)",
        #     "de_BE": "German (Belgium)",
        #     "de_DE": "German (Germany)",
        #     "de_LI": "German (Liechtenstein)",
        #     "de_LU": "German (Luxembourg)",
        #     "de_CH": "German (Switzerland)",
        #     "de": "German",
        #     "el_CY": "Greek (Cyprus)",
        #     "el_GR": "Greek (Greece)",
        #     "el": "Greek",
        #     "gu_IN": "Gujarati (India)",
        #     "gu": "Gujarati",
        #     "guz_KE": "Gusii (Kenya)",
        #     "guz": "Gusii",
        #     "ha_Latn": "Hausa (Latin)",
        #     "ha_Latn_GH": "Hausa (Latin, Ghana)",
        #     "ha_Latn_NE": "Hausa (Latin, Niger)",
        #     "ha_Latn_NG": "Hausa (Latin, Nigeria)",
        #     "ha": "Hausa",
        #     "haw_US": "Hawaiian (United States)",
        #     "haw": "Hawaiian",
        #     "he_IL": "Hebrew (Israel)",
        #     "he": "Hebrew",
        #     "hi_IN": "Hindi (India)",
        #     "hi": "Hindi",
        #     "hu_HU": "Hungarian (Hungary)",
        #     "hu": "Hungarian",
        #     "is_IS": "Icelandic (Iceland)",
        #     "is": "Icelandic",
        #     "ig_NG": "Igbo (Nigeria)",
        #     "ig": "Igbo",
        #     "id_ID": "Indonesian (Indonesia)",
        #     "id": "Indonesian",
        #     "ga_IE": "Irish (Ireland)",
        #     "ga": "Irish",
        #     "it_IT": "Italian (Italy)",
        #     "it_CH": "Italian (Switzerland)",
        #     "it": "Italian",
        #     "ja_JP": "Japanese (Japan)",
        #     "ja": "Japanese",
        #     "kea_CV": "Kabuverdianu (Cape Verde)",
        #     "kea": "Kabuverdianu",
        #     "kab_DZ": "Kabyle (Algeria)",
        #     "kab": "Kabyle",
        #     "kl_GL": "Kalaallisut (Greenland)",
        #     "kl": "Kalaallisut",
        #     "kln_KE": "Kalenjin (Kenya)",
        #     "kln": "Kalenjin",
        #     "kam_KE": "Kamba (Kenya)",
        #     "kam": "Kamba",
        #     "kn_IN": "Kannada (India)",
        #     "kn": "Kannada",
        #     "kk_Cyrl": "Kazakh (Cyrillic)",
        #     "kk_Cyrl_KZ": "Kazakh (Cyrillic, Kazakhstan)",
        #     "kk": "Kazakh",
        #     "km_KH": "Khmer (Cambodia)",
        #     "km": "Khmer",
        #     "ki_KE": "Kikuyu (Kenya)",
        #     "ki""": "Kikuyu",
        #     "rw_RW": "Kinyarwanda (Rwanda)",
        #     "rw": "Kinyarwanda",
        #     "kok_IN": "Konkani (India)",
        #     "kok": "Konkani",
        #     "ko_KR": "Korean (South Korea)",
        #     "ko": "Korean",
        #     "khq_ML": "Koyra Chiini (Mali)",
        #     "khq": "Koyra Chiini",
        #     "ses_ML": "Koyraboro Senni (Mali)",
        #     "ses": "Koyraboro Senni",
        #     "lag_TZ": "Langi (Tanzania)",
        #     "lag": "Langi",
        #     "lv_LV": "Latvian (Latvia)",
        #     "lv": "Latvian",
        #     "lt_LT": "Lithuanian (Lithuania)",
        #     "lt": "Lithuanian",
        #     "luo_KE": "Luo (Kenya)",
        #     "luo": "Luo",
        #     "luy_KE": "Luyia (Kenya)",
        #     "luy": "Luyia",
        #     "mk_MK": "Macedonian (Macedonia)",
        #     "mk": "Macedonian",
        #     "jmc_TZ": "Machame (Tanzania)",
        #     "jmc": "Machame",
        #     "kde_TZ": "Makonde (Tanzania)",
        #     "kde": "Makonde",
        #     "mg_MG": "Malagasy (Madagascar)",
        #     "mg": "Malagasy",
        #     "ms_BN": "Malay (Brunei)",
        #     "ms_MY": "Malay (Malaysia)",
        #     "ms": "Malay",
        #     "ml_IN": "Malayalam (India)",
        #     "ml": "Malayalam",
        #     "mt_MT": "Maltese (Malta)",
        #     "mt": "Maltese",
        #     "gv_GB": "Manx (United Kingdom)",
        #     "gv": "Manx",
        #     "mr_IN": "Marathi (India)",
        #     "mr": "Marathi",
        #     "mas_KE": "Masai (Kenya)",
        #     "mas_TZ": "Masai (Tanzania)",
        #     "mas": "Masai",
        #     "mer_KE": "Meru (Kenya)",
        #     "mer": "Meru",
        #     "mfe_MU": "Morisyen (Mauritius)",
        #     "mfe": "Morisyen",
        #     "naq_NA": "Nama (Namibia)",
        #     "naq": "Nama",
        #     "ne_IN": "Nepali (India)",
        #     "ne_NP": "Nepali (Nepal)",
        #     "ne": "Nepali",
        #     "nd_ZW": "North Ndebele (Zimbabwe)",
        #     "nd": "North Ndebele",
        #     "nb_NO": "Norwegian Bokmål (Norway)",
        #     "nb": "Norwegian Bokmål",
        #     "nn_NO": "Norwegian Nynorsk (Norway)",
        #     "nn": "Norwegian Nynorsk",
        #     "nyn_UG": "Nyankole (Uganda)",
        #     "nyn": "Nyankole",
        #     "or_IN": "Oriya (India)",
        #     "or": "Oriya",
        #     "om_ET": "Oromo (Ethiopia)",
        #     "om_KE": "Oromo (Kenya)",
        #     "om": "Oromo",
        #     "ps_AF": "Pashto (Afghanistan)",
        #     "ps": "Pashto",
        #     "fa_AF": "Persian (Afghanistan)",
        #     "fa_IR": "Persian (Iran)",
        #     "fa": "Persian",
        #     "pl_PL": "Polish (Poland)",
        #     "pl": "Polish",
        #     "pt_BR": "Portuguese (Brazil)",
        #     "pt_GW": "Portuguese (Guinea-Bissau)",
        #     "pt_MZ": "Portuguese (Mozambique)",
        #     "pt_PT": "Portuguese (Portugal)",
        #     "pt": "Portuguese",
        #     "pa_Arab": "Punjabi (Arabic)",
        #     "pa_Arab_PK": "Punjabi (Arabic, Pakistan)",
        #     "pa_Guru": "Punjabi (Gurmukhi)",
        #     "pa_Guru_IN": "Punjabi (Gurmukhi, India)",
        #     "pa": "Punjabi",
        #     "ro_MD": "Romanian (Moldova)",
        #     "ro_RO": "Romanian (Romania)",
        #     "ro": "Romanian",
        #     "rm_CH": "Romansh (Switzerland)",
        #     "rm": "Romansh",
        #     "rof_TZ": "Rombo (Tanzania)",
        #     "rof": "Rombo",
        #     "ru_MD": "Russian (Moldova)",
        #     "ru_RU": "Russian (Russia)",
        #     "ru_UA": "Russian (Ukraine)",
        #     "ru": "Russian",
        #     "rwk_TZ": "Rwa (Tanzania)",
        #     "rwk": "Rwa",
        #     "saq_KE": "Samburu (Kenya)",
        #     "saq": "Samburu",
        #     "sg_CF": "Sango (Central African Republic)",
        #     "sg": "Sango",
        #     "seh_MZ": "Sena (Mozambique)",
        #     "seh": "Sena",
        #     "sr_Cyrl": "Serbian (Cyrillic)",
        #     "sr_Cyrl_BA": "Serbian (Cyrillic, Bosnia and Herzegovina)",
        #     "sr_Cyrl_ME": "Serbian (Cyrillic, Montenegro)",
        #     "sr_Cyrl_RS": "Serbian (Cyrillic, Serbia)",
        #     "sr_Latn": "Serbian (Latin)",
        #     "sr_Latn_BA": "Serbian (Latin, Bosnia and Herzegovina)",
        #     "sr_Latn_ME": "Serbian (Latin, Montenegro)",
        #     "sr_Latn_RS": "Serbian (Latin, Serbia)",
        #     "sr": "Serbian",
        #     "sn_ZW": "Shona (Zimbabwe)",
        #     "sn": "Shona",
        #     "ii_CN": "Sichuan Yi (China)",
        #     "ii": "Sichuan Yi",
        #     "si_LK": "Sinhala (Sri Lanka)",
        #     "si": "Sinhala",
        #     "sk_SK": "Slovak (Slovakia)",
        #     "sk": "Slovak",
        #     "sl_SI": "Slovenian (Slovenia)",
        #     "sl": "Slovenian",
        #     "xog_UG": "Soga (Uganda)",
        #     "xog": "Soga",
        #     "so_DJ": "Somali (Djibouti)",
        #     "so_ET": "Somali (Ethiopia)",
        #     "so_KE": "Somali (Kenya)",
        #     "so_SO": "Somali (Somalia)",
        #     "so": "Somali",
        #     "es_AR": "Spanish (Argentina)",
        #     "es_BO": "Spanish (Bolivia)",
        #     "es_CL": "Spanish (Chile)",
        #     "es_CO": "Spanish (Colombia)",
        #     "es_CR": "Spanish (Costa Rica)",
        #     "es_DO": "Spanish (Dominican Republic)",
        #     "es_EC": "Spanish (Ecuador)",
        #     "es_SV": "Spanish (El Salvador)",
        #     "es_GQ": "Spanish (Equatorial Guinea)",
        #     "es_GT": "Spanish (Guatemala)",
        #     "es_HN": "Spanish (Honduras)",
        #     "es_419": "Spanish (Latin America)",
        #     "es_MX": "Spanish (Mexico)",
        #     "es_NI": "Spanish (Nicaragua)",
        #     "es_PA": "Spanish (Panama)",
        #     "es_PY": "Spanish (Paraguay)",
        #     "es_PE": "Spanish (Peru)",
        #     "es_PR": "Spanish (Puerto Rico)",
        #     "es_ES": "Spanish (Spain)",
        #     "es_US": "Spanish (United States)",
        #     "es_UY": "Spanish (Uruguay)",
        #     "es_VE": "Spanish (Venezuela)",
        #     "es": "Spanish",
        #     "sw_KE": "Swahili (Kenya)",
        #     "sw_TZ": "Swahili (Tanzania)",
        #     "sw": "Swahili",
        #     "sv_FI": "Swedish (Finland)",
        #     "sv_SE": "Swedish (Sweden)",
        #     "sv": "Swedish",
        #     "gsw_CH": "Swiss German (Switzerland)",
        #     "gsw": "Swiss German",
        #     "shi_Latn": "Tachelhit (Latin)",
        #     "shi_Latn_MA": "Tachelhit (Latin, Morocco)",
        #     "shi_Tfng": "Tachelhit (Tifinagh)",
        #     "shi_Tfng_MA": "Tachelhit (Tifinagh, Morocco)",
        #     "shi": "Tachelhit",
        #     "dav_KE": "Taita (Kenya)",
        #     "dav": "Taita",
        #     "ta_IN": "Tamil (India)",
        #     "ta_LK": "Tamil (Sri Lanka)",
        #     "ta": "Tamil",
        #     "te_IN": "Telugu (India)",
        #     "te": "Telugu",
        #     "teo_KE": "Teso (Kenya)",
        #     "teo_UG": "Teso (Uganda)",
        #     "teo": "Teso",
        #     "th_TH": "Thai (Thailand)",
        #     "th": "Thai",
        #     "bo_CN": "Tibetan (China)",
        #     "bo_IN": "Tibetan (India)",
        #     "bo": "Tibetan",
        #     "ti_ER": "Tigrinya (Eritrea)",
        #     "ti_ET": "Tigrinya (Ethiopia)",
        #     "ti": "Tigrinya",
        #     "to_TO": "Tonga (Tonga)",
        #     "to": "Tonga",
        #     "tr_TR": "Turkish (Turkey)",
        #     "tr": "Turkish",
        #     "uk_UA": "Ukrainian (Ukraine)",
        #     "uk": "Ukrainian",
        #     "ur_IN": "Urdu (India)",
        #     "ur_PK": "Urdu (Pakistan)",
        #     "ur": "Urdu",
        #     "uz_Arab": "Uzbek (Arabic)",
        #     "uz_Arab_AF": "Uzbek (Arabic, Afghanistan)",
        #     "uz_Cyrl": "Uzbek (Cyrillic)",
        #     "uz_Cyrl_UZ": "Uzbek (Cyrillic, Uzbekistan)",
        #     "uz_Latn": "Uzbek (Latin)",
        #     "uz_Latn_UZ": "Uzbek (Latin, Uzbekistan)",
        #     "uz": "Uzbek",
        #     "vi_VN": "Vietnamese (Vietnam)",
        #     "vi": "Vietnamese",
        #     "vun_TZ": "Vunjo (Tanzania)",
        #     "vun": "Vunjo",
        #     "cy_GB": "Welsh (United Kingdom)",
        #     "cy": "Welsh",
        #     "yo_NG": "Yoruba (Nigeria)",
        #     "yo": "Yoruba",
        #     "zu_ZA": "Zulu (South Africa)",
        #     "zu": "Zulu"
        # }
        # voices = {'Rachel': '21m00Tcm4TlvDq8ikWAM', 'Drew': '29vD33N1CtxCmqQRPOHJ', 'Clyde': '2EiwWnXFnvU5JabPnv8n',
        #           'Paul': '5Q0t7uMcjvnagumLfvZi', 'Domi': 'AZnzlk1XvdvUeBnXmlld', 'Dave': 'CYw3kZ02Hs0563khs1Fj',
        #           'Fin': 'D38z5RcWu1voky8WS1ja', 'Sarah': 'EXAVITQu4vr4xnSDxMaL', 'Antoni': 'ErXwobaYiN019PkySvjV',
        #           'Thomas': 'GBv7mTt0atIp3Br8iCZE', 'Charlie': 'IKne3meq5aSn9XLyUdCD', 'George': 'JBFqnCBsd6RMkjVDRZzb',
        #           'Emily': 'LcfcDJNUP1GQjkzn1xUU', 'Elli': 'MF3mGyEYCl7XYWbV9V6O', 'Callum': 'N2lVS1w4EtoT3dr4eOWO',
        #           'Patrick': 'ODq5zmih8GrVes37Dizd', 'Harry': 'SOYHLrjzK2X1ezoPC6cr', 'Liam': 'TX3LPaxmHKxFdv7VOQHJ',
        #           'Dorothy': 'ThT5KcBeYPX3keUQqHPh', 'Josh': 'TxGEqnHWrfWFTfGW9XjX', 'Arnold': 'VR6AewLTigWG4xSOukaG',
        #           'Charlotte': 'XB0fDUnXU5powFXDhCwa', 'Alice': 'Xb7hH8MSUJpSbSDYk0k2',
        #           'Matilda': 'XrExE9yKIg1WjnnlVkGX', 'Matthew': 'Yko7PKHZNXotIFUBG7I9', 'James': 'ZQe5CZNOzWyzPSCn5a3c',
        #           'Joseph': 'Zlb1dXrM653N07WRdFW3', 'Jeremy': 'bVMeCyTHy58xNoL34h3p', 'Michael': 'flq6f7yk4E4fJM5XTYuZ',
        #           'Ethan': 'g5CIjZEefAph4nQFvHAz', 'Chris': 'iP95p4xoKVk53GoZ742B', 'Gigi': 'jBpfuIE2acCO8z3wKNLl',
        #           'Freya': 'jsCqWAovK2LkecY7zXl4', 'Brian': 'nPczCjzI2devNBz1zQrb', 'Grace': 'oWAxZDx7w5VEj9dCyTzz',
        #           'Daniel': 'onwK4e9ZLuTAKqWW03F9', 'Lily': 'pFZP5JQG7iQjIQuC4Bku', 'Serena': 'pMsXgVXv3BLzUgSXRplE',
        #           'Adam': 'pNInz6obpgDQGcFmaJgB', 'Nicole': 'piTKgcLEGmPE4e6mEKli', 'Bill': 'pqHfZKP75CvOlQylNhV4',
        #           'Jessie': 't0jbNlBVZ17f02VDIeMI', 'Sam': 'yoZ06aMxZJJ28mfd3POQ', 'Glinda': 'z9fAnlkpzviPz146aGWa',
        #           'Giovanni': 'zcAOhNBS3c14rBihAFp1', 'Mimi': 'zrHiDhphv9ZnVXBqCLjz'}
        #
        # # for num in range(data_length):
        # #     print(num)
        # #     #     print(data[num]['name'])
        # #     #     print(data[num]['voice_id'])
        # #     voices[f"{data[num]['name']}"] = f"{data[num]['voice_id']}"
        # # # int("".join(request.url.split('=')[1]))
        # # print(voices)
        #

        headers = {
            "accept": "application/json",
            "content-type": "application/json",

            "X-API-KEY": os.environ.get('X-API-KEY'),
        }


        # GET Speakers
        speakers = requests.get(f"{URL}/api/v1/speakers", headers=headers).json()
        data = speakers['data']


        data_length = int(speakers["totalCount"])

        # to make a dict include languages and locales
        # di = {}
        # for num in range(data_length):
        #     dat = data[num]['locale'].replace('-', "_")
        #     # if d not in locale_list:
        #     try:
        #         di[LANGUAGE_BY_LOCALE[dat]] = data[num]['id']
        #     except KeyError:
        #         print(f'{dat} does not exist.')
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

        # def merge_dicts(*dicts):
        #     """
        #     Merges dictionaries, retaining values for duplicate keys.
        #     Args:
        #         *dicts: Variable number of dictionaries to merge.
        #     Returns:
        #         dict: A new dictionary with lists of values for duplicate keys.
        #     """
        #     result = collections.defaultdict(list)
        #     for d in dicts:
        #         for k, v in d.items():
        #             result[k].append(v)
        #     return dict(result)
        #
        # # Example usage:
        # # d1 = {'a': 1, 'b': 2}
        # # d2 = {'c': 3, 'b': 4}
        # # d3 = {'a': 5, 'd': 6}
        #
        # new_dict = merge_dicts(di)
        # print(new_dict)


        # for loc in locale_list:
        #     try:
        #         print(LANGUAGE_BY_LOCALE[loc])
        #     except KeyError:
        #         print(f'{loc} does not exist.')


        # print(f'Fetched a total of # {speakers["totalCount"]} speakers!')
        sound_url = None
        if request.method == 'POST':
            # selected_voice_num = int(request.form['voice_num'])
            # speaker_id = speakers['data'][selected_voice_num]['id']
            speaker_id = request.form['voice_num']
            # print(f'The speaker ID we will use is {speaker_id}')
            # print(selected_voice_id)
            # print(request.form['voice_num'])
            # print(request.form['textarea'])
            # Text to speech
            #     CHUNK_SIZE = 1024
            #     url = f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice_id}"
            #
            #     headers = {
            #         "Accept": "audio/mpeg",
            #         "Content-Type": "application/json",
            #         "xi-api-key": os.environ.get('xi-api-key')
            #     }
            #
            #     data = {
            #         "text": request.form['textarea'],
            #         "model_id": "eleven_monolingual_v1",
            #         "voice_settings": {
            #             "stability": 0.5,
            #             "similarity_boost": 0.5
            #         }
            #     }
            #
            #     response = requests.post(url, json=data, headers=headers)
            #     with open("./static/output.mp3", "wb") as f:
            #         for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            #             if chunk:
            #                 f.write(chunk)

            # You can find specific speakerId with the below using the displayName you can see in Genny Web.
            # speaker_found = next(filter(lambda speaker: speaker['displayName'] == 'Chloe Woods', speakers['data']), None)
            # print(speaker_found)

            # POST TTS (Async)
            tts_body = {
                "speaker": speaker_id,
                "text": request.form['textarea']
            }

            tts_job = requests.post(f"{URL}/api/v1/tts", headers=headers, data=json.dumps(tts_body)).json()
            job_id = tts_job['id']
            # print(f'TTS Job is created with ID: {job_id}')

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
            return render_template('TTS.html', sound_url=tts_url, data=data, data_length=data_length, di=di)
        return render_template('TTS.html', data=data, data_length=data_length, sound_url=sound_url, di=di)
    else:
        flash("login please")
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(port=5002, debug=True)
