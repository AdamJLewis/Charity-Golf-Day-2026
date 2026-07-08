import streamlit as st
import qrcode
import re
import base64
import pandas as pd

from io import BytesIO
from html import escape

import requests
from bs4 import BeautifulSoup

JUSTGIVING_URL = "https://www.justgiving.com/page/queens-head-charity-golf"

RAFFLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1As4qQsj5j1tWxbVGheYTRUn_ti_jOkMvDjaxhWOwJamdl26hzKdoB3rGMKMsZLZf09qP4OpMKPCD/pub?gid=985645544&single=true&output=csv"


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

[data-testid="column"] {
    padding: 0 0.5rem;
}

.element-container {
    margin-bottom: 0.75rem;
}

@media screen and (max-width: 900px) {

    .dashboard-card {
        min-height: auto;
        height: auto;
        margin-bottom: 20px;
        padding: 24px;
    }

    .main-title {
        letter-spacing: 3.5px;
    }

    .sub-title {
        letter-spacing: 3.5px;
    }

    .big-total {
        font-size: 58px;
    }

    .qr-image img {
        width: 170px;
    }

    .raffle-results-card {
        min-height: auto;
    }

    .probability-card {
        min-height: auto;
    }
}

</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def get_fundraising_data():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept-Language": "en-GB,en;q=0.9",
    }

    try:
        response = requests.get(
            JUSTGIVING_URL,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for item in soup(["script", "style", "noscript"]):
            item.decompose()

        body_text = soup.get_text("\n", strip=True)

    except Exception as error:
        st.warning(f"Could not load JustGiving data at the moment: {error}")
        return "£0", []

    lines = [
        line.strip()
        for line in body_text.split("\n")
        if line.strip()
    ]

    money_pattern = r"£\s?\d[\d,]*(?:\.\d{2})?"

    total_raised = "£0"

    for i, line in enumerate(lines):

        line_lower = line.lower()

        if line_lower == "donation summary":

            nearby_lines = lines[i:i + 20]

            for j, nearby_line in enumerate(nearby_lines):

                if nearby_line.lower() == "total":

                    for candidate in nearby_lines[j + 1:j + 5]:

                        amount_match = re.search(money_pattern, candidate)

                        if amount_match:
                            total_raised = amount_match.group(0).replace(" ", "")
                            break

                    break

            break

    if total_raised == "£0":

        for i, line in enumerate(lines):

            line_lower = line.lower()

            if "raised" in line_lower or "fundraising" in line_lower:

                nearby_text = " ".join(lines[max(0, i - 4):i + 8])

                amounts = re.findall(money_pattern, nearby_text)

                if amounts:
                    total_raised = amounts[-1].replace(" ", "")
                    break

    donations = []

    donation_summary_index = len(lines)

    for i, line in enumerate(lines):

        if line.lower() == "donation summary":
            donation_summary_index = i
            break

    donation_lines = lines[:donation_summary_index]

    ignore_terms = [
        "give now",
        "share",
        "story",
        "read story",
        "donation",
        "gift aid",
        "justgiving",
        "fundraising",
        "target",
        "raised",
        "offline",
        "online",
        "fee",
        "learn more",
        "queens head",
        "andysmanclub"
    ]

    for i, line in enumerate(donation_lines):

        amount_match = re.search(money_pattern, line)

        if not amount_match:
            continue

        amount = amount_match.group(0).replace(" ", "")

        donor_name = "Anonymous"

        previous_lines = donation_lines[max(0, i - 10):i]

        for previous_line in reversed(previous_lines):

            previous_lower = previous_line.lower()

            if (
                previous_lower.startswith("#")
                or re.search(money_pattern, previous_line)
                or "ago" in previous_lower
                or any(term in previous_lower for term in ignore_terms)
            ):
                continue

            donor_name = previous_line
            break

        donations.append({
            "name": donor_name,
            "amount": amount
        })

        if len(donations) >= 6:
            break

    return total_raised, donations


def generate_qr_base64(url):

    qr = qrcode.make(url)

    buffer = BytesIO()

    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return qr_base64


@st.cache_data(ttl=60)
def get_raffle_entries():

    try:

        raffle_df = pd.read_csv(RAFFLE_SHEET_CSV_URL)

        raffle_df.columns = raffle_df.columns.str.strip()

        required_columns = ["Ticket Number", "Ticket Holder"]

        for column in required_columns:

            if column not in raffle_df.columns:
                return pd.DataFrame(columns=required_columns)

        raffle_df = raffle_df[required_columns]

        raffle_df["Ticket Number"] = raffle_df["Ticket Number"].astype(str)

        raffle_df["Ticket Holder"] = raffle_df["Ticket Holder"].astype(str)

        raffle_df = raffle_df.dropna(subset=["Ticket Number", "Ticket Holder"])

        raffle_df = raffle_df.sort_values(
            by="Ticket Number",
            key=lambda column: pd.to_numeric(column, errors="coerce")
        )

        return raffle_df

    except Exception as error:

        st.error(f"Could not load raffle entries: {error}")

        return pd.DataFrame(columns=["Ticket Number", "Ticket Holder"])


total_raised, donations = get_fundraising_data()

raffle_df = get_raffle_entries()


amount_match = re.search(r'£([\d,]+(?:\.\d+)?)', total_raised)

if amount_match:

    numeric_amount = float(
        amount_match.group(1).replace(",", "")
    )

else:

    numeric_amount = 0

progress_percent = min(
    int((numeric_amount / TARGET_AMOUNT) * 100),
    100
)


logo_col2, logo_col3 = st.columns([3.2, 1])

with logo_col2:

    st.markdown(
        f'<div class="main-title">{EVENT_NAME}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Supporting ANDYSMANCLUB</div>',
        unsafe_allow_html=True
    )

with logo_col3:
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    st.image(ANDYS_LOGO, width=500)


left_col, middle_col, right_col = st.columns([1, 1, 1])

qr_base64 = generate_qr_base64(JUSTGIVING_URL)


with left_col:

    left_card_html = f"""
<div class="dashboard-card">
    <div class="section-heading">Raised So Far</div>
    <div class="big-total">{total_raised}</div>
    <div class="progress-container">
        <div class="progress-bar" style="width:{progress_percent}%;">{progress_percent}%</div>
    </div>
    <div class="progress-helper">
        <span>{progress_percent}% funded</span>
        <span>Target £{TARGET_AMOUNT:,}</span>
    </div>
</div>
"""

    st.markdown(left_card_html, unsafe_allow_html=True)


with middle_col:

    if donations:

        donation_html = ""

        for donation in donations:

            donor_name = escape(donation.get("name", "Anonymous"))
            amount = escape(donation.get("amount", ""))

            donation_html += f"""
<div class="donation-box">
    <div>
        <span class="donor-name">{donor_name}</span>
        <span class="donation-amount">{amount}</span>
    </div>
</div>
"""

    else:

        donation_html = """
<div class="empty-donations">No recent donations found yet</div>
"""

    middle_card_html = f"""
<div class="dashboard-card">
    <div class="section-heading">Latest Supporters</div>
    {donation_html}
</div>
"""

    st.markdown(middle_card_html, unsafe_allow_html=True)


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
<div class="dashboard-card raffle-card">
    <div class="raffle-title">Raffle Ticket Search</div>
    <div class="raffle-helper">
        Search your name to find your raffle ticket numbers and winning odds.
    </div>
</div>
""",
    unsafe_allow_html=True
)

search_name = st.text_input(
    "Search your name",
    placeholder="Type your name here"
)

if search_name:

    filtered_raffle_df = raffle_df[
        raffle_df["Ticket Holder"].str.contains(search_name, case=False, na=False)
    ]

else:

    filtered_raffle_df = raffle_df

total_tickets = len(raffle_df)

user_tickets = len(filtered_raffle_df)

win_probability = 0

if total_tickets > 0:
    win_probability = round((user_tickets / total_tickets) * 100, 2)

raffle_left, raffle_right = st.columns([1.55, 0.85])


with raffle_left:

    tickets_title = "Matching Tickets" if search_name else "All Tickets"

    if filtered_raffle_df.empty:

        table_html = '<div class="raffle-empty">No raffle tickets found</div>'

    else:

        raffle_rows = ""

        for _, row in filtered_raffle_df.iterrows():

            ticket_number = escape(str(row["Ticket Number"]))
            name = escape(str(row["Ticket Holder"]))

            raffle_rows += f"<tr><td>{ticket_number}</td><td>{name}</td></tr>"

        table_html = f'<div class="raffle-table-wrapper"><table class="raffle-table"><thead><tr><th>Ticket Number</th><th>Ticket Holder</th></tr></thead><tbody>{raffle_rows}</tbody></table></div>'

    left_card_html = f'<div class="raffle-results-card"><div class="raffle-section-title">{tickets_title}</div>{table_html}</div>'

    st.markdown(left_card_html, unsafe_allow_html=True)


with raffle_right:

    pie_degrees = min(max(win_probability * 3.6, 0), 360)

    pie_background = f"conic-gradient(#e10600 0deg, #e10600 {pie_degrees}deg, #dddddd {pie_degrees}deg, #dddddd 360deg)"

    if user_tickets > 0:

        right_card_html = (
            f'<div class="raffle-results-card probability-wrapper probability-card">'
            f'<div class="raffle-section-title">Win Probability</div>'
            f'<div class="css-pie-wrapper">'
            f'<div class="css-pie" style="background:{pie_background};">'
            f'<div class="css-pie-hole"></div>'
            f'</div>'
            f'</div>'
            f'<div class="probability-number">{win_probability}%</div>'
            f'<div class="probability-label">Chance based on selected tickets</div>'
            f'<div class="ticket-count">{user_tickets} ticket(s) out of {total_tickets}</div>'
            f'</div>'
        )

    else:

        right_card_html = (
            '<div class="raffle-results-card probability-wrapper probability-card">'
            '<div class="raffle-section-title">Win Probability</div>'
            '<div class="raffle-empty">No tickets selected</div>'
            '</div>'
        )

    st.markdown(right_card_html, unsafe_allow_html=True)


st.markdown(
    """
    <div class="footer-banner">
        Supporting Men's Mental Health • Talk. Support. Change Lives.
    </div>
    """,
    unsafe_allow_html=True
)
