from notification import send_email
from test import app, db, Todos, User, TOMORROW
from collections import Counter

with app.app_context():

    db.create_all()
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
        users = []
        for item in tomorrow_todos:
            user = db.get_or_404(User, item.user_id)

            # todo_title is in html because email message is in html format\.
            todo_title = f"""
                                                    <li class="mb-2">{item.info}.</li>
                                                """
            print(f"{user.id}-{todo_title}")
            send_email(user.username, user.email, user.tel, msg=todo_title)
if __name__ == "__main__":
    app.run(port=5002, debug=True)