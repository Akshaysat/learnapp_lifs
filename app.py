import email
import json
from select import select
import time
from unicodedata import name
import streamlit as st
import requests
import pandas as pd
import datetime as dt
from google.oauth2 import service_account
from gsheetsdb import connect

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

# Function to get userid from email
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


# function to get course progress
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
        st.caption(f"📅 {date_format}")

    with col2:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown(
            f"[![Play Now](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-05-jan-23-la-announcement-shivam-vashisth/233692d4-8dac-4d1c-bccd-aa65561e7a11.png)]({course_url})"
        )
        st.caption(f"{progress_str}% completed")

    st.write("----")
    st.write("")


# function for creating the genericcourse cards
def workshop_container(day_no, date, workshop_name, workshop_jpeg, agenda, zoom_link):
    #
    request_link = "https://api.whatsapp.com/send/?phone=9810620950"
    date_format = date.strftime("%d %b'%y")
    time_format = date.strftime("%H:%M %p")
    recording_link = df_recording[df_recording["Day_No"] == day_no][
        "Recording_Url"
    ].iloc[0]
    date_format = date.strftime("%d %b'%y")
    time_format = date.strftime("%H:%M %p")

    cutoff_datetime = date + dt.timedelta(hours=1)
    st.subheader(f"🛠️ {day_no}: {workshop_name}")
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.image(workshop_jpeg, width=300)
        st.caption(f"📅 {date_format} | 🕒 {time_format}")

    with col2:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        if dt.datetime.now() + dt.timedelta(hours=5, minutes=30) > cutoff_datetime:

            col_name = day_no.replace(" ", "_") + "_Live"
            try:
                recording_score = df[df["Email"] == email_id][col_name].iloc[0]
            except:
                recording_score = 0

            if recording_score > 5:

                if recording_link == None:
                    st.write("⌛ Uploading...")
                    st.caption("Check back in some time")
                else:
                    st.markdown(
                        f"[![Watch Recording](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-05-jan-23-la-announcement-shivam-vashisth/600f5e01-fc1b-4edb-b3fb-411f35a8c092.png)]({recording_link})"
                    )

            else:
                st.markdown(
                    f"[![Request Recording](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-05-jan-23-la-announcement-shivam-vashisth/2e866960-fa4c-4ee5-abcd-02ee18c88dd2.png)]({request_link})"
                )
                st.write("🤷 Uh Oh! Looks like you did not attend this class!")

        else:
            st.markdown(
                f"[![Register](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-05-jan-23-la-announcement-shivam-vashisth/3c432ff4-a7ac-4790-a978-2546286f4945.png)]({zoom_link})"
            )

    st.write("----")
    st.write("")


def schedule_container():
    # day-wise schedule

    workshop_container(
        "Day 00",
        dt.datetime(2023, 1, 9, 9, 0, 0),
        "Kickoff Session",
        "workshop/kick-off-session.jpeg",
        "Meet your mentors and peers, 10 day schedule and program outcomes",
        "https://us06web.zoom.us/j/82289267409",
    )

    course_key = "basics-of-personal-finance"
    course_container("Day 01", dt.datetime(2023, 1, 10, 9, 0, 0), course_key)

    workshop_container(
        "Day 02",
        dt.datetime(2023, 1, 11, 9, 0, 0),
        "Create your own Personal Budget",
        "workshop/basics-of-personal-finance.jpeg",
        "Budget creation, emergency fund and goal planning",
        "https://us06web.zoom.us/j/88540364413",
    )

    course_key = "asset-allocation-strategy"
    course_container("Day 03", dt.datetime(2023, 1, 12, 9, 0, 0), course_key)

    workshop_container(
        "Day 04",
        dt.datetime(2023, 1, 13, 9, 0, 0),
        "Build your Personal Asset Allocation Strategy",
        "workshop/asset-allocation-strategy.jpeg",
        "Learn to calculate: CAGR, XIRR and Sharpe Ratio",
        "https://us06web.zoom.us/j/86026920286",
    )

    workshop_container(
        "Day 05",
        dt.datetime(2023, 1, 16, 9, 0, 0),
        "Learn softwares for Stock Analysis",
        "workshop/tool-box-101.jpeg",
        "Learn to use softwares used for analysis",
        "https://us06web.zoom.us/j/85081482839",
    )

    course_key = "long-india-portfolio-"
    course_container("Day 06", dt.datetime(2023, 1, 17, 9, 0, 0), course_key)

    workshop_container(
        "Day 07",
        dt.datetime(2023, 1, 18, 9, 0, 0),
        "Build your Long India Portfolio",
        "workshop/long-india-portfolio-.jpeg",
        "Futuristic themes in India, Stock selection using screener, Entry & Exit criteria",
        "https://us06web.zoom.us/j/88411595833",
    )

    course_key = "long-term-momentum-strategy"
    course_container("Day 08", dt.datetime(2023, 1, 19, 9, 0, 0), course_key)

    workshop_container(
        "Day 09",
        dt.datetime(2023, 1, 20, 9, 0, 0),
        "Build your systematic investment portfolio",
        "workshop/systematic-investment-portoflio.jpeg",
        "Selection criteria, entry & exit rules",
        "https://us06web.zoom.us/j/87298469196",
    )

    st.subheader(f"📘 Day 10: Graduation Day")
    st.write(
        "🚨 Celebrate your success, share your experience and progression path to become a good investor"
    )
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        st.image("workshop/grad-day.jpeg", width=300)
        st.caption(f"📅 21 Jan'23 | 🕒 09:00 AM")

    with col2:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        st.markdown(
            f"[![Register](https://s3.ap-south-1.amazonaws.com/messenger.prod.learnapp.com/emails/newsLetters-05-jan-23-la-announcement-shivam-vashisth/3c432ff4-a7ac-4790-a978-2546286f4945.png)](https://us06web.zoom.us/j/85725705831)"
        )

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

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
# @st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows


sheet_url = st.secrets[f"private_gsheets_url_lifs-02"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')
df = pd.DataFrame(rows)
df.set_index("User_ID", inplace=True)
df = df.sort_values("Score", ascending=False)

recording_sheet_url = "https://docs.google.com/spreadsheets/d/1NkBcJv1PH1Bumjpf7tD1cK4Zt-QopU4nsFen3UI11qU/edit#gid=1961064199"
rows = run_query(f'SELECT * FROM "{recording_sheet_url}"')
df_recording = pd.DataFrame(rows)

# frontend code
try:
    email_id = st.experimental_get_query_params()["email"][0]
    schedule_container()
except:
    st.write("-----")
    email_id = (
        st.text_input(
            "Enter your LearnApp Registered Email Address to see your progress"
        )
        .strip()
        .lower()
    )

    if st.button("Show my progress"):
        st.write("-----")
        st.subheader("Your Stats")
        try:
            user_score = df[df["Email"] == email_id]["Score"].iloc[0]

        except:
            user_score = 0

        leaderboard_cutoff = df["Score"].iloc[20]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Your Score", user_score)
        with col2:
            st.metric("Leaderboard Cutoff", leaderboard_cutoff)

        st.write("")
        if user_score >= leaderboard_cutoff:
            st.success("You're doing great. Keep up the consistency!")

        else:
            st.info("Please complete the pending courses to join leaderboard toppers")

        st.write("-----")
        st.subheader("Your Schedule")
        schedule_container()
