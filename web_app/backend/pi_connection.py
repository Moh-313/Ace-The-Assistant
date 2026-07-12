from datetime import datetime
from backend.assistant_state import assistant_state


def check_pi_connection() -> bool:
    """
    Check whether the Raspberry Pi is connected.

    This is a temporary placeholder.
    Your teammate can replace this logic with the real connection later.
    """
    return False


def update_connection_state() -> None:
    """Update Ace's stored Raspberry Pi connection status."""

    if check_pi_connection():
        assistant_state.pi_connection = "Connected"
    else:
        assistant_state.pi_connection = "Disconnected"


def get_pi_logs() -> list[str]:
    """
    Return logs received from the Raspberry Pi.

    For now, this returns simulated logs.
    Later, your teammate can replace this with real Raspberry Pi output.
    """

    current_time = datetime.now().strftime("%H:%M:%S")

    if check_pi_connection():
        return [
            f"[{current_time}] SUCCESS  Raspberry Pi connected",
            f"[{current_time}] INFO     Voice assistant service online",
            f"[{current_time}] STATUS   Ace is ready",
        ]

    return [
        f"[{current_time}] SYSTEM   Ace web interface started",
        f"[{current_time}] INFO     Assistant mode: {assistant_state.mode}",
        f"[{current_time}] INFO     Voice module: {assistant_state.voice_status}",
        f"[{current_time}] WARNING  Raspberry Pi is not connected",
        f"[{current_time}] STATUS   Waiting for Raspberry Pi data...",
    ]