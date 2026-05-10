import streamlit as st


def apply_app_theme():
    st.markdown(
        """
        <style>
        :root {
            --page-bg: #f5f7fb;
            --surface: #ffffff;
            --text: #16202a;
            --muted: #5d6b7a;
            --border: #d9e2ec;
            --primary: #0b5cab;
            --primary-hover: #084985;
            --success: #117a4f;
            --warning: #a55f00;
            --route: #0f766e;
        }

        html, body, [class*="css"] {
            font-family: "Noto Sans TC", "Microsoft JhengHei", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--text);
        }

        .stApp {
            background: var(--page-bg);
        }

        .block-container {
            max-width: 1220px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stWidgetLabel"] p {
            letter-spacing: 0;
            color: var(--text) !important;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--border);
        }

        .app-header {
            padding: 22px 0 18px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 18px;
        }

        .app-kicker {
            color: var(--route);
            font-size: 13px;
            font-weight: 800;
            letter-spacing: .02em;
            margin-bottom: 7px;
        }

        .app-title {
            color: var(--text) !important;
            font-size: clamp(28px, 4vw, 34px);
            line-height: 1.18;
            font-weight: 800;
            margin: 0;
        }

        .app-description {
            max-width: 760px;
            color: var(--muted) !important;
            font-size: 16px;
            line-height: 1.65;
            margin: 10px 0 0;
        }

        .home-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
            margin-top: 20px;
        }

        .choice-card {
            min-height: 132px;
            padding: 18px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            color: var(--text) !important;
        }

        .choice-card strong {
            display: block;
            color: var(--text) !important;
            font-size: 18px;
            margin-bottom: 8px;
        }

        .choice-card span {
            color: var(--muted) !important;
            font-size: 14px;
            line-height: 1.55;
        }

        .status-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin: 12px 0 18px;
        }

        .status-item {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            padding: 13px 14px;
        }

        .status-label {
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .status-value {
            color: var(--text);
            font-size: 18px;
            font-weight: 800;
            line-height: 1.2;
        }

        .route-summary {
            border-left: 4px solid var(--route);
            background: #ffffff;
            border-radius: 8px;
            border-top: 1px solid var(--border);
            border-right: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
            padding: 14px 16px;
            margin: 12px 0;
        }

        .route-summary-title {
            font-weight: 800;
            margin-bottom: 7px;
        }

        .route-summary-body {
            color: var(--muted);
            line-height: 1.6;
            font-size: 14px;
        }

        div.stButton > button,
        div.stFormSubmitButton > button {
            background: #ffffff;
            border-radius: 8px;
            color: var(--text);
            font-weight: 750;
            min-height: 42px;
            border: 1px solid var(--border);
        }

        div.stButton > button[kind="primary"],
        div.stFormSubmitButton > button[kind="primary"] {
            background: var(--primary);
            border-color: var(--primary);
            color: #ffffff;
        }

        div.stButton > button[kind="primary"] p,
        div.stFormSubmitButton > button[kind="primary"] p {
            color: #ffffff !important;
        }

        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
            border-color: var(--primary);
            color: var(--primary);
        }

        div.stButton > button[kind="primary"]:hover,
        div.stFormSubmitButton > button[kind="primary"]:hover {
            background: var(--primary-hover);
            border-color: var(--primary-hover);
            color: #ffffff;
        }

        [data-testid="stSelectbox"],
        [data-testid="stTextInput"],
        [data-testid="stRadio"] {
            margin-bottom: .4rem;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] {
            background: #ffffff !important;
            border-color: var(--border) !important;
            border-radius: 8px !important;
            color: var(--text) !important;
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="input"] input {
            color: var(--text) !important;
        }

        [role="radiogroup"] label,
        [role="radiogroup"] p {
            color: var(--text) !important;
        }

        [data-testid="stAlert"] {
            border-radius: 8px;
        }

        @media (max-width: 760px) {
            .home-grid,
            .status-strip {
                grid-template-columns: 1fr;
            }

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(kicker, title, description):
    st.markdown(
        f"""
        <section class="app-header">
            <div class="app-kicker">{kicker}</div>
            <h1 class="app-title">{title}</h1>
            <p class="app-description">{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_status_strip(items):
    cells = []
    for label, value in items:
        cells.append(
            f'<div class="status-item"><div class="status-label">{label}</div><div class="status-value">{value}</div></div>'
        )
    st.markdown(f"""<div class="status-strip">{''.join(cells)}</div>""", unsafe_allow_html=True)
