import { useEffect, useState } from "react";

function LiveEvents() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchLiveEvents = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8001/live-events?limit=20"
      );

      if (!response.ok) {
        throw new Error("Failed to fetch live events");
      }

      const data = await response.json();

      setEvents(data);
      setError("");
    } catch (err) {
      setError("Unable to load live security events");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveEvents();

    const interval = setInterval(() => {
      fetchLiveEvents();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getEventTypeClass = (eventType) => {
    return String(eventType || "")
      .toLowerCase()
      .replace(/_/g, "-");
  };

  const getEventTypeLabel = (eventType) => {
    switch (eventType) {
      case "authentication_success":
        return "AUTHENTICATION SUCCESS";

      case "authentication_failed":
        return "AUTHENTICATION FAILED";

      case "network_activity":
        return "NETWORK ACTIVITY";

      case "endpoint_alert":
        return "ENDPOINT ALERT";

      default:
        return String(eventType || "UNKNOWN EVENT").replace(/_/g, " ");
    }
  };

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case "authentication_success":
        return "✓";

      case "authentication_failed":
        return "✕";

      case "network_activity":
        return "↔";

      case "endpoint_alert":
        return "!";

      default:
        return "•";
    }
  };

  return (
    <section className="live-events-section">
      <div className="section-header">
        <div>
          <h2>Live Security Events</h2>
          <p>Real-time events received from Kafka</p>
        </div>

        <div className="live-indicator">
          <span className="live-dot"></span>
          LIVE
        </div>
      </div>

      {loading && (
        <p className="status-message">
          Loading live events...
        </p>
      )}

      {error && (
        <p className="status-message error">
          {error}
        </p>
      )}

      {!loading && !error && (
        <div className="live-events-table-wrapper">
          <table className="live-events-table">
            <thead>
              <tr>
                <th>Event ID</th>
                <th>Event Type</th>
                <th>User ID</th>
                <th>Asset ID</th>
                <th>Severity</th>
                <th>Event Time</th>
                <th>Received</th>
              </tr>
            </thead>

            <tbody>
              {events.map((event) => {
                const eventTypeClass = getEventTypeClass(
                  event.event_type
                );

                return (
                  <tr
                    key={`${event.event_id}-${event.received_at}`}
                  >
                    <td className="event-id-cell">
                      {event.event_id}
                    </td>

                    <td>
                      <div
                        className={`event-type-badge ${eventTypeClass}`}
                      >
                        <span className="event-type-icon">
                          {getEventIcon(event.event_type)}
                        </span>

                        <span>
                          {getEventTypeLabel(event.event_type)}
                        </span>
                      </div>
                    </td>

                    <td className="user-id-cell">
                      {event.user_id}
                    </td>

                    <td className="asset-id-cell">
                      {event.asset_id}
                    </td>

                    <td>
                      <span
                        className={`severity-badge ${String(
                          event.severity || ""
                        ).toLowerCase()}`}
                      >
                        {event.severity}
                      </span>
                    </td>

                    <td className="event-time-cell">
                      {new Date(
                        event.event_timestamp
                      ).toLocaleTimeString()}
                    </td>

                    <td className="event-time-cell">
                      {new Date(
                        event.received_at
                      ).toLocaleTimeString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default LiveEvents;