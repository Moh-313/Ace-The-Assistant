def load_css():
    return """
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #111827;
    }

    .main-title {
        font-size: 40px;
        font-weight: 800;
        color: #0B5ED7;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #4B5563;
        margin-bottom: 25px;
    }

    .hero-card {
        background: linear-gradient(135deg, #EAF3FF, #FFFFFF);
        padding: 26px;
        border-radius: 24px;
        border: 1px solid #D8E8FF;
        margin-bottom: 20px;
    }

    .card {
        background-color: #EAF3FF;
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 16px;
        border-left: 6px solid #0B5ED7;
    }

    .white-card {
        background-color: #FFFFFF;
        padding: 18px;
        border-radius: 18px;
        border: 1px solid #D8E8FF;
        margin-bottom: 14px;
    }

    .status-pill {
        display: inline-block;
        background-color: #EAF3FF;
        color: #063970;
        padding: 8px 14px;
        border-radius: 999px;
        font-weight: 600;
        margin: 4px 4px 8px 0;
    }

    .footer {
        color: #4B5563;
        font-size: 13px;
        text-align: center;
        margin-top: 35px;
    }

    [data-testid="stSidebar"] {
        background-color: #EAF3FF;
    }
    </style>
    """