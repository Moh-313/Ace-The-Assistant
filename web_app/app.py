import streamlit as st
from datetime import datetime
from utils.styles import load_css
from utils.terminal_logs import generate_terminal_logs

st.set_page_config(
    page_title="Ace The Assistant",
    page_icon="✨",
    layout="wide"
)

st.markdown(load_css(), unsafe_allow_html=True)

st.sidebar.title("✨ Ace")
st.sidebar.caption("The Assistant")

page = st.sidebar.radio(
    "Menu",
    [
        "Home",
        "About Ace",
        "Features",
        "Status Dashboard",
        "Ace Terminal",
        "Update History",
        "Settings"
    ]
)

if page == "Home":
    st.markdown('<div class="main-title">Ace The Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Your intelligent assistant for information, interaction, and system monitoring.</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="hero-card">
        <h3>Hi, I’m Ace ✨</h3>
        <p>
        Ace is a friendly assistant interface designed to make interaction with technology
        simple, useful, and a little more fun.
        </p>
        <span class="status-pill">🟢 Ace is online</span>
        <span class="status-pill">🎤 Voice module standby</span>
        <span class="status-pill">🔗 Raspberry Pi pending</span>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Quick Access")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="white-card">
        <h4>About Ace</h4>
        <p>Learn what Ace is and what the project is about.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="white-card">
        <h4>Features</h4>
        <p>View current and future assistant capabilities.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="white-card">
        <h4>Ace Terminal</h4>
        <p>Monitor Ace’s activity and system status.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="white-card">
        <h4>Update History</h4>
        <p>Track progress, versions, and planned improvements.</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "About Ace":
    st.header("About Ace")

    st.markdown("""
    <div class="card">
    Ace The Assistant is a software and hardware project inspired by the idea of a friendly digital companion.
    It combines a custom web interface, Python logic, and future Raspberry Pi integration.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Purpose")
    st.write("""
    The purpose of Ace is to provide a simple assistant experience where users can view information,
    interact with the system, and monitor what Ace is doing through a clear interface.
    """)

    st.subheader("Tools Used")
    st.write("- Python")
    st.write("- Streamlit")
    st.write("- VS Code")
    st.write("- Git and GitHub")
    st.write("- Raspberry Pi integration later")

elif page == "Features":
    st.header("Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
        <h4>Current Features</h4>
        <ul>
            <li>Mobile-friendly web app prototype</li>
            <li>Clean blue and white interface</li>
            <li>Friendly Ace identity</li>
            <li>About section</li>
            <li>Feature overview</li>
            <li>Simulated live terminal</li>
            <li>Update history</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
        <h4>Future Features</h4>
        <ul>
            <li>Real Raspberry Pi connection</li>
            <li>Live assistant activity logs</li>
            <li>Voice interaction</li>
            <li>System status monitoring</li>
            <li>Command execution</li>
            <li>Custom animations and avatar</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

elif page == "Status Dashboard":
    st.header("Status Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
        <h4>🟢 Ace Status</h4>
        <p>Online</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
        <h4>🎤 Voice Module</h4>
        <p>Standby</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
        <h4>🔗 Raspberry Pi</h4>
        <p>Pending connection</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
        <h4>⚙️ Current Mode</h4>
        <p>Idle</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <h4>Version</h4>
    <p>Ace The Assistant v1.0</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "Ace Terminal":
    st.header("Ace Terminal")

    st.write("Live-style activity feed showing what Ace is doing. For now, this is simulated.")

    terminal_text = generate_terminal_logs()

    st.code(terminal_text, language="bash")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("Ace Online")

    with col2:
        st.info("Voice Standby")

    with col3:
        st.warning("Pi Pending")

    if st.button("🔄 Refresh Terminal"):
        st.rerun()

elif page == "Update History":
    st.header("Update History")

    st.markdown("""
    <div class="card">
    <h4>Version 1.0</h4>
    <ul>
        <li>Created first Streamlit prototype</li>
        <li>Added Ace identity and blue/white theme</li>
        <li>Added Home, About, Features, Terminal, Update History, and Settings pages</li>
        <li>Added simulated live terminal</li>
        <li>Improved project structure</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <h4>Next Updates</h4>
    <ul>
        <li>Add final project hex codes</li>
        <li>Add Ace logo or avatar</li>
        <li>Connect terminal to Raspberry Pi logs</li>
        <li>Add real assistant status data</li>
        <li>Improve animations and visual design</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

elif page == "Settings":
    st.header("Settings")

    st.markdown("""
    <div class="card">
    <h4>Assistant Settings</h4>
    <ul>
        <li>Assistant name: Ace</li>
        <li>Theme: Blue and white</li>
        <li>Voice module: Standby</li>
        <li>Raspberry Pi connection: Pending</li>
        <li>Current version: 1.0</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
Ace The Assistant · Streamlit Web App Prototype
</div>
""", unsafe_allow_html=True)