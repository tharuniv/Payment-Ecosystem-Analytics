import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import re


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Payment Ecosystem Analytics",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------------- GLOBAL ---------------- */

    .stApp {
        background-color: #f5f7fb;
    }

    .main .block-container {
        padding-top: 35px;
        padding-left: 55px;
        padding-right: 55px;
        max-width: 1500px;
    }

    /* ---------------- SIDEBAR ---------------- */

    section[data-testid="stSidebar"] {
        background-color: #111827;
        min-width: 280px;
        max-width: 280px;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    .sidebar-title {
        font-size: 25px;
        font-weight: 800;
        line-height: 1.25;
        margin-top: 20px;
        margin-bottom: 35px;
    }

    .sidebar-line {
        border-bottom: 1px solid #374151;
        margin-bottom: 30px;
    }

    .sidebar-footer {
        margin-top: 45px;
        padding-top: 25px;
        border-top: 1px solid #374151;
        color: #9ca3af !important;
        font-size: 14px;
        line-height: 1.8;
    }

    /* ---------------- HEADINGS ---------------- */

    .main-title {
        font-size: 43px;
        font-weight: 850;
        color: #12213f;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }

    .main-subtitle {
        font-size: 17px;
        color: #64748b;
        margin-bottom: 40px;
    }

    .section-title {
        font-size: 29px;
        font-weight: 750;
        color: #12213f;
        margin-top: 30px;
        margin-bottom: 5px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 16px;
        margin-bottom: 22px;
    }

    /* ---------------- KPI CARDS ---------------- */

    .kpi-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 17px;
        padding: 23px;
        min-height: 145px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.06);
    }

    .kpi-title {
        font-size: 15px;
        color: #64748b;
        margin-bottom: 14px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #12213f;
        word-break: break-word;
    }

    .kpi-description {
        font-size: 13px;
        color: #94a3b8;
        margin-top: 8px;
    }

    /* ---------------- INSIGHT BOX ---------------- */

    .insight {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 22px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.045);
    }

    .insight-title {
        font-size: 19px;
        font-weight: 750;
        color: #12213f;
        margin-bottom: 9px;
    }

    .insight-text {
        font-size: 15px;
        color: #475569;
        line-height: 1.7;
    }

    /* ---------------- RESULT CARDS ---------------- */

    .result-card {
        background: white;
        border-radius: 16px;
        padding: 22px;
        border: 1px solid #e2e8f0;
        margin-bottom: 18px;
    }

    .result-label {
        color: #64748b;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }

    .result-value {
        color: #12213f;
        font-size: 27px;
        font-weight: 800;
        margin-top: 7px;
    }

    /* ---------------- FOOTER ---------------- */

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 13px;
        padding-top: 50px;
        padding-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def section(title, subtitle=""):
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True
    )

    if subtitle:
        st.markdown(
            f'<div class="section-subtitle">{subtitle}</div>',
            unsafe_allow_html=True
        )


def card(title, value, description=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def format_number(value):
    if pd.isna(value):
        return "—"

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} B"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f} M"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.2f} K"

    return f"{value:,.0f}"


def find_file(patterns):
    """
    Search website folder for a file matching any supplied pattern.
    """
    for pattern in patterns:
        matches = list(BASE_DIR.rglob(pattern))

        if matches:
            return matches[0]

    return None


def load_csv_file(patterns):
    file_path = find_file(patterns)

    if file_path is None:
        return None

    try:
        return pd.read_csv(file_path)
    except Exception:
        return None


def load_excel_file(patterns):
    file_path = find_file(patterns)

    if file_path is None:
        return None

    try:
        return pd.read_excel(file_path)
    except Exception:
        return None


def get_month_order():
    return [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ]


# ============================================================
# LOAD MAIN DATASET
# ============================================================

df = load_csv_file([
    "ml_prepared_2025(4).csv",
    "ml_prepared_2025(3).csv",
    "ml_prepared_2025*.csv"
])

if df is None:

    st.error(
        """
        Main dataset could not be found.

        Please place `ml_prepared_2025(4).csv` inside the
        Payment_Ecosystem_Website folder.
        """
    )

    st.stop()


# ============================================================
# BASIC DATA PREPARATION
# ============================================================

if "Month_Num" in df.columns:
    df = df.sort_values("Month_Num")

if "Month" in df.columns:
    month_order = get_month_order()

    df["Month"] = pd.Categorical(
        df["Month"],
        categories=month_order,
        ordered=True
    )

    df = df.sort_values("Month_Num" if "Month_Num" in df.columns else "Month")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">
            💳 PAYMENT<br>
            ECOSYSTEM
        </div>

        <div class="sidebar-line"></div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Navigation")

    pages = [
        "Executive Overview",
        "Payment Ecosystem",
        "Infrastructure",
        "Growth Analysis",
        "Strategic Intelligence",
        "Statistical Analysis",
        "ML & Explainable AI",
        "Business Insights"
    ]

    page = st.radio(
        "",
        pages,
        index=0
    )

    st.markdown(
        """
        <div class="sidebar-footer">
            <b>Project Period</b><br>
            India<br>
            Jan–Dec 2025<br><br>

            <b>Datasets</b><br>
            ATM<br>
            PSI<br>
            NPCI
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">PAYMENT ECOSYSTEM ANALYTICS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'India | Jan–Dec 2025 | Payment Infrastructure, '
    'Transaction Activity & Growth Analysis'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    section(
        "Executive Overview",
        "A consolidated view of India's payment ecosystem using ATM, PSI and NPCI indicators."
    )

    # ---------------- KPI VALUES ----------------

    total_market = None
    total_card = None
    npci_value = None
    upi_total = None
    psi_value = None

    if "Total_Card_Payment_Volume" in df.columns:
        total_card = df["Total_Card_Payment_Volume"].sum()

    if "NPCI_Value_Bn" in df.columns:
        npci_value = df["NPCI_Value_Bn"].sum()

    if "UPI_QR" in df.columns:
        upi_total = df["UPI_QR"].sum()

    if "PSI_Value_Current_Month" in df.columns:
        psi_value = df["PSI_Value_Current_Month"].sum()

    market_columns = [
        c for c in [
            "CC_POS_Volume",
            "CC_Online_Volume",
            "UPI_QR",
            "POS",
            "Credit_Cards",
            "Debit_Cards",
            "Micro_ATM",
            "DC_ATM_Withdrawal_Volume",
            "DC_POS_Volume",
            "Bharat_QR",
            "DC_Online_Volume"
        ]
        if c in df.columns
    ]

    if market_columns:
        total_market = df[market_columns].sum().sum()

    # ---------------- KPI ROW ----------------

    cols = st.columns(5)

    with cols[0]:
        card(
            "Total Payment Market",
            format_number(total_market),
            "Total analysed payment activity"
        )

    with cols[1]:
        card(
            "Total Card Payment",
            format_number(total_card),
            "Credit + debit card payment volume"
        )

    with cols[2]:
        card(
            "NPCI Value",
            format_number(npci_value),
            "NPCI transaction value indicator"
        )

    with cols[3]:
        card(
            "UPI Transactions",
            format_number(upi_total),
            "UPI QR activity"
        )

    with cols[4]:
        card(
            "PSI Value",
            format_number(psi_value),
            "PSI current-month value"
        )

    # ---------------- TREND ----------------

    section(
        "Payment Ecosystem Trend",
        "Monthly movement across NPCI, PSI and card-payment indicators."
    )

    trend_columns = []

    for c in [
        "NPCI_Value_Bn",
        "PSI_Value_Current_Month",
        "Total_Card_Payment_Volume"
    ]:

        if c in df.columns:
            trend_columns.append(c)

    if trend_columns:

        trend = df[
            ["Month"] + trend_columns
        ].copy()

        trend_long = trend.melt(
            id_vars="Month",
            var_name="Indicator",
            value_name="Value"
        )

        fig = px.line(
            trend_long,
            x="Month",
            y="Value",
            color="Indicator",
            markers=True,
            title="NPCI, PSI and Card Payment Trends"
        )

        fig.update_layout(
            height=470,
            template="plotly_white",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------- CHANNEL RANKING ----------------

    section(
        "Payment Channel Activity",
        "Ranking of major payment channels by 2025 transaction volume."
    )

    ranking_columns = [
        "UPI_QR",
        "DC_ATM_Withdrawal_Volume",
        "CC_POS_Volume",
        "CC_Online_Volume",
        "DC_POS_Volume",
        "DC_Online_Volume",
        "POS",
        "Bharat_QR",
        "Micro_ATM"
    ]

    ranking_columns = [
        c for c in ranking_columns
        if c in df.columns
    ]

    if ranking_columns:

        ranking = (
            df[ranking_columns]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )

        ranking.columns = [
            "Channel",
            "Volume"
        ]

        channel_names = {
            "UPI_QR": "UPI QR",
            "DC_ATM_Withdrawal_Volume": "ATM Withdrawal",
            "CC_POS_Volume": "Credit Card POS",
            "CC_Online_Volume": "Credit Card Online",
            "DC_POS_Volume": "Debit Card POS",
            "DC_Online_Volume": "Debit Card Online",
            "POS": "POS",
            "Bharat_QR": "Bharat QR",
            "Micro_ATM": "Micro ATM"
        }

        ranking["Channel"] = ranking["Channel"].map(
            lambda x: channel_names.get(x, x)
        )

        fig = px.bar(
            ranking,
            x="Volume",
            y="Channel",
            orientation="h",
            text_auto=".3s",
            title="Payment Channel Ranking — 2025"
        )

        fig.update_layout(
            height=550,
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------- KEY FINDINGS ----------------

    section(
        "Executive Findings",
        "Major findings from the completed payment ecosystem analysis."
    )

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">Digital payment momentum</div>
            <div class="insight-text">
                UPI QR remains one of the largest payment channels and
                continues to show strong growth during the analysed year.
            </div>
        </div>

        <div class="insight">
            <div class="insight-title">Credit card growth</div>
            <div class="insight-text">
                Credit Card POS and Credit Card Online activity show some
                of the strongest Q1-to-Q4 growth among the analysed channels.
            </div>
        </div>

        <div class="insight">
            <div class="insight-title">Traditional payment pressure</div>
            <div class="insight-text">
                Several debit-card and ATM-related channels show declining
                activity during the year, indicating a shift in payment behaviour.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE 2 — PAYMENT ECOSYSTEM
# ============================================================

elif page == "Payment Ecosystem":

    section(
        "Payment Ecosystem",
        "Detailed analysis of payment channels, cards, PSI and NPCI activity."
    )

    # ---------------- QUARTER FILTER ----------------

    if "Quarter" in df.columns:

        quarter = st.selectbox(
            "Select Quarter",
            ["All"] + sorted(df["Quarter"].dropna().unique().tolist())
        )

        if quarter != "All":
            page_df = df[df["Quarter"] == quarter].copy()
        else:
            page_df = df.copy()

    else:
        page_df = df.copy()

    # ---------------- DIGITAL VS CARD ----------------

    digital_columns = [
        "UPI_QR",
        "CC_POS_Volume",
        "CC_Online_Volume",
        "DC_POS_Volume",
        "DC_Online_Volume"
    ]

    digital_columns = [
        c for c in digital_columns
        if c in page_df.columns
    ]

    if digital_columns:

        section(
            "Digital vs Card Payment Activity",
            "Comparison of major digital and card-based channels."
        )

        temp = (
            page_df[digital_columns]
            .sum()
            .reset_index()
        )

        temp.columns = [
            "Channel",
            "Volume"
        ]

        names = {
            "UPI_QR": "UPI QR",
            "CC_POS_Volume": "Credit Card POS",
            "CC_Online_Volume": "Credit Card Online",
            "DC_POS_Volume": "Debit Card POS",
            "DC_Online_Volume": "Debit Card Online"
        }

        temp["Channel"] = temp["Channel"].map(
            lambda x: names.get(x, x)
        )

        fig = px.bar(
            temp,
            x="Channel",
            y="Volume",
            text_auto=".3s",
            title="Digital & Card Payment Channels"
        )

        fig.update_layout(
            template="plotly_white",
            height=470
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------- UPI ----------------

    if "UPI_QR" in df.columns:

        section(
            "UPI Growth Trend",
            "Monthly UPI QR transaction activity."
        )

        fig = px.area(
            df,
            x="Month",
            y="UPI_QR",
            markers=True,
            title="UPI QR Transaction Trend"
        )

        fig.update_layout(
            template="plotly_white",
            height=430
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------- PSI ----------------

    psi_cols = [
        "PSI_Volume_Current_Month",
        "PSI_Value_Current_Month"
    ]

    if all(c in df.columns for c in psi_cols):

        section(
            "PSI Payment Activity",
            "Current-month PSI volume and value indicators."
        )

        psi_plot = df[
            ["Month"] + psi_cols
        ].copy()

        psi_long = psi_plot.melt(
            id_vars="Month",
            var_name="Indicator",
            value_name="Value"
        )

        fig = px.line(
            psi_long,
            x="Month",
            y="Value",
            color="Indicator",
            markers=True,
            title="PSI Current-Month Activity"
        )

        fig.update_layout(
            template="plotly_white",
            height=430
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# PAGE 3 — INFRASTRUCTURE
# ============================================================

elif page == "Infrastructure":

    section(
        "Payment Infrastructure",
        "Infrastructure supporting India's payment ecosystem."
    )

    # ---------------- ATM ----------------

    atm_columns = [
        "ATM_Onsite",
        "ATM_Offsite"
    ]

    atm_columns = [
        c for c in atm_columns
        if c in df.columns
    ]

    if atm_columns:

        section(
            "ATM Infrastructure Trend",
            "Onsite and offsite ATM infrastructure during 2025."
        )

        atm = df[
            ["Month"] + atm_columns
        ].copy()

        atm_long = atm.melt(
            id_vars="Month",
            var_name="Infrastructure",
            value_name="Count"
        )

        names = {
            "ATM_Onsite": "ATM Onsite",
            "ATM_Offsite": "ATM Offsite"
        }

        atm_long["Infrastructure"] = atm_long[
            "Infrastructure"
        ].map(
            lambda x: names.get(x, x)
        )

        fig = px.line(
            atm_long,
            x="Month",
            y="Count",
            color="Infrastructure",
            markers=True,
            title="ATM Infrastructure Trend"
        )

        fig.update_layout(
            template="plotly_white",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------- DIGITAL INFRASTRUCTURE ----------------

    infrastructure_columns = [
        "Total_QR_Infrastructure",
        "Total_ATM_Infrastructure",
        "Total_Digital_Infrastructure"
    ]

    available_infrastructure = [
        c for c in infrastructure_columns
        if c in df.columns
    ]

    if available_infrastructure:

        section(
            "Digital Infrastructure",
            "Aggregated infrastructure indicators from the combined dataset."
        )

        infra = (
            df[available_infrastructure]
            .sum()
            .reset_index()
        )

        infra.columns = [
            "Infrastructure",
            "Count"
        ]

        fig = px.bar(
            infra,
            x="Infrastructure",
            y="Count",
            text_auto=".3s",
            title="Payment Infrastructure Comparison"
        )

        fig.update_layout(
            template="plotly_white",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------- INFRASTRUCTURE KPIs ----------------

    cols = st.columns(3)

    for i, c in enumerate(available_infrastructure[:3]):

        with cols[i]:

            card(
                c.replace("_", " "),
                format_number(df[c].sum()),
                "2025 aggregate"
            )


# ============================================================
# PAGE 4 — GROWTH ANALYSIS
# ============================================================

elif page == "Growth Analysis":

    section(
        "Growth & Comparative Analysis",
        "Q1-to-Q4 growth across major payment ecosystem indicators."
    )

    growth_columns = [
        "CC_POS_Volume",
        "CC_Online_Volume",
        "UPI_QR",
        "POS",
        "Credit_Cards",
        "Debit_Cards",
        "Micro_ATM",
        "DC_ATM_Withdrawal_Volume",
        "DC_POS_Volume",
        "Bharat_QR",
        "DC_Online_Volume",
        "PSI_Volume_Current_Month",
        "PSI_Value_Current_Month",
        "NPCI_Value_Bn",
        "NPCI_Volume_Mn",
        "ATM_Onsite",
        "ATM_Offsite"
    ]

    growth_columns = [
        c for c in growth_columns
        if c in df.columns
    ]

    if "Quarter" in df.columns:

        quarterly = (
            df.groupby("Quarter", observed=True)[growth_columns]
            .sum()
            .reset_index()
        )

        quarter_order = [
            "Q1",
            "Q2",
            "Q3",
            "Q4"
        ]

        quarterly["Quarter"] = pd.Categorical(
            quarterly["Quarter"],
            categories=quarter_order,
            ordered=True
        )

        quarterly = quarterly.sort_values("Quarter")

        if len(quarterly) >= 2:

            q1 = quarterly.iloc[0]
            q4 = quarterly.iloc[-1]

            growth_data = []

            for c in growth_columns:

                start = q1[c]
                end = q4[c]

                if start != 0:

                    growth = (
                        (end - start) /
                        abs(start)
                    ) * 100

                else:
                    growth = np.nan

                growth_data.append(
                    [
                        c,
                        start,
                        end,
                        growth
                    ]
                )

            growth_df = pd.DataFrame(
                growth_data,
                columns=[
                    "Indicator",
                    "Q1",
                    "Q4",
                    "Growth_Percent"
                ]
            )

            growth_df = growth_df.sort_values(
                "Growth_Percent",
                ascending=False
            )

            section(
                "Q1 → Q4 Growth",
                "Percentage change from the first quarter to the fourth quarter."
            )

            fig = px.bar(
                growth_df,
                x="Growth_Percent",
                y="Indicator",
                orientation="h",
                text="Growth_Percent",
                title="Payment Ecosystem Growth — Q1 to Q4"
            )

            fig.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside"
            )

            fig.update_layout(
                template="plotly_white",
                height=650
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            display_df = growth_df.copy()

            display_df["Q1"] = display_df["Q1"].map(
                format_number
            )

            display_df["Q4"] = display_df["Q4"].map(
                format_number
            )

            display_df["Growth"] = growth_df[
                "Growth_Percent"
            ].map(
                lambda x: f"{x:.2f}%" if pd.notna(x) else "—"
            )

            display_df = display_df[
                [
                    "Indicator",
                    "Q1",
                    "Q4",
                    "Growth"
                ]
            ]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# PAGE 5 — STRATEGIC INTELLIGENCE
# ============================================================

elif page == "Strategic Intelligence":

    section(
        "Strategic Intelligence",
        "Business-oriented interpretation of payment channel growth, share and strategic priority."
    )

    # ---------------- STRATEGIC RESULTS ----------------

    strategic_data = pd.DataFrame(
        [
            ["CC POS", 21.51, 1.10, 95.95, "Invest / Expand"],
            ["CC Online", 20.55, 1.01, 92.91, "Invest / Expand"],
            ["UPI QR", 11.77, 1.18, 79.06, "Invest / Expand"],
            ["Credit Cards", 5.14, -0.05, 67.14, "Grow Selectively"],
            ["POS", 8.92, 0.01, 64.17, "Grow Selectively"],
            ["Debit Cards", 4.55, -0.60, 53.77, "Grow Selectively"],
            ["Micro ATM", -2.65, 0.00, 44.41, "Monitor"],
            ["Bharat QR", -9.23, 0.00, 34.50, "Monitor"],
            ["DC POS", -8.57, -0.43, 32.33, "Monitor"],
            ["DC Online", -13.53, -0.20, 24.81, "Monitor"],
            ["ATM Withdrawal", -5.97, -1.99, 23.17, "Reduce / Transform"]
        ],
        columns=[
            "Channel",
            "Q1_Q4_Growth",
            "Share_Gain_pp",
            "Strategic_Score",
            "Strategy"
        ]
    )

    # ---------------- KPI ----------------

    cols = st.columns(4)

    with cols[0]:
        card(
            "Market Growth",
            "6.37%",
            "Overall Q1 → Q4 growth"
        )

    with cols[1]:
        card(
            "Top Priority",
            "CC POS",
            "Strategic score 95.95"
        )

    with cols[2]:
        card(
            "Largest Share Gain",
            "UPI QR",
            "+1.18 percentage points"
        )

    with cols[3]:
        card(
            "Largest Share Loss",
            "ATM Withdrawal",
            "-1.99 percentage points"
        )

    # ---------------- STRATEGIC SCORE ----------------

    section(
        "Strategic Action Priority",
        "Higher scores indicate stronger strategic priority in the completed analysis."
    )

    score_plot = strategic_data.sort_values(
        "Strategic_Score"
    )

    fig = px.bar(
        score_plot,
        x="Strategic_Score",
        y="Channel",
        orientation="h",
        text="Strategic_Score",
        title="Strategic Action Score by Payment Channel"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_white",
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------- TABLE ----------------

    st.dataframe(
        strategic_data.style.format(
            {
                "Q1_Q4_Growth": "{:.2f}%",
                "Share_Gain_pp": "{:.2f}",
                "Strategic_Score": "{:.2f}"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    # ---------------- STRATEGIC INSIGHTS ----------------

    section(
        "Strategic Findings",
        "Key business implications from the channel-level analysis."
    )

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">
                1. Prioritize digital growth
            </div>
            <div class="insight-text">
                UPI QR, Credit Card POS and Credit Card Online show strong
                growth and strategic importance. These channels represent
                the strongest expansion opportunities in the analysis.
            </div>
        </div>

        <div class="insight">
            <div class="insight-title">
                2. Protect dominant channels
            </div>
            <div class="insight-text">
                Debit Cards remain a major contributor to payment activity
                even though their growth rate is lower than the strongest
                emerging channels.
            </div>
        </div>

        <div class="insight">
            <div class="insight-title">
                3. Transform declining channels
            </div>
            <div class="insight-text">
                ATM withdrawal and some debit-card channels show declining
                activity. These channels should be monitored and strategically
                transformed rather than treated as primary growth engines.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE 6 — STATISTICAL ANALYSIS
# ============================================================

elif page == "Statistical Analysis":

    section(
        "Statistical Analysis",
        "Descriptive statistics, relationships and hypothesis testing from the completed project workflow."
    )

    # ========================================================
    # DESCRIPTIVE STATISTICS
    # ========================================================

    section(
        "Descriptive Statistics",
        "Summary statistics for numerical payment ecosystem variables."
    )

    numeric_df = df.select_dtypes(
        include=np.number
    )

    if not numeric_df.empty:

        selected_numeric = st.multiselect(
            "Select variables",
            numeric_df.columns.tolist(),
            default=numeric_df.columns.tolist()[:8]
        )

        if selected_numeric:

            stats = numeric_df[
                selected_numeric
            ].describe().T

            stats = stats.reset_index()

            stats = stats.rename(
                columns={
                    "index": "Variable"
                }
            )

            st.dataframe(
                stats,
                use_container_width=True,
                hide_index=True
            )

    # ========================================================
    # CORRELATION
    # ========================================================

    section(
        "Correlation Analysis",
        "Correlation measures the strength and direction of association between numerical variables."
    )

    correlation_columns = st.multiselect(
        "Select variables for correlation matrix",
        numeric_df.columns.tolist(),
        default=[
            c for c in [
                "Debit_Cards",
                "PSI_Volume_Current_Month",
                "CC_Online_Volume",
                "UPI_QR",
                "NPCI_Volume_Mn",
                "NPCI_Value_Bn"
            ]
            if c in numeric_df.columns
        ]
    )

    if len(correlation_columns) >= 2:

        corr = df[
            correlation_columns
        ].corr()

        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            title="Correlation Matrix"
        )

        fig.update_layout(
            height=650,
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">Interpretation</div>
            <div class="insight-text">
                Correlation identifies association between variables.
                A strong correlation does not by itself establish a causal
                relationship.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # HYPOTHESIS TESTING
    # ========================================================

    section(
        "Hypothesis Testing",
        "Statistical hypotheses were evaluated as part of the completed analytical workflow."
    )

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">
                Why Hypothesis Testing?
            </div>

            <div class="insight-text">
                Descriptive statistics and correlation analysis reveal
                patterns in the payment ecosystem. Hypothesis testing
                provides a formal statistical framework for evaluating
                whether an observed relationship or difference has
                sufficient evidence against a null hypothesis.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- SIGNIFICANCE LEVEL ----------------

    hcols = st.columns(3)

    with hcols[0]:
        card(
            "Significance Level",
            "α = 0.05",
            "Statistical decision threshold"
        )

    with hcols[1]:
        card(
            "Decision Rule",
            "p < 0.05",
            "Reject H₀"
        )

    with hcols[2]:
        card(
            "Interpretation",
            "Statistical Evidence",
            "Not causal evidence"
        )

    # ========================================================
    # AUTOMATIC NOTEBOOK READER
    # ========================================================

    hypothesis_file = find_file([
        "hypothesis_testing(2).ipynb",
        "hypothesis_testing*.ipynb",
        "Hypothesis_Testing.ipynb",
        "hypothesis_testing.ipynb"
    ])

    if hypothesis_file is not None:

        st.success(
            f"Loaded hypothesis-testing notebook: {hypothesis_file.name}"
        )

        try:

            with open(
                hypothesis_file,
                "r",
                encoding="utf-8"
            ) as f:

                notebook = json.load(f)

            markdown_sections = []
            output_sections = []

            for cell in notebook.get(
                "cells",
                []
            ):

                cell_type = cell.get(
                    "cell_type",
                    ""
                )

                source = "".join(
                    cell.get(
                        "source",
                        []
                    )
                )

                if cell_type == "markdown" and source.strip():

                    markdown_sections.append(
                        source
                    )

                if cell_type == "code":

                    for output in cell.get(
                        "outputs",
                        []
                    ):

                        text = ""

                        if "text" in output:

                            text = "".join(
                                output["text"]
                            )

                        elif "data" in output:

                            if "text/plain" in output["data"]:

                                text = "".join(
                                    output["data"]["text/plain"]
                                )

                        if text.strip():

                            output_sections.append(
                                text
                            )

            # ---------------- NOTEBOOK RESULTS ----------------

            if markdown_sections:

                section(
                    "Hypothesis Testing Methodology",
                    "Methodology and hypotheses recorded in the completed notebook."
                )

                for text in markdown_sections:

                    clean_text = text.strip()

                    if (
                        "hypoth" in clean_text.lower()
                        or "null" in clean_text.lower()
                        or "alternative" in clean_text.lower()
                        or "test" in clean_text.lower()
                    ):

                        st.markdown(
                            clean_text
                        )

            # ---------------- ACTUAL OUTPUTS ----------------

            if output_sections:

                section(
                    "Recorded Test Results",
                    "These results are read directly from the completed hypothesis-testing notebook."
                )

                for result in output_sections:

                    st.code(
                        result,
                        language="text"
                    )

            else:

                st.info(
                    """
                    The hypothesis-testing notebook was found, but it does
                    not contain stored text outputs. Open the notebook and
                    save it after running the statistical test cells.
                    """
                )

        except Exception as e:

            st.warning(
                f"Could not read the hypothesis-testing notebook: {e}"
            )

    else:

        st.warning(
            """
            `hypothesis_testing(2).ipynb` was not found in the website folder.

            Put the completed hypothesis-testing notebook in the same folder
            as `app.py`. The website will automatically display its actual
            hypotheses, test results and p-values.
            """
        )

    # ========================================================
    # HYPOTHESIS FRAMEWORK
    # ========================================================

    section(
        "Hypothesis Testing Framework",
        "How statistical hypotheses are interpreted."
    )

    framework = pd.DataFrame(
        [
            [
                "H₀",
                "Null Hypothesis",
                "No statistically significant relationship or difference"
            ],
            [
                "H₁",
                "Alternative Hypothesis",
                "A statistically significant relationship or difference exists"
            ],
            [
                "α",
                "Significance Level",
                "0.05"
            ],
            [
                "Decision",
                "p-value",
                "p < 0.05 → Reject H₀"
            ]
        ],
        columns=[
            "Symbol",
            "Component",
            "Meaning"
        ]
    )

    st.dataframe(
        framework,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # CORRELATION VS HYPOTHESIS TESTING
    # ========================================================

    section(
        "Correlation vs Hypothesis Testing",
        "Two complementary statistical approaches used in the project."
    )

    comparison = pd.DataFrame(
        [
            [
                "Correlation",
                "Measures association",
                "Correlation coefficient"
            ],
            [
                "Hypothesis Testing",
                "Evaluates statistical evidence",
                "Test statistic + p-value"
            ],
            [
                "Business Interpretation",
                "Identifies relationships",
                "Supports statistical decision-making"
            ]
        ],
        columns=[
            "Analysis",
            "Purpose",
            "Typical Output"
        ]
    )

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">
                Statistical Limitation
            </div>

            <div class="insight-text">
                The statistical results should be interpreted within the
                scope of the analysed 2025 payment ecosystem data.
                Statistical association should not be interpreted as proof
                of causation.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE 7 — ML & EXPLAINABLE AI
# ============================================================

elif page == "ML & Explainable AI":

    section(
        "ML & Explainable AI",
        "Predictive modelling and feature-influence analysis completed for NPCI value and volume."
    )

    # ---------------- TARGETS ----------------

    cols = st.columns(2)

    with cols[0]:

        card(
            "Prediction Target",
            "NPCI Value",
            "NPCI_Value_Bn"
        )

    with cols[1]:

        card(
            "Prediction Target",
            "NPCI Volume",
            "NPCI_Volume_Mn"
        )

    # ---------------- METHODOLOGY ----------------

    section(
        "Predictive Modelling",
        "Machine-learning models were developed to analyse NPCI value and volume."
    )

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">
                Model validation
            </div>

            <div class="insight-text">
                The completed ML workflow used quarterly modelling because
                the monthly NPCI target values contain repeated quarterly
                information. Model validation and comparison were performed
                separately from the explainability analysis.
            </div>
        </div>

        <div class="insight">
            <div class="insight-title">
                Explainable AI
            </div>

            <div class="insight-text">
                Explainable AI was used to understand which features had the
                strongest local influence on the model predictions.
                These feature contributions should be treated as model-based
                evidence rather than causal relationships.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # XAI DATA FILES
    # ========================================================

    xai_files = [
        "step16_final_xai_evidence_table_2025.csv",
        "npcivalue_final_local_xai_summary_2025.csv",
        "npcivolume_final_local_xai_summary_2025.csv",
        "final_xai_consolidated_report_2025.csv",
        "final_xai_target_comparison_2025.csv"
    ]

    found_xai = []

    for filename in xai_files:

        path = find_file([filename])

        if path is not None:
            found_xai.append(path)

    if found_xai:

        section(
            "Explainable AI Evidence",
            "Available XAI result files from the completed ML workflow."
        )

        selected_xai = st.selectbox(
            "Select XAI result",
            found_xai,
            format_func=lambda x: x.name
        )

        try:

            xai_df = pd.read_csv(
                selected_xai
            )

            st.dataframe(
                xai_df,
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:

            st.warning(
                f"Could not read XAI result: {e}"
            )

    # ---------------- XAI SUMMARY ----------------

    section(
        "Top XAI Features",
        "Feature influence rankings recorded in the completed analysis."
    )

    xai_summary = pd.DataFrame(
        [
            [
                "NPCI Value",
                "Bharat_QR",
                "Dominant model contribution"
            ],
            [
                "NPCI Value",
                "DC_ATM_Withdrawal_Volume",
                "Strong model contribution"
            ],
            [
                "NPCI Value",
                "Micro_ATM",
                "Strong model contribution"
            ],
            [
                "NPCI Value",
                "DC_Online_Volume",
                "Strong model contribution"
            ],
            [
                "NPCI Value",
                "Month_Sin",
                "Temporal feature contribution"
            ],
            [
                "NPCI Volume",
                "DC_ATM_Withdrawal_Volume",
                "Strong model contribution"
            ],
            [
                "NPCI Volume",
                "PSI_Value_Previous_Month",
                "Strong model contribution"
            ],
            [
                "NPCI Volume",
                "POS",
                "Strong model contribution"
            ],
            [
                "NPCI Volume",
                "Month_Sin",
                "Temporal feature contribution"
            ],
            [
                "NPCI Volume",
                "Debit_Cards",
                "Strong model contribution"
            ]
        ],
        columns=[
            "Target",
            "Feature",
            "Interpretation"
        ]
    )

    st.dataframe(
        xai_summary,
        use_container_width=True,
        hide_index=True
    )

    st.warning(
        """
        XAI feature rankings describe model behaviour. They should not be
        interpreted as causal evidence. The effective quarterly sample is
        small, so these rankings are exploratory and may be unstable.
        """
    )


# ============================================================
# PAGE 8 — BUSINESS INSIGHTS
# ============================================================

elif page == "Business Insights":

    section(
        "Business Insights",
        "Business-oriented conclusions derived from the complete payment ecosystem analysis."
    )

    # ---------------- OVERALL MARKET ----------------

    section(
        "Overall Market Movement",
        "The payment ecosystem expanded from Q1 to Q4."
    )

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">
                Overall payment market growth: 6.37%
            </div>

            <div class="insight-text">
                Total analysed payment activity increased from Q1 to Q4,
                indicating continued expansion of the payment ecosystem
                during 2025.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- DIGITAL ----------------

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">
                Digital payment channels are strengthening
            </div>

            <div class="insight-text">
                UPI QR recorded approximately 11.77% Q1-to-Q4 growth and
                gained about 1.18 percentage points of market share.
                This supports continued attention toward digital payment
                infrastructure and adoption.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- CREDIT CARD ----------------

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">
                Credit card channels show strong momentum
            </div>

            <div class="insight-text">
                Credit Card POS increased by approximately 21.51% and
                Credit Card Online increased by approximately 20.55%
                from Q1 to Q4.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- ATM ----------------

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">
                ATM and some debit channels are under pressure
            </div>

            <div class="insight-text">
                ATM Withdrawal, Debit Card POS and Debit Card Online show
                declining Q1-to-Q4 activity. This suggests that some
                traditional channels are losing relative momentum.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- STRATEGY ----------------

    section(
        "Recommended Business Actions",
        "Strategic actions based on the completed channel analysis."
    )

    recommendations = pd.DataFrame(
        [
            [
                "UPI QR",
                "Invest / Expand",
                "Strong digital growth and largest share gain"
            ],
            [
                "Credit Card POS",
                "Invest / Expand",
                "Highest strategic priority and strongest growth"
            ],
            [
                "Credit Card Online",
                "Invest / Expand",
                "Strong online payment growth"
            ],
            [
                "Debit Cards",
                "Protect / Grow Selectively",
                "Large existing contribution but slower growth"
            ],
            [
                "ATM Withdrawal",
                "Reduce / Transform",
                "Declining activity and largest share loss"
            ],
            [
                "Debit Card Online",
                "Monitor",
                "Strongest decline among selected channels"
            ]
        ],
        columns=[
            "Channel",
            "Recommended Action",
            "Reason"
        ]
    )

    st.dataframe(
        recommendations,
        use_container_width=True,
        hide_index=True
    )

    # ---------------- FINAL MESSAGE ----------------

    st.markdown(
        """
        <div class="insight">
            <div class="insight-title">
                Final Project Conclusion
            </div>

            <div class="insight-text">
                The 2025 payment ecosystem shows continued overall growth,
                with digital and credit-card channels gaining momentum while
                several traditional debit-card and ATM channels decline.
                The combined ATM, PSI and NPCI analysis provides a broader
                view of payment infrastructure, transaction activity,
                comparative growth, statistical relationships, strategic
                priorities and predictive modelling.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        PAYMENT ECOSYSTEM ANALYTICS · INDIA · 2025
        <br>
        ATM · PSI · NPCI · EDA · STATISTICS · STRATEGY · ML · XAI
    </div>
    """,
    unsafe_allow_html=True
)