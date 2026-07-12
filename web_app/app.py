import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
from utils.styles import load_css
from backend.assistant_state import assistant_state
from backend.pi_connection import update_connection_state
from backend.terminal_manager import terminal_manager
from backend.assistant import assistant



st.set_page_config(
    page_title="Ace The Assistant",
    page_icon="✨",
    layout="wide"
)

st.markdown(load_css(), unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=[
        "Home",
        "About",
        "Features",
        "Dashboard",
        "Terminal",
        "Updates",
        "Settings"
    ],
    icons=[
        "house",
        "info-circle",
        "stars",
        "speedometer2",
        "terminal",
        "clock-history",
        "gear"
    ],
    orientation="horizontal",
)

if selected == "Home":
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

elif selected == "About":
    st.header("About")

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

elif selected == "Features":
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

elif selected == "Dashboard":
    st.header("Dashboard")

    ace_dashboard = assistant.get_state()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="card">
                <h4>🟢 Assistant Status</h4>
                <p>{ace_dashboard["assistant"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="card">
                <h4>🎤 Voice Module</h4>
                <p>{ace_dashboard["voice"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="card">
                <h4>🔗 Raspberry Pi</h4>
                <p>{ace_dashboard["raspberry_pi"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="card">
                <h4>⚙️ Current Mode</h4>
                <p>{ace_dashboard["mode"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="card">
            <h4>Version</h4>
            <p>Ace The Assistant v{ace_dashboard["version"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    #### TEMPORARY TESTING ####
    st.subheader("Backend Testing Controls")

    control_col1, control_col2, control_col3 = st.columns(3)

    with control_col1:
        if st.button("Start Listening"):
            try:
                assistant.start_listening()
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))

        if st.button("Processing"):
            try:
                assistant.start_processing()
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))

    with control_col2:
        if st.button("Start Speaking"):
            try:
                assistant.start_speaking()
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))

        if st.button("Return to Idle"):
            try:
                assistant.return_to_idle()
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))

    with control_col3:
        if st.button("Sleep"):
            try:
                assistant.sleep()
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))

        if st.button("Wake"):
            try:
                assistant.wake()
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))
    ##################################
    #### TEMPORARY SYSTEM AND CONNECTION TESTING ####
    system_col1, system_col2, system_col3, system_col4 = st.columns(4)

    with system_col1:
        if st.button("Stop Ace"):
            assistant.stop()
            st.rerun()

    with system_col2:
        if st.button("Start Ace"):
            assistant.start()
            st.rerun()

    with system_col3:
        if st.button("Connect Pi"):
            assistant.connect_raspberry_pi()
            st.rerun()

    with system_col4:
        if st.button("Disconnect Pi"):
            assistant.disconnect_raspberry_pi()
            st.rerun()
    ############################################

elif selected == "Terminal":
    st.header("Ace Terminal")

    st.write(
        "This terminal displays Ace’s system activity. "
        "The logs are simulated for now and can later be replaced with Raspberry Pi output."
    )

    terminal_text = terminal_manager.get_formatted_logs()

    st.code(terminal_text, language="bash")

    st.caption(f"Stored logs: {terminal_manager.log_count()} / 50")

    ace_dashboard = assistant.get_state()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"Ace: {ace_dashboard['assistant']}")

    with col2:
        st.info(f"Voice: {ace_dashboard['voice']}")

    with col3:
        if ace_dashboard["raspberry_pi"] == "Connected":
            st.success("Pi Connected")
        else:
            st.warning("Pi Disconnected")

    button_col1, button_col2, button_col3 = st.columns(3)

    with button_col1:
        if st.button("Add Test Log"):
            terminal_manager.info("Test activity received from Ace")
            st.rerun()

    with button_col2:
        if st.button("Clear Terminal"):
            terminal_manager.clear_logs()
            st.rerun()

    with button_col3:
        if st.button("Reset Terminal"):
            terminal_manager.reset_logs()
            st.rerun()

elif  selected == "Updates":
    st.header("Updates")

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

elif selected == "Settings":
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