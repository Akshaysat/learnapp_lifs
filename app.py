import email
import json
from select import select
import time
from unicodedata import name
import streamlit as st
import requests
import pandas as pd
import datetime as dt

# set page config
st.set_page_config(page_title="LearnApp", page_icon="favicon.png")

# hide streamlit branding and hamburger menu
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# set today's date and time
curr_time_dec = time.localtime(time.time())
curr_date = time.strftime("%Y-%m-%d", curr_time_dec)

# get learnapp's content data
f = open("content.json")
content_data = json.load(f)
f.close()

# functions for getting user specific course progress
url = "https://e3d72bp6aa.execute-api.ap-south-1.amazonaws.com/"
payload = {}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload)
access_token = response.text

token = "Bearer " + access_token


def fetch_userid(email):
    email = email.replace("@", "%40")
    url = "https://hydra.prod.learnapp.com/kraken/users/search?q=" + email

    payload = {}
    headers = {
        "authorization": token,
        "x-api-key": "u36jbrsUjD8v5hx2zHdZNwqGA6Kz7gsm",
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    try:
        data = json.loads(response.text)["users"][0]
        try:
            return data["userId"]
        except:
            return -1
    except:
        return -1


def course_progress(email_id, course_id):
    try:
        user_id = fetch_userid(email_id)
        url = f"https://census.prod.learnapp.com/kraken/users/{user_id}/courses/{course_id}"
        payload = {}
        headers = {
            "authorization": token,
            "x-api-key": "Ch2rqJp3rxH8ZVccQT8ywV7zMR3Ac8fQ",
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        data = json.loads(response.text)
        progress = data["courseDetailData"]["percentage"]
    except:
        progress = 0

    return progress


# function for creating the genericcourse cards
def course_container(day_no, date, course_key):
    #
    date_format = date.strftime("%d %b'%y")
    st.subheader(f"📘 {day_no}: {content_data[course_key]['title']}")
    st.write(f"📅 {date_format}")
    st.write("✍️ Watch this recorded course before the next live class")
    st.write("")

    canonical_title = content_data[course_key]["canonicalTitle"]
    course_id = content_data[course_key]["id"]
    progress = course_progress(email_id, course_id)
    if progress >= 85:
        progress_str = f"✅ {progress}"
    else:
        progress_str = f"📖 {progress}"
    course_url = (
        f"https://learnapp.com/courses/{canonical_title}/topics/trailer?locale=en-us"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.image(content_data[course_key]["assetUrl"], width=300)

    with col2:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown(
            f"[![Play Now](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-17-nov-22-options-course-email/7b488dc8-950e-4295-81f2-2129c2ab91f0.png)]({course_url})"
        )
        # st.markdown(
        #     f"[![Play Now](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-15-nov-22-la-announcement-akriti-singh/5e7bcdd4-039a-4a0f-a255-7c48d3993eaa.png)]({course_url})"
        # )
        st.caption(f"{progress_str}% completed")

    st.write("----")
    st.write("")


# function for creating the genericcourse cards
def workshop_container(day_no, date, workshop_name, workshop_jpeg, agenda, zoom_link):
    #
    date_format = date.strftime("%d %b'%y")
    time_format = date.strftime("%H:%M %p")

    cutoff_datetime = date + dt.timedelta(hours=1)
    st.subheader(f"📕 {day_no}: {workshop_name}")
    st.write(f"📅 {date_format}")
    st.write(f"🚨 {agenda} ")
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.image(workshop_jpeg, width=300)

    with col2:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        if dt.datetime.now() + dt.timedelta(hours=5, minutes=30) > cutoff_datetime:
            st.write("🤷 This live class is now over!")
        else:
            st.markdown(
                f"[![Register](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-17-nov-22-options-course-email/2f26a465-4fd4-4a0c-b121-5459d714f573.png)]({zoom_link})"
            )
            st.caption(f"📅 {date_format}")
            st.caption(f"🕒 {time_format}")

    st.write("----")
    st.write("")


def schedule_container():
    # day-wise schedule
    workshop_container(
        "Day 00",
        dt.datetime(2022, 12, 13, 9, 0, 0),
        "Kickoff Session",
        "workshop/kick-off-session.jpeg",
        "Meet your mentors and peers, 10 day schedule and program outcomes",
        "https://us06web.zoom.us/j/87994652970",
    )

    course_key = "basics-of-personal-finance"
    course_container("Day 01", dt.datetime(2022, 12, 14, 9, 0, 0), course_key)

    workshop_container(
        "Day 02",
        dt.datetime(2022, 12, 15, 9, 0, 0),
        "Create your own Personal Budget",
        "workshop/basics-of-personal-finance.jpeg",
        "Budget creation, emergency fund and goal planning",
        "https://us06web.zoom.us/j/83932114049",
    )

    course_key = "basics-of-trading"
    course_container("Day 03", dt.datetime(2022, 12, 16, 9, 0, 0), course_key)

    workshop_container(
        "Day 04",
        dt.datetime(2022, 12, 17, 9, 0, 0),
        "How to use trading terminal?",
        "workshop/basics-of-trading.jpeg",
        "Place different order types, place stoploss and target",
        "https://us06web.zoom.us/j/85648552919",
    )

    course_key = "asset-allocation-strategy"
    course_container("Day 05", dt.datetime(2022, 12, 18, 9, 0, 0), course_key)

    workshop_container(
        "Day 06",
        dt.datetime(2022, 12, 20, 9, 0, 0),
        "Build your Personal Asset Allocation Strategy",
        "workshop/asset-allocation-strategy.jpeg",
        "Learn to calculate: CAGR, XIRR and Sharpe Ratio",
        "https://us06web.zoom.us/j/84529479220",
    )

    course_key = "long-india-portfolio-"
    course_container("Day 07", dt.datetime(2022, 12, 21, 9, 0, 0), course_key)

    workshop_container(
        "Day 08",
        dt.datetime(2022, 12, 22, 9, 0, 0),
        "Build your Long India Portfolio",
        "workshop/long-india-portfolio-.jpeg",
        "Futuristic themes in India, Stock selection using screener, Entry & Exit criteria",
        "https://us06web.zoom.us/j/85011547765",
    )

    #
    st.subheader(f"📕 Day 09: Live Examination")
    st.write(f"📅 23 Dec'22")
    st.write(f"🕒 09:00 AM - 12:00 PM")
    st.write("🚨 60 minutes, 30 questions and proof of work subsmission")
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        st.image("workshop/exam_day.jpeg", width=300)

    with col2:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        # st.markdown(
        #     f"[![Register](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-17-nov-22-options-course-email/2f26a465-4fd4-4a0c-b121-5459d714f573.png)](https://us06web.zoom.us/meeting/register/tZYkdu2rpzgiHdcxaGToQ-zP9aYd6UHOmCeC)"
        # )
        st.write(f"🕒 The examination link will be made live at 09:00 AM")

    st.write("----")
    st.write("")

    st.subheader(f"📕 Day 10: Graduation Day")
    st.write(f"📅 24 Dec'22")
    st.write(f"🕒 09:00 AM")
    st.write(
        "🚨 Celebrate your success, share your experience and progression path to become a good investor"
    )
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        st.image("workshop/grad-day.jpeg", width=300)

    with col2:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        st.markdown(
            f"[![Register](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-17-nov-22-options-course-email/2f26a465-4fd4-4a0c-b121-5459d714f573.png)](https://us06web.zoom.us/j/88364876297)"
        )
        st.caption(f"🕒 09:00 to 10:00 AM")

    st.write("----")
    st.write("")


# Frontend
col1, col2, col3 = st.columns(3)
with col1:
    st.write("")
with col2:
    st.image("logo.png", width=225)
    st.write("")
with col3:
    st.write("")

st.write("----")

st.markdown(
    "<h2 style='text-align: center; color: white;'>Learn Investing From Scratch</h2>",
    unsafe_allow_html=True,
)


try:
    email_id = st.experimental_get_query_params()["email"][0]
    schedule_container()
except:
    st.write("-----")
    email_id = (
        st.text_input(
            "Enter your LearnApp Registered Email Address to get cohort schedule & your progress"
        )
        .strip()
        .lower()
    )
    if st.button("Get Schedule"):
        st.write("-----")
        schedule_container()
