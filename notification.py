from mailjet_rest import Client as mailjet_Client
from flask import Flask, render_template, redirect, url_for, request, flash, abort
import os
import requests
from twilio.rest import Client as twilio_Client


def send_sms(msg, tel):

    account_sid = os.environ.get('account_sid')
    auth_token = os.environ.get('auth_token')
    client = twilio_Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=f'{msg}',
        to=f'whatsapp:{tel}'
    )

    print(message.sid)


def send_email(user_name, user_email, tel, msg, item_id):
    # os.environ.get("MJ_APIKEY_PRIVATE")
    MJ_APIKEY_PRIVATE = os.environ.get("MJ_APIKEY_PRIVATE")
    # os.environ.get("MJ_APIKEY_PUBLIC")
    MJ_APIKEY_PUBLIC = os.environ.get("MJ_APIKEY_PUBLIC")

    mailjet = mailjet_Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_PRIVATE), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "humble.py.test@gmail.com",
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
                            f"<p>To know more details <a href='https://reminder-h4wv.onrender.com'>Click here</a>."
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