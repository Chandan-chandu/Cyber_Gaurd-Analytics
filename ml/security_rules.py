from datetime import datetime, timedelta


FAILED_LOGIN_THRESHOLD = 5

TIME_WINDOW_MINUTES = 2


def check_failed_login_rule(events):
    """
    Detect repeated failed authentication attempts
    for the same user within a short time window.
    """

    if not events:
        return {
            "rule_triggered": False,
            "severity": "LOW",
            "reason": None,
        }

    events = sorted(
        events,
        key=lambda event: event["timestamp"]
    )

    for i in range(len(events)):

        window_start = events[i]["timestamp"]

        window_end = (
            window_start
            + timedelta(minutes=TIME_WINDOW_MINUTES)
        )

        failed_events = [
            event
            for event in events
            if (
                event["result"] == "FAILED"
                and window_start
                <= event["timestamp"]
                <= window_end
            )
        ]

        if len(failed_events) >= FAILED_LOGIN_THRESHOLD:

            return {
                "rule_triggered": True,
                "severity": "HIGH",
                "reason": (
                    f"{len(failed_events)} failed "
                    "authentication attempts detected "
                    "within 2 minutes."
                ),
            }

    return {
        "rule_triggered": False,
        "severity": "LOW",
        "reason": None,
    }


if __name__ == "__main__":

    print("\n========== RULE-BASED SECURITY DETECTOR ==========\n")

    base_time = datetime.now()

    test_events = []

    for i in range(5):

        test_events.append(
            {
                "timestamp": (
                    base_time
                    + timedelta(seconds=i * 15)
                ),
                "result": "FAILED",
            }
        )

    result = check_failed_login_rule(test_events)

    print("Test events:", len(test_events))

    print("\nRule triggered:", result["rule_triggered"])
    print("Severity:", result["severity"])
    print("Reason:", result["reason"])