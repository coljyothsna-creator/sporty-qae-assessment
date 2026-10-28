"""Receipt timestamps compared against browser-local wall time, not runner time."""

import re
from datetime import datetime, time, timedelta

from selenium.webdriver.remote.webdriver import WebDriver


def browser_local_time(driver: WebDriver) -> datetime:
    parts = driver.execute_script(
        "const now = new Date();"
        "return [now.getFullYear(), now.getMonth() + 1, now.getDate(),"
        "now.getHours(), now.getMinutes(), now.getSeconds(),"
        "now.getMilliseconds() * 1000];"
    )
    return datetime(*parts)


def receipt_timestamp_error(
    text: str, submitted_at: datetime, received_at: datetime
) -> str | None:
    """Return a diagnostic for invalid timestamps, or None when plausible.

    Today does not encode a date. Use only dates intersecting the browser window,
    including both sides of midnight, rather than assuming the runner's date.
    """
    if submitted_at.tzinfo is not None or received_at.tzinfo is not None:
        return "Timestamp validation requires browser-local wall times without offsets"
    if received_at < submitted_at:
        return (
            "Browser clock moved backwards during placement; cannot validate timestamp"
        )
    match = re.fullmatch(
        r"Today,\s*([01]\d|2[0-3]):([0-5]\d)", text.strip(), flags=re.IGNORECASE
    )
    if match is None:
        return f"Timestamp {text!r} is missing or invalid; expected 'Today, HH:MM'"

    displayed_time = time(int(match[1]), int(match[2]))
    start = submitted_at.replace(second=0, microsecond=0)
    end = received_at.replace(second=0, microsecond=0)
    candidate = datetime.combine(start.date(), displayed_time)
    if candidate < start:
        candidate += timedelta(days=1)
    if candidate <= end:
        return None
    return (
        f"Timestamp {text!r} is outside browser-local submission window "
        f"{submitted_at.isoformat()} through {received_at.isoformat()} "
        "(compared at minute precision)"
    )
