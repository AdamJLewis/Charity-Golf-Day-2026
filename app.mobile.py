import streamlit as st
import time
import qrcode
import re
import base64
import pandas as pd

from io import BytesIO
from html import escape

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

JUSTGIVING_URL = "https://www.justgiving.com/page/queens-head-charity-golf"

RAFFLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1As4qQsj5j1tWxbVGheYTRUn_ti_jOkMvDjaxhWOwJamdl26hzKdoB3rGMKMsZLZf09qP4OpMKPCD/pub?gid=985645544&single=true&output=csv"

REFRESH_SECONDS = 300

EVENT_NAME = "Queens Head Charity Golf Day"

TARGET_AMOUNT = 2000

ANDYS_LOGO = "andysmanclub.png"


st.set_page_config(
    page_title="Queens Head Charity Golf Day",
    layout="wide"
)


st.markdown("""
<style>

#MainMenu,
footer,
header {
    visibility: hidden;
}

html, body, [class*="css"] {
    background-color: #ffffff;
    color: #111111;
    font-family: 'Segoe UI', Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(225, 6, 0, 0.10), transparent 34%),
        radial-gradient(circle at top right, rgba(225, 6, 0, 0.07), transparent 30%),
        linear-gradient(180deg, #ffffff 0%, #f4f4f4 100%);
}

.block-container {
    max-width: 1240px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

.main-title {
    text-align: center;
    font-size: clamp(38px, 5vw, 74px);
    font-weight: 950;
    letter-spacing: 6px;
    line-height: 1.12;
    color: #111111;
    text-transform: uppercase;
    margin: 0 0 18px 0;
    text-shadow:
        0 3px 0 rgba(225, 6, 0, 0.18),
        0 10px 22px rgba(0,0,0,0.12);
}

.sub-title {
    text-align: center;
    font-size: clamp(14px, 1.45vw, 20px);
    letter-spacing: 5px;
    color: #e10600;
    text-transform: uppercase;
    margin: 0 0 42px 0;
    font-weight: 850;
}

img {
    max-width: 100%;
}

.dashboard-card {
    background: linear-gradient(180deg, #ffffff, #f8f8f8);
    border: 1px solid rgba(225, 6, 0, 0.34);
    border-radius: 18px;
    padding: 28px;
    min-height: 342px;
    height: 342px;
    box-shadow:
        0 18px 36px rgba(0,0,0,0.12),
        inset 0 1px 0 rgba(255,255,255,0.9);
    box-sizing: border-box;
    overflow: hidden;
}

.dashboard-card:hover {
    border-color: rgba(225, 6, 0, 0.70);
    box-shadow:
        0 22px 44px rgba(0,0,0,0.16),
        0 0 24px rgba(225, 6, 0, 0.16);
}

.section-heading {
    text-align: center;
    font-size: clamp(18px, 1.75vw, 24px);
    font-weight: 950;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    color: #111111;
    margin: 0 0 24px 0;
}

.section-heading::after {
    content: "";
    display: block;
    width: 78px;
    height: 2px;
    margin: 12px auto 0 auto;
    background: linear-gradient(90deg, transparent, #e10600, transparent);
}

.big-total {
    text-align: center;
    font-size: clamp(60px, 6vw, 88px);
    font-weight: 950;
    line-height: 1;
    color: #e10600;
    margin: 34px 0 30px 0;
    text-shadow:
        0 4px 0 rgba(0,0,0,0.08),
        0 0 22px rgba(225, 6, 0, 0.18);
}

.progress-helper {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    color: #333333;
    font-size: 13px;
    font-weight: 850;
}

.progress-container {
    width: 100%;
    height: 26px;
    background: #e9e9e9;
    border-radius: 999px;
    overflow: hidden;
    border: 1px solid rgba(0,0,0,0.08);
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.12);
}

.progress-bar {
    height: 100%;
    min-width: 8px;
    background: linear-gradient(90deg, #8b0000, #e10600, #ff3434);
    border-radius: 999px;
    box-shadow: 0 0 14px rgba(225, 6, 0, 0.32);
    color: transparent;
    text-align: center;
    font-size: 13px;
    font-weight: 950;
    line-height: 26px;
}

.donation-box {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.08);
    border-left: 5px solid #e10600;
    border-radius: 13px;
    padding: 12px 14px;
    margin-bottom: 11px;
    color: #111111;
    font-size: 15px;
    font-weight: 700;
    box-shadow: 0 8px 18px rgba(0,0,0,0.08);
}

.donor-name {
    font-size: 15px;
    font-weight: 900;
    color: #111111;
}

.donation-amount {
    float: right;
    color: #e10600;
    font-size: 16px;
    font-weight: 950;
}

.donation-message {
    clear: both;
    color: #555555;
    font-size: 13px;
    margin-top: 6px;
    font-style: italic;
    line-height: 1.35;
}

.empty-donations {
    text-align: center;
    color: #555555;
    font-size: 15px;
    font-weight: 700;
    padding-top: 92px;
}

.qr-card {
    text-align: center;
}

.qr-title {
    color: #111111;
    text-align: center;
    font-size: clamp(14px, 1.2vw, 20px);
    font-weight: 950;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0 0 16px 0;
    line-height: 1.4;
}

.qr-image {
    text-align: center;
}

.qr-image img {
    width: 158px;
    background: #ffffff;
    padding: 12px;
    border-radius: 12px;
    border: 4px solid #e10600;
    box-shadow:
        0 14px 30px rgba(0,0,0,0.18),
        0 0 20px rgba(225, 6, 0, 0.18);
}

.qr-text {
    text-align: center;
    margin-top: 18px;
    font-size: 18px;
    font-weight: 950;
    color: #111111;
    letter-spacing: 0.5px;
}

.raffle-card {
    margin-top: 36px;
    padding: 20px 26px;
    height: auto;
    min-height: 125px;
    overflow: visible;
}

.raffle-title {
    text-align: center;
    font-size: clamp(18px, 1.8vw, 26px);
    font-weight: 950;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #111111;
    margin: 0 0 8px 0;
}

.raffle-title::after {
    content: "";
    display: block;
    width: 78px;
    height: 2px;
    margin: 10px auto 0 auto;
    background: linear-gradient(90deg, transparent, #e10600, transparent);
}

.raffle-helper {
    text-align: center;
    color: #555555;
    font-size: 14px;
    font-weight: 700;
    margin-top: 14px;
}

.stTextInput > label {
    color: #111111;
    font-weight: 900;
    font-size: 16px;
}

.stTextInput > div > div > input {
    background-color: #ffffff;
    color: #111111;
    border: 1px solid rgba(225, 6, 0, 0.45);
    border-radius: 12px;
    padding: 12px;
    font-size: 18px;
    font-weight: 700;
}

.raffle-results-card {
    background: #ffffff;
    border: 1px solid rgba(225, 6, 0, 0.22);
    border-radius: 18px;
    padding: 18px;
    margin-top: 18px;
    height: 420px;
    min-height: 420px;
    box-shadow:
        0 12px 24px rgba(0,0,0,0.08),
        inset 0 1px 0 rgba(255,255,255,0.9);
    box-sizing: border-box;
    overflow: hidden;
}

.probability-card {
    height: 420px;
    min-height: 420px;
    text-align: center;
}

.raffle-section-title {
    text-align: center;
    font-size: 18px;
    font-weight: 950;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #111111;
    margin-bottom: 16px;
}

.raffle-section-title::after {
    content: "";
    display: block;
    width: 60px;
    height: 2px;
    margin: 8px auto 0 auto;
    background: linear-gradient(90deg, transparent, #e10600, transparent);
}

.raffle-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
}

.raffle-table-wrapper {
    height: 335px;
    overflow-y: auto;
    padding-right: 6px;
}

.raffle-table-wrapper::-webkit-scrollbar {
    width: 8px;
}

.raffle-table-wrapper::-webkit-scrollbar-track {
    background: #f2f2f2;
    border-radius: 999px;
}

.raffle-table-wrapper::-webkit-scrollbar-thumb {
    background: #e10600;
    border-radius: 999px;
}

.raffle-table th {
    text-align: left;
    color: #111111;
    font-size: 13px;
    font-weight: 950;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 12px;
    border-bottom: 1px solid rgba(0,0,0,0.12);
}

.raffle-table td {
    background: #ffffff;
    color: #111111;
    padding: 13px 12px;
    font-size: 15px;
    font-weight: 750;
    border-bottom: 1px solid rgba(0,0,0,0.08);
}

.raffle-table td:first-child {
    border-left: 5px solid #e10600;
    color: #e10600;
    font-weight: 950;
    width: 170px;
}

.raffle-empty {
    text-align: center;
    color: #555555;
    font-size: 15px;
    font-weight: 800;
    padding: 35px 10px;
}

.css-pie-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 18px 0 18px 0;
}

.css-pie {
    width: 185px;
    height: 185px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.css-pie-hole {
    width: 112px;
    height: 112px;
    border-radius: 50%;
    background: #ffffff;
}

.probability-number {
    font-size: 42px;
    font-weight: 950;
    color: #e10600;
    line-height: 1;
    margin-top: 0;
}

.probability-label {
    color: #555555;
    font-size: 14px;
    font-weight: 750;
    margin-top: 8px;
}

.ticket-count {
    margin-top: 14px;
    color: #111111;
    font-size: 15px;
    font-weight: 900;
}

.footer-banner {
    margin-top: 36px;
    padding: 20px;
    border: 1px solid rgba(225, 6, 0, 0.38);
    border-radius: 14px;
    text-align: center;
    color: #111111;
    background: #ffffff;
    font-size: clamp(15px, 1.5vw, 19px);
    font-weight: 950;
    letter-spacing: 1px;
    box-shadow:
        0 16px 30px rgba(0,0,0,0.10),
        inset 0 1px 0 rgba(255,255,255,0.9);
}

</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def get_fundraising_data():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = "/usr/bin/chromium"

    driver = None

    try:
        driver = webdriver.Chrome(
            service=Service("/usr/bin/chromedriver"),
            options=options
        )

        driver.get(JUSTGIVING_URL)

        time.sleep(6)

        body_text = driver.find_element(By.TAG_NAME, "body").text

    except Exception as error:
        st.warning(f"Could not load JustGiving data at the moment: {error}")
        return "£0", []

    finally:
        if driver is not None:
            driver.quit()

    return "£0", []


def generate_qr_base64(url):

    qr = qrcode.make(url)

    buffer = BytesIO()

    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return qr_base64


total_raised, donations = get_fundraising_data()

logo_col1, logo_col2 = st.columns([3.5, 1])

with logo_col1:

    st.markdown(
        f'<div class="main-title">{EVENT_NAME}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Supporting ANDYSMANCLUB</div>',
        unsafe_allow_html=True
    )

with logo_col2:
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    st.image(ANDYS_LOGO, width=500)


left_col, middle_col, right_col = st.columns([1, 1, 1])

qr_base64 = generate_qr_base64(JUSTGIVING_URL)


with right_col:

    right_card_html = f"""
<div class="dashboard-card qr-card">
    <div class="qr-title">Click or Scan the QR Code to Donate</div>
    <div class="qr-image">
        <a href="{JUSTGIVING_URL}" target="_blank">
            <img src="data:image/png;base64,{qr_base64}" style="width:190px;">
        </a>
    </div>
    <div class="qr-text">Every £1 = 1 Raffle Ticket</div>
</div>
"""

    st.markdown(right_card_html, unsafe_allow_html=True)


st.markdown(
    """
    <div class="footer-banner">
        Supporting Men's Mental Health • Talk. Support. Change Lives.
    </div>
    """,
    unsafe_allow_html=True
)


time.sleep(REFRESH_SECONDS)

st.rerun()
