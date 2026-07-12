from datetime import datetime
from typing import Final


class TerminalManager:
    """Stores, formats, and manages Ace terminal logs."""

    VALID_LEVELS: Final[set[str]] = {
        "INFO",
        "STATUS",
        "SUCCESS",
        "WARNING",
        "ERROR",
        "SYSTEM",
    }

    def __init__(self, max_logs: int = 50) -> None:
        if max_logs <= 0:
            raise ValueError("max_logs must be greater than zero.")

        self.max_logs = max_logs
        self._logs: list[dict[str, str]] = []

        self.reset_logs()

    def add_log(self, level: str, message: str) -> None:
        """Add a validated log entry."""

        normalized_level = level.upper().strip()
        normalized_message = message.strip()

        if normalized_level not in self.VALID_LEVELS:
            valid_levels = ", ".join(sorted(self.VALID_LEVELS))
            raise ValueError(
                f"Invalid log level '{level}'. Choose one of: {valid_levels}"
            )

        if not normalized_message:
            raise ValueError("Log message cannot be empty.")

        self._logs.append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": normalized_level,
                "message": normalized_message,
            }
        )

        self._enforce_log_limit()

    def info(self, message: str) -> None:
        """Add an informational log."""
        self.add_log("INFO", message)

    def status(self, message: str) -> None:
        """Add a status log."""
        self.add_log("STATUS", message)

    def success(self, message: str) -> None:
        """Add a success log."""
        self.add_log("SUCCESS", message)

    def warning(self, message: str) -> None:
        """Add a warning log."""
        self.add_log("WARNING", message)

    def error(self, message: str) -> None:
        """Add an error log."""
        self.add_log("ERROR", message)

    def system(self, message: str) -> None:
        """Add a system log."""
        self.add_log("SYSTEM", message)

    def get_logs(self, level: str | None = None) -> list[dict[str, str]]:
        """
        Return stored logs.

        If a level is provided, only logs from that level are returned.
        """

        if level is None:
            return self._logs.copy()

        normalized_level = level.upper().strip()

        if normalized_level not in self.VALID_LEVELS:
            valid_levels = ", ".join(sorted(self.VALID_LEVELS))
            raise ValueError(
                f"Invalid log level '{level}'. Choose one of: {valid_levels}"
            )

        return [
            log.copy()
            for log in self._logs
            if log["level"] == normalized_level
        ]

    def get_formatted_logs(self, level: str | None = None) -> str:
        """Return formatted logs for display in Streamlit."""

        logs = self.get_logs(level)

        terminal_text = "ACE LIVE TERMINAL\n"
        terminal_text += "--------------------------------------------\n\n"

        if not logs:
            terminal_text += "No logs available.\n"
            return terminal_text

        for log in logs:
            terminal_text += (
                f"[{log['time']}] "
                f"{log['level']:<8} "
                f"{log['message']}\n"
            )

        return terminal_text

    def clear_logs(self) -> None:
        """Remove all terminal logs."""
        self._logs.clear()

    def reset_logs(self) -> None:
        """Restore the default startup logs."""

        self.clear_logs()
        self.system("Ace web interface started")
        self.info("Assistant services loaded")
        self.status("Waiting for Raspberry Pi data")

    def log_count(self) -> int:
        """Return the current number of stored logs."""
        return len(self._logs)

    def _enforce_log_limit(self) -> None:
        """Keep only the newest logs when the limit is exceeded."""

        if len(self._logs) > self.max_logs:
            excess_logs = len(self._logs) - self.max_logs
            del self._logs[:excess_logs]


terminal_manager = TerminalManager(max_logs=50)