import time

from live_alert_detector import detect_live_alerts, engine


print("\n" + "=" * 70)
print("CYBERGUARD LIVE ALERT DETECTOR STARTED")
print("=" * 70)
print("Checking live authentication events continuously...")
print("Detection interval: 5 seconds")
print("Press CTRL+C to stop")
print("=" * 70 + "\n")


try:

    while True:

        try:
            detect_live_alerts()

        except Exception as error:

            print(
                f"\nAlert detection error: {error}"
            )

            print(
                "Retrying in 5 seconds...\n"
            )

        time.sleep(5)


except KeyboardInterrupt:

    print("\n")
    print("=" * 70)
    print("CYBERGUARD LIVE ALERT DETECTOR STOPPED")
    print("=" * 70)


finally:

    engine.dispose()