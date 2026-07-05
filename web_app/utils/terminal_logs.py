from datetime import datetime
import random

def generate_terminal_logs():
    current_time = datetime.now().strftime("%H:%M:%S")

    possible_logs = [
        "Ace is awake and ready ✨",
        "Assistant interface online",
        "User session started",
        "Voice module on standby",
        "System check completed",
        "Waiting for user input",
        "Connection check in progress",
        "Raspberry Pi connection pending",
        "Idle mode activated",
        "Assistant services loaded",
    ]

    selected_logs = random.sample(possible_logs, 6)

    terminal_text = "ACE LIVE TERMINAL\n"
    terminal_text += "--------------------------------------------\n\n"

    for log in selected_logs:
        if "pending" in log.lower():
            terminal_text += f"[{current_time}] WARNING  {log}\n"
        elif "ready" in log.lower() or "completed" in log.lower() or "online" in log.lower():
            terminal_text += f"[{current_time}] STATUS   {log}\n"
        else:
            terminal_text += f"[{current_time}] INFO     {log}\n"

    return terminal_text