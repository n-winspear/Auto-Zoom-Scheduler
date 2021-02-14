import requests
import json
import os
import datetime
import random
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()


# API Credentials
user_id = 'n.winspear@leadership.ac.nz'
base_uri = 'https://api.zoom.us/v2/users/{}/meetings'.format(user_id)
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
api_token = os.getenv('API_TOKEN')

# Headers
headers = {
    'authorization': 'Bearer {}'.format(api_token),
    'content-type': 'application/json'
}

# Log Content
log_content = {
    "zoomResponse": "",
    "emailResponses": []
}

# Recipient Data

green = "#72BE44"
blue = "#2D62AD"
yellow = "#F1A11F"
red = "#E12729"

recipients = [
    {
        "name": "Nathan",
        "emailAddress": "n.winspear@leadership.ac.nz",
        "colour": green
    },
    {
        "name": "Swetha",
        "emailAddress": "s.thomas@leadership.ac.nz",
        "colour": yellow
    },
    {
        "name": "Geoff",
        "emailAddress": "g.lorigan@leadership.ac.nz",
        "colour": red
    },
    {
        "name": "Sythey",
        "emailAddress": "s.russell@leadership.ac.nz",
        "colour": yellow
    },
    {
        "name": "Demian",
        "emailAddress": "d.rosenthal@leadership.ac.nz",
        "colour": yellow
    },
    {
        "name": "Laksitha",
        "emailAddress": "l.siriwardena@leadership.ac.nz",
        "colour": yellow
    },
    {
        "name": "Kasun",
        "emailAddress": "k.wickramanayake@leadership.ac.nz",
        "colour": yellow
    },
    {
        "name": "Eswari",
        "emailAddress": "p.thirumeni@leadership.ac.nz",
        "colour": yellow
    },
    {
        "name": "John",
        "emailAddress": "j.wadsworth@leadership.ac.nz",
        "colour": yellow
    },
    {
        "name": "Divya",
        "emailAddress": "d.somashekarappa@leadership.ac.nz",
        "colour": yellow
    },
]


def generate_password():
    password_length = 8
    possible_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMONPQRSTUVWXYZ1234567890'
    random_character_list = [random.choice(
        possible_characters) for i in range(password_length)]
    random_password = ''.join(random_character_list)
    return random_password


def get_start_time(time):
    if time == 'morning':
        return '{}T{}'.format(datetime.date.today(), datetime.time(9, 0, 0))
    else:
        return '{}T{}'.format(datetime.date.today(), datetime.time(17, 0, 0))


def build_request_body(time):
    return json.dumps({
        "topic": "Morning Check In" if time == 'morning' else 'Evening Check Out',
        "type": 2,
        "start_time": get_start_time(time),
        "duration": 60,
        "password": generate_password(),
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": True,
            "mute_upon_entry": True,
            "approval_type": 2,
            "audio": "voip",
            "alternative_hosts": 's.russell@leadership.ac.nz',
            "waiting_room": False,
            "meeting_authentication": False,
        }
    })


def build_message_parts(recipient_data, meeting_details, time):

    text = """\
    Good {time_of_day} {recipient_name}!
    Join {meeting_type}
    Link: {link}
    Password: {password}

    This message was sent by Nathan's automated check in / check out system
    """.format(time_of_day=time,
               recipient_name=recipient_data["name"],
               meeting_type=('Morning Check In' if time ==
                             'morning' else 'Evening Check Out'),
               link=(meeting_details[0] if recipient_data['name']
                     == 'Nathan' else meeting_details[1]),
               password=meeting_details[2]
               )

    html = """\
    <html style="width: 100%; height: 100%; box-sizing: border-box;">
        <head>
            <link
            href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap"
            rel="stylesheet"
            />
        </head>
        <body
            style="
            width: 100%;
            height: 100%;
            font-family: 'Roboto', sans-serif;
            "
        >
            <div>
            <h1 style="color: #444444;">
                Good {time_of_day} <span style="color: {recipient_colour};">{recipient_name}!</span>
            </h1>
            </div><br>
            <a href="{link}">
                <div>
                    <!--[if mso]>
                    <v:roundrect xmlns_v="urn:schemas-microsoft-com:vml" xmlns_w="urn:schemas-microsoft-com:office:word" href="{link}" style="height:36px;v-text-anchor:middle;width:150px; color="#ffffff;" arcsize="5%" strokecolor="#3B99FC" fillcolor="#3B99FC">
                        <w:anchorlock/>
                        <center style="color:#ffffff;font-family:Helvetica, Arial,sans-serif;font-size:16px;">Join {meeting_type} &rarr;</center>
                    </v:roundrect>
                    <![endif]-->
                    <a href="{link}" style="background-color:#3B99FC;border:1px solid #3B99FC;border-radius:3px;color:#ffffff;display:inline-block;font-family:sans-serif;font-size:16px;line-height:44px;text-align:center;text-decoration:none;width:150px;-webkit-text-size-adjust:none;mso-hide:all;">Join {meeting_type} &rarr;</a>
                </div>
            </a><br>
            <div>
                <h4
                    style="
                    font-weight: 500;
                    color: #444444;
                    "
                >
                    Password:
                </h4>
                <h1
                    style="
                    font-weight: 700;
                    color: #444444;
                    "
                >
                    {password}
                </h1>
            </div>
            <div>
                <h5
                    style="
                    font-weight: 300;
                    color: #444444;
                    "
                >
                    This message was sent by Nathan's automated check in / check out system
                </h5>
            </div>
        </body>
    </html>
    """.format(time_of_day=time,
               recipient_colour=recipient_data['colour'],
               recipient_name=recipient_data["name"],
               meeting_type=('Check In' if time ==
                             'morning' else 'Check Out'),
               link=(meeting_details[0] if recipient_data['name']
                     == 'Nathan' else meeting_details[1]),
               password=meeting_details[2]
               )
    message_plaintext = MIMEText(text, 'plain')
    message_html = MIMEText(html, 'html')

    return [message_plaintext, message_html]


def create_meeting(time):
    request_body = build_request_body(time)
    response = requests.post(base_uri, request_body, headers=headers)
    data = response.json()
    log_content["zoomResponse"] = response.json()
    return [data['start_url'], data['join_url'], data['password']]


def send_meeting_email(recipient_data, meeting_details, time):
    sender_email = 'n.winspear@leadership.ac.nz'

    message = MIMEMultipart('alternative')
    message['Subject'] = "Morning Check In" if time == 'morning' else 'Evening Check Out'
    message['From'] = sender_email
    message['To'] = recipient_data['emailAddress']

    message_parts = build_message_parts(recipient_data, meeting_details, time)

    message.attach(message_parts[0])
    message.attach(message_parts[1])

    text = message.as_string()

    # Sending Email
    host = 'smtp.office365.com'
    port = 587
    password = os.getenv('MAIL_PASSWORD')

    # context = ssl.create_default_context() context=context
    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls()
        server.login(sender_email, password)
        try:
            server.sendmail(sender_email, recipient_data['emailAddress'], text)
            return json.dumps({"status": "success", "message": "Email sent successfully", "recipient": recipient_data['name']})
        except Exception as e:
            return json.dumps({"status": "failed", "message": str(e), "recipient": recipient_data['name']})


def log_event():
    log_folder_path = "/home/pi/Documents/Auto-Zoom-Scheduler/logs"
    filename = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")

    f = open("{}/{}.txt".format(log_folder_path, filename), "w")
    f.write("Emails sent at: {}\n\n{}".format(
        datetime.datetime.now(), json.dumps(log_content)))
    f.close()


def main():
    meeting_time = 'morning' if datetime.datetime.now().hour in (8, 9) else 'evening'
    meeting_details = create_meeting(meeting_time)
    for recipient in recipients:
        response = send_meeting_email(recipient, meeting_details, meeting_time)
        log_content["emailResponses"].append(response)
    log_event()
    #print(json.dumps(log_content))


main()
