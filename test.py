
from flask import Flask, render_template, redirect, url_for, request, flash, abort
# from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user
from notification import send_email
import os
# from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
import datetime as dt
from datetime import timedelta
import calendar
from collections import Counter

TODAY = str(dt.datetime.now().strftime('%Y-%m-%d'))

TOMORROW = dt.datetime.now() + timedelta(days=1)
CURRENT_MONTH = "".join(TODAY).split('-')[1]
CURRENT_YEAR = "".join(TODAY).split('-')[0]
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


@app.route("/email123456789", methods=["GET", "POST"])
def admin_email():
    result = db.session.execute(db.select(Todos))
    all_todos = result.scalars().all()
    tomorrow_todos = []
    for date in all_todos:
        if date.due_date == TOMORROW.strftime('%Y-%m-%d'):
            tomorrow_todos = db.session.execute(
                db.select(Todos).where(Todos.due_date == TOMORROW.strftime('%Y-%m-%d'))).scalars().all()
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
            if f"{i.due_date.split('-')[0]}-{i.due_date.split('-')[1]}" == f"{CURRENT_YEAR}-{CURRENT_MONTH}":
                todo_date.append(i.due_date)

                # to get rid of duplicat dates
                unique_todo_date = list(set(todo_date))

    for i in all_dones:
        # to separate user's items
        if i.user_id == current_user.id:
            if f"{i.due_date.split('-')[0]}-{i.due_date.split('-')[1]}" == f"{CURRENT_YEAR}-{CURRENT_MONTH}":
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
            if date.due_date == TOMORROW.strftime('%Y-%m-%d'):
                tomorrow_todos = db.session.execute(
                    db.select(Todos).where(Todos.due_date == TOMORROW.strftime('%Y-%m-%d'))).scalars().all()
            x.append(f'{"".join(date.due_date).split("-")[0]}-{"".join(date.due_date).split("-")[1]}')



            year = "".join(date.due_date).split('-')[0]
            all_years.append(year)
# on condition that there is not any date it means there is noting to do
    if not f'{CURRENT_YEAR}-{CURRENT_MONTH}' in x:
        nothing_for_this_month = True
    # preparing title to send to log in user
    if tomorrow_todos:
        todo_title = ''
        for item in tomorrow_todos:
            if item.user_id == current_user.id:
                # todo_title is in html because email message is in html format\.
                todo_title += f"""
                                <li class="mb-2">{item.info}.</li>
                            """
        # if email is sent today it won't send again till next day
        if not EMAIL_SENT_DATE == TODAY:
            EMAIL_SENT_DATE = TODAY

            # send_email(current_user.username, current_user.email, current_user.tel, msg=todo_title)

    else:
        pass


    # if toto is done the year num stay in years list
    for date in all_dones:
        year = "".join(date.due_date).split('-')[0]
        all_years.append(year)

    return render_template('index.html', todos=all_todos, dones=all_dones,
                           user=current_user, unique_done_date=unique_done_date, unique_todo_date=unique_todo_date,
                           today=TODAY, nothing_for_this_month=nothing_for_this_month,
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
    if not todo_date :
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
                           today=TODAY, no_date=no_date, all_is_done=all_is_done, years=sorted(list(set(all_years))),
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
            if new_todo.due_date < TODAY:
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
    return render_template('add_todo.html', item=item, is_edit=True, edit_form=edit_todo, years=sorted(list(set(nav_year()))))


@app.route("/details<int:item_id>", methods=["GET", "POST"])
def details(item_id):
    item = db.get_or_404(Todos, item_id)
    detail = Todos(
        due_date=item.due_date,
        info=item.info,
        title=item.title,
    )
    return render_template('add_todo.html', item=item, is_detail=True, detail=detail, years=sorted(list(set(nav_year()))))


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







if __name__ == "__main__":
    app.run(port=5002, debug=True)
