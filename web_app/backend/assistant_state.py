from dataclasses import dataclass, asdict


@dataclass
class AssistantState:
    """Stores Ace's current system state."""

    status: str = "Online"
    mode: str = "Idle"
    voice_status: str = "Standby"
    pi_connection: str = "Disconnected"
    version: str = "1.0.0"

    def to_dict(self) -> dict:
        """Return the state as a dictionary."""
        return asdict(self)


# Temporary state used until real data comes from the Raspberry Pi
assistant_state = AssistantState()