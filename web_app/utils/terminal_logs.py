from backend.pi_connection import get_pi_logs


def generate_terminal_logs() -> str:
    """Format Ace's logs for display in the terminal."""

    logs = get_pi_logs()

    terminal_text = "ACE LIVE TERMINAL\n"
    terminal_text += "--------------------------------------------\n\n"
    terminal_text += "\n".join(logs)

    return terminal_text