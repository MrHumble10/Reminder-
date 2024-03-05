from mailjet_rest import Client
import os
# def reply_mail(name, email):
#     MJ_APIKEY_PRIVATE = '3989ddb697e3f2feb9950571f17b79dd'
#         # os.environ.get("MJ_APIKEY_PRIVATE")
#     MJ_APIKEY_PUBLIC = '51045e3e145ebe22953a762762d80622'
#         # os.environ.get("MJ_APIKEY_PUBLIC")
#
#
#     # os.environ.get("MJ_APIKEY_PRIVATE")
#     mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_PRIVATE), version='v3.1')
#     data = {
#         'Messages': [
#             {
#                 "From": {
#                     "Email": "humble.py.test@gmail.com",
#                     "Name": "Me"
#                 },
#                 "To": [
#                     {
#                         "Email": f"{email}",
#                         "Name": "You"
#                     }
#                 ],
#                 "Subject": "REPLY FROM POST LAND!",
#                 "TextPart": f"Dear {name}\n\nWe have received your message and our response would be sent to you soon."
#                             f"Thank you\n\nPOSTLAND TEAM",
#                 "HTMLPart": ""
#             }
#         ]
#     }
#     result = mailjet.send.create(data=data)
#     print(result.status_code)
#     print(result.json())
#


def send_email(user_name, user_email, tel, msg, item_id):
    # os.environ.get("MJ_APIKEY_PRIVATE")
    MJ_APIKEY_PRIVATE = os.environ.get("MJ_APIKEY_PRIVATE")
    # os.environ.get("MJ_APIKEY_PUBLIC")
    MJ_APIKEY_PUBLIC = os.environ.get("MJ_APIKEY_PUBLIC")


    mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_PRIVATE), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "humble.py2017@gmail.com",
                    "Name": "Me"
                },
                "To": [
                    {
                        "Email": user_email,
                        "Name": "You"
                    }
                ],
                "Subject": "YOUR PLANS FOR TOMORROW!",
                "TextPart": '',
                "HTMLPart": f"<h1>Hi Dear {user_name}!</h1><br>"
                            f"<p>You have already sat plan(s) for tomorrow.</p>"
                            f"<p>This Email has been sent to you "
                            f"in order to remember what you are going to do by Tomorrow.</p>"
                            f"<p>To know more details <a href='reminder-h4wv.onrender.com/details{item_id}'>Click here</a>."
                            f"""<div class="container py-5">
                            <!-- For demo purpose -->
                            <header class="text-center text-white">
                                <h1 class="display-4">Your TODO List</h1>
                                
                            </header>
                        
                            <div class="row py-5">
                                <div class="col-lg-7 mx-auto">
                                    <div class="card shadow mb-4">
                                        <div class="card-body p-5">
                                            <h4 class="mb-4">What you are going to do by Tomorrow ▼</h4>
                                            <!-- List with bullets -->
                                            <ol>
                                                {msg}
                                            </ol>
                                            
                                            
                                        </div>
                                    </div>
                        
                                </div>
                            </div>
                        </div>"""
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
    # reply_mail(name=user_name, email=user_email)