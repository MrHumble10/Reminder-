from mailjet_rest import Client as mailjet_Client
from flask import Flask, render_template, redirect, url_for, request, flash, abort
import os
import time
import json
import requests
from twilio.rest import Client as twilio_Client

URL = "https://api.genny.lovo.ai"
def get_audio(msg):
    # send voice in email and whatsup
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": '7c8b99eb-415a-4eb6-a27a-9bf2f575f745'
        # "X-API-KEY": os.environ.get('X-API-KEY'),
    }

    # GET Speakers
    # speakers = requests.get(f"{URL}/api/v1/speakers", headers=headers).json()
    # data = speakers['data']

    tts_body = {
        "speaker": '63b40896241a82001d51c426',
        "text": msg
    }

    tts_job = requests.post(f"{URL}/api/v1/tts", headers=headers, data=json.dumps(tts_body)).json()
    print(tts_job)
    job_id = tts_job['id']

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
            print(retry_count)
        else:
            job_complete = True
            tts_url = job_res['data'][0]['urls'][0]

    return f"{tts_url}"

# sound = requests.get(url=get_audio('hello world'))
# print(sound.url)

# with open('./x.wav', mode='wb') as file:
#     file.write(sound.content)
def send_sms(msg, tel):
    account_sid = os.environ.get("account_sid")
    auth_token = os.environ.get("auth_token")
    client = twilio_Client(account_sid, auth_token)
    message = client.messages.create(
        media_url=['https://th.bing.com/th/id/OIP.cWFY-f2HWyewx55rTukOOgHaEK?w=2880&h=1620&rs=1&pid=ImgDetMain'],
        from_='whatsapp:+14155238886',
        body=f'{msg}\n',
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