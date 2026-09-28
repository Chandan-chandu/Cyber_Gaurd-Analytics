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
              {events.map((event) => (
                <tr key={`${event.event_id}-${event.received_at}`}>
                  <td>{event.event_id}</td>
                  <td>{event.event_type}</td>
                  <td>{event.user_id}</td>
                  <td>{event.asset_id}</td>

                  <td>
                    <span
                      className={`severity-badge ${String(
                        event.severity
                      ).toLowerCase()}`}
                    >
                      {event.severity}
                    </span>
                  </td>

                  <td>
                    {new Date(
                      event.event_timestamp
                    ).toLocaleTimeString()}
                  </td>

                  <td>
                    {new Date(
                      event.received_at
                    ).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default LiveEvents;