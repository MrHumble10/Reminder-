#
# from test import app, db, Todos, User, TOMORROW
# from collections import Counter
#
# with app.app_context():
#     result = db.session.execute(db.select(Todos))
#     all_todos = result.scalars().all()
#     tomorrow_todos = []
#     for date in all_todos:
#         if date.due_date == TOMORROW.strftime('%Y-%m-%d'):
#             tomorrow_todos = db.session.execute(
#                 db.select(Todos).where(Todos.due_date == TOMORROW.strftime('%Y-%m-%d'))).scalars().all()
#     print(tomorrow_todos)
#
#     #  preparing title to send to log in user
#     if tomorrow_todos:
#         todo_title = ''
#         users = []
#         for item in tomorrow_todos:
#             user = db.get_or_404(User, item.user_id)
#
#             # todo_title is in html because email message is in html format\.
#             todo_title = f"""
#                                             <li class="mb-2">{item.info}.</li>
#                                         """
#             print(f"{user.id}-{todo_title}")
#             send_email(user.username, user.email, user.tel, msg=todo_title)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#     # for todo in tomorrow_todos:
#     #     # Retrieve items from your "todo" table (replace with your actual data retrieval logic)
#     #     user_email = db.get_or_404(User, todo.user_id).email
#     #     user_items = [
#     #         {"task": f"{todo.info}", "description": f"{todo.title}"},
#     #
#     #         # Add more items as needed
#     #     ]
#     #
#     #     # Group items by user email (you can use a dictionary or any other data structure)
#     #     grouped_items = "\n".join(f"- {item['task']}: {item['description']}" for item in user_items)
#     #
#     #     print(grouped_items)
#     db.create_all()
#
