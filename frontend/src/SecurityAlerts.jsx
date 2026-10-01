import { useEffect, useMemo, useState } from "react";

function SecurityAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeFilter, setActiveFilter] = useState("ALL");

  // Currently opened alert
  const [selectedAlert, setSelectedAlert] = useState(null);

  // --------------------------------------------------
  // FETCH SECURITY ALERTS
  // --------------------------------------------------

  const fetchSecurityAlerts = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8001/security-alerts?limit=20"
      );

      if (!response.ok) {
        throw new Error("Failed to fetch security alerts");
      }

      const data = await response.json();

      setAlerts(data);
      setError("");

      // Keep the opened alert updated when new API data arrives
      setSelectedAlert((currentSelected) => {
        if (!currentSelected) {
          return null;
        }

        const updatedAlert = data.find(
          (alert) => alert.alert_id === currentSelected.alert_id
        );

        return updatedAlert || currentSelected;
      });
    } catch (err) {
      setError("Unable to load security alerts");
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // AUTO REFRESH
  // --------------------------------------------------

  useEffect(() => {
    fetchSecurityAlerts();

    const interval = setInterval(() => {
      fetchSecurityAlerts();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // --------------------------------------------------
  // SEVERITY CLASS
  // --------------------------------------------------

  const getSeverityClass = (severity) => {
    return String(severity || "").toLowerCase();
  };

  // --------------------------------------------------
  // FILTER ALERTS
  // --------------------------------------------------

  const filteredAlerts = useMemo(() => {
    if (activeFilter === "ALL") {
      return alerts;
    }

    return alerts.filter(
      (alert) =>
        String(alert.severity || "").toUpperCase() === activeFilter
    );
  }, [alerts, activeFilter]);

  // --------------------------------------------------
  // ALERT COUNTS
  // --------------------------------------------------

  const alertCounts = useMemo(() => {
    return {
      ALL: alerts.length,

      CRITICAL: alerts.filter(
        (alert) =>
          String(alert.severity || "").toUpperCase() === "CRITICAL"
      ).length,

      HIGH: alerts.filter(
        (alert) =>
          String(alert.severity || "").toUpperCase() === "HIGH"
      ).length,

      MEDIUM: alerts.filter(
        (alert) =>
          String(alert.severity || "").toUpperCase() === "MEDIUM"
      ).length,

      LOW: alerts.filter(
        (alert) =>
          String(alert.severity || "").toUpperCase() === "LOW"
      ).length,
    };
  }, [alerts]);

  // --------------------------------------------------
  // OPEN / CLOSE INVESTIGATION
  // --------------------------------------------------

  const handleOpenInvestigation = (alert) => {
    if (
      selectedAlert &&
      selectedAlert.alert_id === alert.alert_id
    ) {
      setSelectedAlert(null);
      return;
    }

    setSelectedAlert(alert);
  };

  const handleCloseInvestigation = () => {
    setSelectedAlert(null);
  };

  // --------------------------------------------------
  // FORMAT ML SCORE
  // --------------------------------------------------

  const formatMLScore = (score) => {
    if (
      score === null ||
      score === undefined ||
      score === ""
    ) {
      return "N/A";
    }

    const numericScore = Number(score);

    if (!Number.isFinite(numericScore)) {
      return "N/A";
    }

    return numericScore.toFixed(4);
  };

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <section className="security-alerts-section">

      {/* ==================================================
          SECTION HEADER
          ================================================== */}

      <div className="section-header">

        <div>

          <h2>
            Security Alerts
          </h2>

          <p>
            ML and rule-based security alerts
          </p>

        </div>

        <div className="alert-status">

          <span className="alert-status-dot"></span>

          MONITORING

        </div>

      </div>


      {/* ==================================================
          ALERT FILTERS
          ================================================== */}

      {!loading &&
        !error &&
        alerts.length > 0 && (

          <div className="alert-filters">

            {/* ALL */}

            <button
              type="button"
              className={`alert-filter-btn ${
                activeFilter === "ALL"
                  ? "active"
                  : ""
              }`}
              onClick={() => setActiveFilter("ALL")}
            >

              <span>
                ALL
              </span>

              <strong>
                {alertCounts.ALL}
              </strong>

            </button>


            {/* CRITICAL */}

            <button
              type="button"
              className={`alert-filter-btn critical ${
                activeFilter === "CRITICAL"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActiveFilter("CRITICAL")
              }
            >

              <span>
                CRITICAL
              </span>

              <strong>
                {alertCounts.CRITICAL}
              </strong>

            </button>


            {/* HIGH */}

            <button
              type="button"
              className={`alert-filter-btn high ${
                activeFilter === "HIGH"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActiveFilter("HIGH")
              }
            >

              <span>
                HIGH
              </span>

              <strong>
                {alertCounts.HIGH}
              </strong>

            </button>


            {/* MEDIUM */}

            <button
              type="button"
              className={`alert-filter-btn medium ${
                activeFilter === "MEDIUM"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActiveFilter("MEDIUM")
              }
            >

              <span>
                MEDIUM
              </span>

              <strong>
                {alertCounts.MEDIUM}
              </strong>

            </button>


            {/* LOW */}

            <button
              type="button"
              className={`alert-filter-btn low ${
                activeFilter === "LOW"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActiveFilter("LOW")
              }
            >

              <span>
                LOW
              </span>

              <strong>
                {alertCounts.LOW}
              </strong>

            </button>

          </div>

        )}


      {/* ==================================================
          LOADING
          ================================================== */}

      {loading && (

        <p className="status-message">
          Loading security alerts...
        </p>

      )}


      {/* ==================================================
          ERROR
          ================================================== */}

      {error && (

        <p className="status-message error">
          {error}
        </p>

      )}


      {/* ==================================================
          NO ALERTS
          ================================================== */}

      {!loading &&
        !error &&
        alerts.length === 0 && (

          <p className="status-message">
            No security alerts detected.
          </p>

        )}


      {/* ==================================================
          NO ALERTS FOR SELECTED FILTER
          ================================================== */}

      {!loading &&
        !error &&
        alerts.length > 0 &&
        filteredAlerts.length === 0 && (

          <p className="status-message">

            No {activeFilter.toLowerCase()} security alerts
            detected.

          </p>

        )}


      {/* ==================================================
          SECURITY ALERT LIST
          ================================================== */}

      {!loading &&
        !error &&
        filteredAlerts.length > 0 && (

          <div className="security-alerts-list">

            {filteredAlerts.map((alert) => {

              const isSelected =
                selectedAlert &&
                selectedAlert.alert_id === alert.alert_id;

              return (

                <div
                  key={alert.alert_id}
                  className="security-alert-wrapper"
                >

                  {/* ==================================================
                      MAIN SECURITY ALERT CARD
                      ================================================== */}

                  <div
                    className={`security-alert-card ${getSeverityClass(
                      alert.severity
                    )}`}
                  >

                    {/* ALERT TOP */}

                    <div className="security-alert-top">

                      <div>

                        <span
                          className={`alert-severity ${getSeverityClass(
                            alert.severity
                          )}`}
                        >
                          {alert.severity}
                        </span>

                        <h3>
                          Authentication Anomaly
                        </h3>

                      </div>


                      {/* OPEN / CLOSE */}

                      <button
                        type="button"
                        className={`alert-status-badge ${
                          isSelected
                            ? "investigation-open"
                            : ""
                        }`}
                        onClick={() =>
                          handleOpenInvestigation(alert)
                        }
                      >

                        {isSelected
                          ? "CLOSE"
                          : alert.status}

                      </button>

                    </div>


                    {/* ALERT DETAILS */}

                    <div className="security-alert-details">

                      <div>

                        <span>
                          User
                        </span>

                        <strong>
                          {alert.user_id}
                        </strong>

                      </div>


                      <div>

                        <span>
                          Asset
                        </span>

                        <strong>
                          {alert.asset_id}
                        </strong>

                      </div>


                      <div>

                        <span>
                          ML Anomaly
                        </span>

                        <strong>
                          {alert.ml_anomaly
                            ? "YES"
                            : "NO"}
                        </strong>

                      </div>


                      <div>

                        <span>
                          Rule Triggered
                        </span>

                        <strong>
                          {alert.rule_triggered
                            ? "YES"
                            : "NO"}
                        </strong>

                      </div>

                    </div>


                    {/* REASON */}

                    <div className="security-alert-reason">

                      <span>
                        Reason
                      </span>

                      <p>
                        {alert.reason}
                      </p>

                    </div>


                    {/* FOOTER */}

                    <div className="security-alert-footer">

                      <span>
                        Alert #{alert.alert_id}
                      </span>

                      <span>
                        {new Date(
                          alert.created_at
                        ).toLocaleString()}
                      </span>

                    </div>

                  </div>


                  {/* ==================================================
                      SMALL VERTICAL INVESTIGATION STRIP
                      ================================================== */}

                  {isSelected && (

                    <div className="compact-investigation-strip">

                      {/* TOP ROW */}

                      <div className="compact-investigation-header">

                        <div className="compact-investigation-title">

                          <span className="investigation-icon">
                            🛡
                          </span>

                          <div>

                            <span>
                              QUICK INVESTIGATION
                            </span>

                            <strong>
                              Alert #{alert.alert_id}
                            </strong>

                          </div>

                        </div>


                        <button
                          type="button"
                          className="compact-investigation-close"
                          onClick={
                            handleCloseInvestigation
                          }
                        >
                          ✕
                        </button>

                      </div>


                      {/* ==================================================
                          ICON INFORMATION ROW
                          ================================================== */}

                      <div className="compact-investigation-content">

                        {/* ML */}

                        <div className="compact-info-card">

                          <div className="compact-info-icon ml">
                            🧠
                          </div>

                          <div>

                            <span>
                              ML DETECTION
                            </span>

                            <strong
                              className={
                                alert.ml_anomaly
                                  ? "detected"
                                  : "not-detected"
                              }
                            >
                              {alert.ml_anomaly
                                ? "DETECTED"
                                : "NOT DETECTED"}
                            </strong>

                          </div>

                        </div>


                        {/* RULE */}

                        <div className="compact-info-card">

                          <div className="compact-info-icon rule">
                            ⚡
                          </div>

                          <div>

                            <span>
                              RULE DETECTION
                            </span>

                            <strong
                              className={
                                alert.rule_triggered
                                  ? "triggered"
                                  : "not-triggered"
                              }
                            >
                              {alert.rule_triggered
                                ? "TRIGGERED"
                                : "NOT TRIGGERED"}
                            </strong>

                          </div>

                        </div>


                        {/* MODEL SCORE */}

                        <div className="compact-info-card">

                          <div className="compact-info-icon score">
                            🎯
                          </div>

                          <div>

                            <span>
                              ML MODEL SCORE
                            </span>

                            <strong>
                              {formatMLScore(
                                alert.ml_anomaly_score
                              )}
                            </strong>

                          </div>

                        </div>

                      </div>


                      {/* ==================================================
                          BOTTOM INFORMATION ROW
                          ================================================== */}

                      <div className="compact-investigation-bottom">

                        {/* REASON */}

                        <div className="compact-bottom-reason">

                          <span className="compact-bottom-icon">
                            🔍
                          </span>

                          <div>

                            <span>
                              DETECTION REASON
                            </span>

                            <p>
                              {alert.reason}
                            </p>

                          </div>

                        </div>


                        {/* EVENT ID */}

                        <div className="compact-event">

                          <span className="compact-bottom-icon">
                            🔗
                          </span>

                          <div>

                            <span>
                              EVENT ID
                            </span>

                            <strong>
                              {alert.event_id || "N/A"}
                            </strong>

                          </div>

                        </div>


                        {/* TIME */}

                        <div className="compact-time">

                          <span className="compact-bottom-icon">
                            🕒
                          </span>

                          <div>

                            <span>
                              TIME
                            </span>

                            <strong>
                              {new Date(
                                alert.created_at
                              ).toLocaleTimeString()}
                            </strong>

                          </div>

                        </div>

                      </div>

                    </div>

                  )}

                </div>

              );

            })}

          </div>

        )}

    </section>
  );
}

export default SecurityAlerts;