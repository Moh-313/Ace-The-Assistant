from backend.dashboard_manager import dashboard_manager
from backend.terminal_manager import terminal_manager


class Assistant:
    """
    Central controller for Ace The Assistant.

    This class coordinates Ace's state with the Dashboard Manager
    and Terminal Manager.

    Later, Raspberry Pi and voice-assistant code can call these
    methods instead of directly modifying the user interface.
    """

    VALID_STATES = {
        "Idle",
        "Listening",
        "Processing",
        "Speaking",
        "Sleeping",
        "Offline",
    }

    def __init__(self) -> None:
        """Initialize Ace with the default application state."""

        self._is_running = True

        dashboard_manager.set_assistant_status("Online")
        dashboard_manager.set_mode("Idle")
        dashboard_manager.set_voice_status("Standby")

    def start(self) -> None:
        """Start Ace and set the assistant to its default active state."""

        if self._is_running:
            terminal_manager.warning("Ace is already running")
            return

        self._is_running = True

        dashboard_manager.set_assistant_status("Online")
        dashboard_manager.set_mode("Idle")
        dashboard_manager.set_voice_status("Standby")

        terminal_manager.success("Ace started successfully")
        terminal_manager.status("Ace is ready")

    def stop(self) -> None:
        """Stop Ace and mark all assistant services as offline."""

        if not self._is_running:
            terminal_manager.warning("Ace is already stopped")
            return

        self._is_running = False

        dashboard_manager.set_assistant_status("Offline")
        dashboard_manager.set_mode("Offline")
        dashboard_manager.set_voice_status("Unavailable")

        terminal_manager.system("Ace stopped")
        terminal_manager.status("Assistant services are offline")

    def wake(self) -> None:
        """Wake Ace and return it to idle mode."""

        self._ensure_running()

        dashboard_manager.set_mode("Idle")
        dashboard_manager.set_voice_status("Standby")

        terminal_manager.success("Ace is awake")
        terminal_manager.status("Waiting for user interaction")

    def sleep(self) -> None:
        """Place Ace in sleeping mode."""

        self._ensure_running()

        dashboard_manager.set_mode("Sleeping")
        dashboard_manager.set_voice_status("Standby")

        terminal_manager.status("Ace entered sleeping mode")

    def start_listening(self) -> None:
        """Set Ace to listening mode."""

        self._ensure_running()

        dashboard_manager.set_mode("Listening")
        dashboard_manager.set_voice_status("Listening")

        terminal_manager.info("Voice input detected")
        terminal_manager.status("Ace is listening")

    def start_processing(self) -> None:
        """Set Ace to processing mode after receiving user input."""

        self._ensure_running()

        dashboard_manager.set_mode("Processing")
        dashboard_manager.set_voice_status("Processing")

        terminal_manager.info("Processing user request")

    def start_speaking(self) -> None:
        """Set Ace to speaking mode."""

        self._ensure_running()

        dashboard_manager.set_mode("Speaking")
        dashboard_manager.set_voice_status("Speaking")

        terminal_manager.success("Response generated")
        terminal_manager.status("Ace is speaking")

    def return_to_idle(self) -> None:
        """Return Ace to its default idle state."""

        self._ensure_running()

        dashboard_manager.set_mode("Idle")
        dashboard_manager.set_voice_status("Standby")

        terminal_manager.status("Ace returned to idle mode")

    def connect_raspberry_pi(self) -> None:
        """
        Mark the Raspberry Pi as connected.

        Later, this method can be called after a real connection
        is successfully established.
        """

        dashboard_manager.set_pi_connection("Connected")
        terminal_manager.success("Raspberry Pi connected")

    def disconnect_raspberry_pi(self) -> None:
        """Mark the Raspberry Pi as disconnected."""

        dashboard_manager.set_pi_connection("Disconnected")
        terminal_manager.warning("Raspberry Pi disconnected")

    def get_state(self) -> dict:
        """Return Ace's complete current dashboard state."""

        state = dashboard_manager.get_status()
        state["running"] = self._is_running

        return state

    def _ensure_running(self) -> None:
        """
        Confirm that Ace is running before changing its active mode.

        Raises:
            RuntimeError: If Ace is currently stopped.
        """

        if not self._is_running:
            terminal_manager.error(
                "Action unavailable because Ace is offline"
            )
            raise RuntimeError(
                "Ace must be started before performing this action."
            )


assistant = Assistant()