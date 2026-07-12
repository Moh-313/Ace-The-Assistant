from dataclasses import asdict, dataclass


@dataclass
class DashboardState:
    """Stores the information displayed on Ace's dashboard."""

    assistant: str = "Online"
    mode: str = "Idle"
    voice: str = "Standby"
    raspberry_pi: str = "Disconnected"
    version: str = "1.0.0"


class DashboardManager:
    """Manages Ace's dashboard and system state."""

    VALID_MODES = {
        "Idle",
        "Listening",
        "Processing",
        "Speaking",
        "Sleeping",
        "Offline",
    }

    VALID_CONNECTIONS = {
        "Connected",
        "Disconnected",
        "Connecting",
    }

    VALID_VOICE_STATES = {
        "Standby",
        "Listening",
        "Processing",
        "Speaking",
        "Unavailable",
    }

    def __init__(self) -> None:
        """Create the default dashboard state."""

        self._state = DashboardState()

    def get_status(self) -> dict:
        """Return a copy of the current dashboard information."""

        return asdict(self._state)

    def set_assistant_status(self, status: str) -> None:
        """Update Ace's general assistant status."""

        normalized_status = status.strip()

        if not normalized_status:
            raise ValueError("Assistant status cannot be empty.")

        self._state.assistant = normalized_status

    def set_mode(self, mode: str) -> None:
        """Update Ace's current operating mode."""

        if mode not in self.VALID_MODES:
            valid_modes = ", ".join(sorted(self.VALID_MODES))
            raise ValueError(
                f"Invalid mode '{mode}'. Choose one of: {valid_modes}"
            )

        self._state.mode = mode

    def set_voice_status(self, voice_status: str) -> None:
        """Update the voice module state."""

        if voice_status not in self.VALID_VOICE_STATES:
            valid_states = ", ".join(
                sorted(self.VALID_VOICE_STATES)
            )

            raise ValueError(
                f"Invalid voice state '{voice_status}'. "
                f"Choose one of: {valid_states}"
            )

        self._state.voice = voice_status

    def set_pi_connection(self, connection_status: str) -> None:
        """Update the Raspberry Pi connection state."""

        if connection_status not in self.VALID_CONNECTIONS:
            valid_connections = ", ".join(
                sorted(self.VALID_CONNECTIONS)
            )

            raise ValueError(
                f"Invalid Pi status '{connection_status}'. "
                f"Choose one of: {valid_connections}"
            )

        self._state.raspberry_pi = connection_status

    def reset(self) -> None:
        """Restore all dashboard values to their defaults."""

        self._state = DashboardState()


dashboard_manager = DashboardManager()