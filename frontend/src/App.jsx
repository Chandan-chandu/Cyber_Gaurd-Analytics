import React, { useEffect, useMemo, useState } from "react";
import LiveEvents from "./LiveEvents";
import SecurityAlerts from "./SecurityAlerts";
import "./App.css";
import Sidebar from "./Sidebar";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";


const API_BASE_URL = "http://127.0.0.1:8001";


// =========================================================
// CUSTOM TOOLTIP
// =========================================================

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  return (
    <div className="custom-tooltip">

      <div className="tooltip-date">
        {label}
      </div>

      {payload.map((item, index) => (
        <div
          className="tooltip-row"
          key={index}
        >

          <span
            className="tooltip-label"
            style={{
              color: item.color || "#2563eb"
            }}
          >
            {item.name}
          </span>

          <strong className="tooltip-value">
            {typeof item.value === "number"
              ? item.value.toLocaleString()
              : item.value}
          </strong>

        </div>
      ))}

    </div>
  );
}


// =========================================================
// KPI CARD
// =========================================================

function KpiCard({
  icon,
  title,
  value,
  subtitle
}) {
  return (
    <div className="kpi-card">

      <div className="kpi-icon">
        {icon}
      </div>

      <div className="kpi-title">
        {title}
      </div>

      <div className="kpi-value">
        {value}
      </div>

      <div className="kpi-subtitle">
        {subtitle}
      </div>

    </div>
  );
}


// =========================================================
// SECTION HEADER
// =========================================================

function SectionHeader({
  title,
  subtitle,
  badge
}) {
  return (
    <>
      <div className="section-header">

        <h2>
          {title}
        </h2>

        <p>
          {subtitle}
        </p>

      </div>

      {badge && (
        <div className="section-badge">
          {badge}
        </div>
      )}
    </>
  );
}


// =========================================================
// MAIN APP
// =========================================================

function App() {

  const [kpis, setKpis] = useState(null);

  const [authenticationData, setAuthenticationData] =
    useState([]);

  const [incidentData, setIncidentData] =
    useState([]);

  const [assetData, setAssetData] =
    useState([]);

  const [suspiciousData, setSuspiciousData] =
    useState([]);

  const [apiOnline, setApiOnline] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const [errorMessage, setErrorMessage] =
    useState("");

  const [lastUpdated, setLastUpdated] =
    useState(null);


  // =======================================================
  // API FETCH FUNCTION
  // =======================================================

  async function fetchApi(endpoint) {

    const response =
      await fetch(
        `${API_BASE_URL}${endpoint}`
      );

    if (!response.ok) {

      throw new Error(
        `${endpoint} returned HTTP ${response.status}`
      );

    }

    return response.json();
  }


  // =======================================================
  // LOAD DASHBOARD
  // =======================================================

  async function loadDashboard() {

    try {

      setLoading(true);

      setErrorMessage("");


      const [
        health,
        kpiResponse,
        authenticationResponse,
        incidentResponse,
        assetResponse,
        suspiciousResponse
      ] = await Promise.all([

        fetchApi("/health"),

        fetchApi("/kpis"),

        fetchApi(
          "/authentication-trends"
        ),

        fetchApi(
          "/incident-analysis"
        ),

        fetchApi(
          "/asset-security-analysis"
        ),

        fetchApi(
          "/suspicious-event-analysis"
        )

      ]);


      // API STATUS

      if (
        health?.status === "healthy"
      ) {

        setApiOnline(true);

      } else {

        setApiOnline(false);

      }


      // KPI DATA

      setKpis(kpiResponse);


      // AUTHENTICATION DATA

      setAuthenticationData(
        Array.isArray(
          authenticationResponse
        )
          ? authenticationResponse
          : []
      );


      // INCIDENT DATA

      setIncidentData(
        Array.isArray(
          incidentResponse
        )
          ? incidentResponse
          : []
      );


      // ASSET DATA

      setAssetData(
        Array.isArray(
          assetResponse
        )
          ? assetResponse
          : []
      );


      // SUSPICIOUS EVENTS

      setSuspiciousData(
        Array.isArray(
          suspiciousResponse
        )
          ? suspiciousResponse
          : []
      );


      setLastUpdated(
        new Date()
      );

    }

    catch (error) {

      console.error(
        "Dashboard loading error:",
        error
      );

      setApiOnline(false);

      setErrorMessage(
        "Unable to connect to CyberGuard API. Make sure FastAPI is running on port 8001."
      );

    }

    finally {

      setLoading(false);

    }

  }


  // =======================================================
  // INITIAL LOAD
  // =======================================================

  useEffect(() => {

    loadDashboard();

  }, []);


  // =======================================================
  // INCIDENT TREND DATA
  // =======================================================

  const incidentTrendData =
    useMemo(() => {

      const grouped = {};


      incidentData.forEach(
        (item) => {

          const date =
            item.date_day;


          if (!grouped[date]) {

            grouped[date] = {

              date_day: date,

              incident_count: 0,

              closed_incident_count: 0

            };

          }


          grouped[date].incident_count +=
            Number(
              item.incident_count || 0
            );


          grouped[date]
            .closed_incident_count +=
            Number(
              item.closed_incident_count || 0
            );

        }
      );


      return Object.values(
        grouped
      ).sort(
        (a, b) =>
          a.date_day.localeCompare(
            b.date_day
          )
      );

    }, [incidentData]);


  // =======================================================
  // INCIDENT SEVERITY DATA
  // =======================================================

  const incidentSeverityData =
    useMemo(() => {

      const grouped = {};


      incidentData.forEach(
        (item) => {

          const severity =
            item.severity ||
            "UNKNOWN";


          if (!grouped[severity]) {

            grouped[severity] = {

              severity,

              incident_count: 0

            };

          }


          grouped[severity]
            .incident_count +=
            Number(
              item.incident_count || 0
            );

        }
      );


      const severityOrder = [

        "CRITICAL",

        "HIGH",

        "MEDIUM",

        "LOW"

      ];


      return Object.values(
        grouped
      ).sort(
        (a, b) =>
          severityOrder.indexOf(
            a.severity
          ) -
          severityOrder.indexOf(
            b.severity
          )
      );

    }, [incidentData]);


  // =======================================================
  // TOP ASSETS
  // =======================================================

  const topAssets =
    useMemo(() => {

      return [...assetData]

        .sort(
          (a, b) =>
            Number(
              b.activity_risk_indicator || 0
            ) -
            Number(
              a.activity_risk_indicator || 0
            )
        )

        .slice(0, 10)

        .map(
          (item) => ({

            ...item,

            asset_label:
              `Asset ${item.asset_id}`,

            activity_risk_indicator:
              Number(
                item.activity_risk_indicator || 0
              )

          })
        );

    }, [assetData]);


  // =======================================================
  // SUSPICIOUS EVENTS BY PROCESS
  // =======================================================

  const suspiciousByProcess =
    useMemo(() => {

      const grouped = {};


      suspiciousData.forEach(
        (item) => {

          const process =
            item.process ||
            "Unknown";


          if (!grouped[process]) {

            grouped[process] = {

              process,

              suspicious_event_count: 0

            };

          }


          grouped[process]
            .suspicious_event_count +=
            Number(
              item.suspicious_event_count || 0
            );

        }
      );


      return Object.values(
        grouped
      )

        .sort(
          (a, b) =>
            b.suspicious_event_count -
            a.suspicious_event_count
        )

        .slice(0, 10);

    }, [suspiciousData]);


  // =======================================================
  // FORMAT NUMBER
  // =======================================================

  function formatNumber(value) {

    if (
      value === null ||
      value === undefined
    ) {

      return "--";

    }

    return Number(
      value
    ).toLocaleString();

  }


  // =======================================================
  // FORMAT PERCENTAGE
  // =======================================================

  function formatPercentage(value) {

    if (
      value === null ||
      value === undefined
    ) {

      return "--";

    }

    return `${Number(
      value
    ).toFixed(2)}%`;

  }


  // =======================================================
  // FORMAT TIME
  // =======================================================

  function formatTime(date) {

    if (!date) {

      return "--";

    }

    return date.toLocaleTimeString(
      [],
      {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      }
    );

  }


  // =======================================================
  // UI
  // =======================================================

  return (

    <div className="cyber-dashboard">

      <Sidebar />

      <main className="cyber-main">

        <div className="app">


      {/* =================================================
          HEADER
      ================================================= */}

      <header className="header">

        <div className="shield">
          🛡️
        </div>


        <h1>
          CYBERGUARD ANALYTICS
        </h1>


        <p className="header-subtitle">
          Security Operations & Threat Monitoring Platform
        </p>


        <div className="header-actions">

          <div
            className={`api-status ${
              apiOnline
                ? "online"
                : "offline"
            }`}
          >

            <span className="status-dot"></span>

            {apiOnline
              ? "API ONLINE"
              : "API OFFLINE"}

          </div>


          <button
            className="refresh-button"
            onClick={
              loadDashboard
            }
          >

            ↻ Refresh

          </button>

        </div>

      </header>


      {/* =================================================
          ERROR
      ================================================= */}

      {errorMessage && (

        <div className="error-message">

          ⚠️ {errorMessage}

        </div>

      )}


      {/* =================================================
          SYSTEM INFORMATION
      ================================================= */}

      <div className="system-info">


        <div className="info-card">

          <span>
            DATA SOURCE
          </span>

          <strong>
            PostgreSQL Analytics Warehouse
          </strong>

        </div>


        <div className="info-card">

          <span>
            TRANSFORMATION
          </span>

          <strong>
            dbt Gold Layer
          </strong>

        </div>


        <div className="info-card">

          <span>
            BACKEND
          </span>

          <strong>
            FastAPI
          </strong>

        </div>


        <div className="info-card">

          <span>
            LAST UPDATED
          </span>

          <strong>
            {formatTime(
              lastUpdated
            )}
          </strong>

        </div>


      </div>


      {/* =================================================
          SECURITY OVERVIEW
      ================================================= */}

      <SectionHeader
        title="Security Overview"
        subtitle="Current cybersecurity activity across the environment"
      />


      <div className="kpi-grid">


        <KpiCard
          icon="🔐"
          title="Total Login Attempts"
          value={
            formatNumber(
              kpis?.total_login_attempts
            )
          }
          subtitle="Authentication activity"
        />


        <KpiCard
          icon="⚠️"
          title="Failed Login Attempts"
          value={
            formatNumber(
              kpis?.failed_login_attempts
            )
          }
          subtitle="Authentication failures"
        />


        <KpiCard
          icon="📊"
          title="Failed Login Rate"
          value={
            formatPercentage(
              kpis?.failed_login_rate_pct
            )
          }
          subtitle="Login failure percentage"
        />


        <KpiCard
          icon="🚨"
          title="Total Incidents"
          value={
            formatNumber(
              kpis?.total_incidents
            )
          }
          subtitle="Security incidents"
        />


        <KpiCard
          icon="✅"
          title="Resolved Incidents"
          value={
            formatNumber(
              kpis?.resolved_incidents
            )
          }
          subtitle="Closed incidents"
        />


        <KpiCard
          icon="🎯"
          title="Resolution Rate"
          value={
            formatPercentage(
              kpis?.incident_resolution_rate_pct
            )
          }
          subtitle="Incident resolution"
        />


        <KpiCard
          icon="🖥️"
          title="High Criticality Assets"
          value={
            formatNumber(
              kpis?.high_criticality_assets
            )
          }
          subtitle="Assets requiring attention"
        />


        <KpiCard
          icon="💻"
          title="Suspicious Endpoint Events"
          value={
            formatNumber(
              kpis?.suspicious_endpoint_events
            )
          }
          subtitle="Potential endpoint threats"
        />


        <KpiCard
          icon="🌐"
          title="Network Events"
          value={
            formatNumber(
              kpis?.total_network_events
            )
          }
          subtitle="Network activity"
        />


      </div>


      {/* =================================================
          AUTHENTICATION ACTIVITY
      ================================================= */}

      <section className="chart-section authentication-section analytics-section">

        <SectionHeader
          title="Authentication Activity"
          subtitle="Login activity and failed authentication attempts over time"
          badge="LIVE ANALYTICS"
        />


        <div className="chart-card">


          {authenticationData.length > 0 ? (

            <ResponsiveContainer
              width="100%"
              height={430}
            >

              <LineChart
                data={
                  authenticationData
                }
                margin={{
                  top: 20,
                  right: 30,
                  left: 10,
                  bottom: 20
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#dbe4f0"
                />


                <XAxis
                  dataKey="date_day"
                  tick={{
                    fill: "#475569",
                    fontSize: 12
                  }}
                />


                <YAxis
                  tick={{
                    fill: "#475569",
                    fontSize: 12
                  }}
                />


                <Tooltip
                  content={
                    <CustomTooltip />
                  }
                  cursor={{
                    stroke: "#2563eb",
                    strokeWidth: 1
                  }}
                />


                <Legend />


                <Line
                  type="monotone"
                  dataKey="failed_login_attempts"
                  name="Failed Logins"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{
                    r: 6
                  }}
                />


                <Line
                  type="monotone"
                  dataKey="successful_login_attempts"
                  name="Successful Logins"
                  stroke="#22c55e"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{
                    r: 6
                  }}
                />


                <Line
                  type="monotone"
                  dataKey="total_login_attempts"
                  name="Total Logins"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{
                    r: 6
                  }}
                />

              </LineChart>

            </ResponsiveContainer>

          ) : (

            <div className="empty-chart">

              {loading
                ? "Loading authentication data..."
                : "No authentication data available."}

            </div>

          )}

        </div>

      </section>
      {/* =========================================================
    SETTINGS
========================================================= */}

<section className="settings-section">

  <div className="section-header">
    <div>
      <h2>Settings</h2>
      <p>CyberGuard platform configuration</p>
    </div>

    <div className="section-badge">
      SYSTEM
    </div>
  </div>

  <div className="settings-grid">

    <div className="settings-card">
      <div className="settings-icon">🗄️</div>
      <div>
        <h3>PostgreSQL Warehouse</h3>
        <p>Analytics warehouse connection</p>
        <span className="settings-status">CONNECTED</span>
      </div>
    </div>

    <div className="settings-card">
      <div className="settings-icon">⚡</div>
      <div>
        <h3>Kafka Streaming</h3>
        <p>Real-time security event pipeline</p>
        <span className="settings-status">ACTIVE</span>
      </div>
    </div>

    <div className="settings-card">
      <div className="settings-icon">🔄</div>
      <div>
        <h3>PySpark Processing</h3>
        <p>Streaming and transformation engine</p>
        <span className="settings-status">READY</span>
      </div>
    </div>

    <div className="settings-card">
      <div className="settings-icon">📊</div>
      <div>
        <h3>Analytics Layer</h3>
        <p>dbt Gold models and analytical marts</p>
        <span className="settings-status">READY</span>
      </div>
    </div>

  </div>

</section>


      {/* =================================================
          INCIDENT MONITORING
      ================================================= */}

      <section className="chart-section incidents-section">


        <SectionHeader
          title="Incident Monitoring"
          subtitle="Security incidents by severity and daily activity"
          badge="INCIDENT INTELLIGENCE"
        />


        {/* =================================================
            INCIDENT TREND
        ================================================= */}

        <div className="chart-card">

          <h3>
            Incident Trend
          </h3>


          <p className="chart-description">
            Daily incident volume and closed incidents
          </p>


          {incidentTrendData.length > 0 ? (

            <ResponsiveContainer
              width="100%"
              height={430}
            >

              {/* CHANGED FROM BarChart TO LineChart */}

              <LineChart
                data={
                  incidentTrendData
                }
                margin={{
                  top: 20,
                  right: 30,
                  left: 10,
                  bottom: 20
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#dbe4f0"
                />


                <XAxis
                  dataKey="date_day"
                  tick={{
                    fill: "#475569",
                    fontSize: 12
                  }}
                  minTickGap={30}
                />


                <YAxis
                  allowDecimals={false}
                  tick={{
                    fill: "#475569",
                    fontSize: 12
                  }}
                />


                <Tooltip
                  content={
                    <CustomTooltip />
                  }
                  cursor={{
                    stroke: "#2563eb",
                    strokeWidth: 1
                  }}
                />


                <Legend />


                <Line
                  type="monotone"
                  dataKey="closed_incident_count"
                  name="Closed Incidents"
                  stroke="#22c55e"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{
                    r: 6
                  }}
                />


                <Line
                  type="monotone"
                  dataKey="incident_count"
                  name="Total Incidents"
                  stroke="#2563eb"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{
                    r: 6
                  }}
                />


              </LineChart>

            </ResponsiveContainer>

          ) : (

            <div className="empty-chart">

              No incident trend data available.

            </div>

          )}

        </div>


        {/* =================================================
            INCIDENT SEVERITY
        ================================================= */}

        <div className="chart-card">

          <h3>
            Incident Severity
          </h3>


          <p className="chart-description">
            Distribution of security incidents by severity
          </p>


          {incidentSeverityData.length > 0 ? (

            <ResponsiveContainer
              width="100%"
              height={400}
            >

              <BarChart
                data={
                  incidentSeverityData
                }
                margin={{
                  top: 20,
                  right: 30,
                  left: 10,
                  bottom: 20
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#dbe4f0"
                />


                <XAxis
                  dataKey="severity"
                  tick={{
                    fill: "#475569"
                  }}
                />


                <YAxis
                  allowDecimals={false}
                  tick={{
                    fill: "#475569"
                  }}
                />


                <Tooltip
                  content={
                    <CustomTooltip />
                  }
                  cursor={{
                    fill:
                      "rgba(37,99,235,0.08)"
                  }}
                />


                <Bar
                  dataKey="incident_count"
                  name="Incidents"
                  fill="#2563eb"
                  radius={[
                    6,
                    6,
                    0,
                    0
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          ) : (

            <div className="empty-chart">

              No incident severity data available.

            </div>

          )}

        </div>


      </section>


      {/* =================================================
          ASSET SECURITY ANALYSIS
      ================================================= */}

      <section className="chart-section assets-section">


        <SectionHeader
          title="Asset Security Analysis"
          subtitle="Assets with the highest observed activity risk indicators"
          badge="ASSET INTELLIGENCE"
        />


        <div className="chart-card">


          {topAssets.length > 0 ? (

            <ResponsiveContainer
              width="100%"
              height={480}
            >

              <BarChart
                data={topAssets}
                layout="vertical"
                margin={{
                  top: 20,
                  right: 40,
                  left: 30,
                  bottom: 20
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#dbe4f0"
                />


                <XAxis
                  type="number"
                  tick={{
                    fill: "#475569"
                  }}
                />


                <YAxis
                  type="category"
                  dataKey="asset_label"
                  width={90}
                  tick={{
                    fill: "#475569",
                    fontSize: 12
                  }}
                />


                <Tooltip
                  content={
                    <CustomTooltip />
                  }
                  cursor={{
                    fill:
                      "rgba(37,99,235,0.08)"
                  }}
                />


                <Bar
                  dataKey="activity_risk_indicator"
                  name="Activity Risk Indicator"
                  fill="#2563eb"
                  radius={[
                    0,
                    6,
                    6,
                    0
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          ) : (

            <div className="empty-chart">

              No asset security data available.

            </div>

          )}

        </div>


      </section>


      {/* =================================================
          SUSPICIOUS ENDPOINT ACTIVITY
      ================================================= */}

      <section className="chart-section">


        <SectionHeader
          title="Suspicious Endpoint Activity"
          subtitle="Processes associated with suspicious endpoint events"
          badge="THREAT MONITORING"
        />


        <div className="chart-card">


          {suspiciousByProcess.length > 0 ? (

            <ResponsiveContainer
              width="100%"
              height={480}
            >

              <BarChart
                data={
                  suspiciousByProcess
                }
                layout="vertical"
                margin={{
                  top: 20,
                  right: 40,
                  left: 40,
                  bottom: 20
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#dbe4f0"
                />


                <XAxis
                  type="number"
                  tick={{
                    fill: "#475569"
                  }}
                />


                <YAxis
                  type="category"
                  dataKey="process"
                  width={140}
                  tick={{
                    fill: "#475569",
                    fontSize: 12
                  }}
                />


                <Tooltip
                  content={
                    <CustomTooltip />
                  }
                  cursor={{
                    fill:
                      "rgba(37,99,235,0.08)"
                  }}
                />


                <Bar
                  dataKey="suspicious_event_count"
                  name="Suspicious Events"
                  fill="#ef4444"
                  radius={[
                    0,
                    6,
                    6,
                    0
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          ) : (

            <div className="empty-chart">

              No suspicious endpoint data available.

            </div>

          )}

        </div>


      </section>

{/* ===================================================
    SECURITY ALERTS
=================================================== */}

<SecurityAlerts />

{/* ===================================================
    LIVE SECURITY EVENTS
=================================================== */}

<LiveEvents />


      {/* =================================================
          DATA PIPELINE
      ================================================= */}

      <section className="pipeline-section">

        <h2>
          CyberGuard Data Pipeline
        </h2>


        <p>
          From security events to actionable intelligence
        </p>


        <div className="pipeline">


          <div className="pipeline-card">

            <div className="pipeline-icon">
              📥
            </div>

            <h3>
              Data Sources
            </h3>

            <span>
              Security logs & events
            </span>

          </div>


          <div className="arrow">
            →
          </div>


          <div className="pipeline-card">

            <div className="pipeline-icon">
              ⚡
            </div>

            <h3>
              Kafka
            </h3>

            <span>
              Real-time event streaming
            </span>

          </div>


          <div className="arrow">
            →
          </div>


          <div className="pipeline-card">

            <div className="pipeline-icon">
              🔥
            </div>

            <h3>
              PySpark
            </h3>

            <span>
              Data transformation
            </span>

          </div>


          <div className="arrow">
            →
          </div>


          <div className="pipeline-card">

            <div className="pipeline-icon">
              🐘
            </div>

            <h3>
              PostgreSQL
            </h3>

            <span>
              Analytics warehouse
            </span>

          </div>


          <div className="arrow">
            →
          </div>


          <div className="pipeline-card">

            <div className="pipeline-icon">
              🔧
            </div>

            <h3>
              dbt
            </h3>

            <span>
              Gold analytical layer
            </span>

          </div>


          <div className="arrow">
            →
          </div>


          <div className="pipeline-card">

            <div className="pipeline-icon">
              📊
            </div>

            <h3>
              Analytics
            </h3>

            <span>
              Security intelligence
            </span>

          </div>


        </div>

      </section>


      {/* =================================================
          FOOTER
      ================================================= */}
{/* =========================================================
    REPORTS
========================================================= */}

<section className="reports-section">

  <div className="section-header">
    <div>
      <h2>Reports</h2>
      <p>Security analytics and operational reports</p>
    </div>

    <div className="section-badge">
      REPORT CENTER
    </div>
  </div>

  <div className="reports-grid">

    <div className="report-card">
      <div className="report-icon">📊</div>

      <div>
        <h3>Security Overview</h3>
        <p>
          Overall authentication, incidents, assets and
          endpoint security metrics.
        </p>
      </div>
    </div>

    <div className="report-card">
      <div className="report-icon">🔐</div>

      <div>
        <h3>Authentication Report</h3>
        <p>
          Login attempts, failed authentication activity
          and authentication trends.
        </p>
      </div>
    </div>

    <div className="report-card">
      <div className="report-icon">🚨</div>

      <div>
        <h3>Incident Report</h3>
        <p>
          Incident counts, status and resolution
          analysis.
        </p>
      </div>
    </div>

    <div className="report-card">
      <div className="report-icon">🖥️</div>

      <div>
        <h3>Asset Security Report</h3>
        <p>
          Asset activity and security risk indicators
          across the environment.
        </p>
      </div>
    </div>

  </div>

</section>
      <footer className="footer">


        <h2>
          CyberGuard Analytics
        </h2>

        <p>
          Data Engineering + Analytics + Cybersecurity
        </p>

      </footer>


      {/* =================================================
          CSS
      ================================================= */}

      <style>{`

        * {
          box-sizing: border-box;
        }


        body {

          margin: 0;

          font-family:
            Inter,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;

          background:
            linear-gradient(
              135deg,
              #eef4ff 0%,
              #f8fafc 50%,
              #eef4ff 100%
            );

          color: #172033;

        }


        .app {

          width: 100%;

          max-width: 1250px;

          margin: 0 auto;

          padding:
            32px 42px 60px;

        }


        .header {

          position: relative;

          text-align: center;

          background:
            rgba(
              255,
              255,
              255,
              0.92
            );

          border:
            1px solid #dbe4f0;

          border-radius: 22px;

          padding:
            34px 30px;

          margin-bottom: 26px;

          box-shadow:
            0 12px 35px
            rgba(
              30,
              64,
              175,
              0.08
            );

        }


        .shield {

          font-size: 28px;

          margin-bottom: 8px;

        }


        .header h1 {

          margin: 0;

          font-size: 44px;

          font-weight: 800;

          letter-spacing: 1px;

          color: #101828;

        }


        .header-subtitle {

          margin:
            10px 0 0;

          color: #64748b;

          font-size: 19px;

        }


        .header-actions {

          display: flex;

          justify-content: center;

          align-items: center;

          gap: 12px;

          margin-top: 24px;

        }


        .api-status {

          display: flex;

          align-items: center;

          gap: 8px;

          border-radius: 30px;

          padding:
            10px 18px;

          font-weight: 700;

          font-size: 14px;

          border: 1px solid;

        }


        .api-status.online {

          color: #15803d;

          background: #f0fdf4;

          border-color: #bbf7d0;

        }


        .api-status.offline {

          color: #b91c1c;

          background: #fef2f2;

          border-color: #fecaca;

        }


        .status-dot {

          width: 10px;

          height: 10px;

          border-radius: 50%;

          background:
            currentColor;

        }


        .refresh-button {

          border: none;

          border-radius: 10px;

          padding:
            11px 20px;

          background: #2563eb;

          color: white;

          font-size: 14px;

          font-weight: 700;

          cursor: pointer;

          transition: 0.2s;

        }


        .refresh-button:hover {

          background: #1d4ed8;

          transform:
            translateY(-1px);

        }


        .error-message {

          background: #fff7ed;

          color: #c2410c;

          border:
            1px solid #fed7aa;

          border-radius: 12px;

          padding:
            14px 18px;

          margin-bottom: 24px;

          text-align: center;

          font-weight: 600;

        }


        .system-info {

          display: grid;

          grid-template-columns:
            repeat(4, 1fr);

          gap: 16px;

          margin-bottom: 36px;

        }


        .info-card {

          background:
            rgba(
              255,
              255,
              255,
              0.92
            );

          border:
            1px solid #dbe4f0;

          border-radius: 16px;

          padding: 20px;

          min-height: 105px;

          display: flex;

          flex-direction: column;

          justify-content: center;

          text-align: center;

          box-shadow:
            0 8px 25px
            rgba(
              15,
              23,
              42,
              0.04
            );

        }


        .info-card span {

          font-size: 12px;

          font-weight: 800;

          letter-spacing: 1px;

          color: #64748b;

          margin-bottom: 12px;

        }


        .info-card strong {

          font-size: 16px;

          color: #172033;

        }


        .section-header {

          margin:
            32px 0 16px;

        }


        .section-header h2 {

          margin: 0;

          font-size: 28px;

          color: #172033;

        }


        .section-header p {

          margin:
            8px 0 0;

          color: #64748b;

          font-size: 16px;

        }


        .section-badge {

          text-align: center;

          padding: 9px;

          margin-bottom: 0;

          border:
            1px solid #bfdbfe;

          background: #eff6ff;

          color: #2563eb;

          font-weight: 800;

          font-size: 13px;

          letter-spacing: 0.5px;

          border-radius:
            8px 8px 0 0;

        }


        .kpi-grid {

          display: grid;

          grid-template-columns:
            repeat(3, 1fr);

          gap: 18px;

          margin-bottom: 35px;

        }


        .kpi-card {

          position: relative;

          background:
            rgba(
              255,
              255,
              255,
              0.96
            );

          border:
            1px solid #dbe4f0;

          border-left:
            5px solid #2563eb;

          border-radius: 16px;

          padding:
            26px 20px;

          min-height: 165px;

          text-align: center;

          box-shadow:
            0 10px 28px
            rgba(
              15,
              23,
              42,
              0.06
            );

          transition: 0.2s;

        }


        .kpi-card:hover {

          transform:
            translateY(-3px);

          box-shadow:
            0 14px 35px
            rgba(
              37,
              99,
              235,
              0.12
            );

        }


        .kpi-icon {

          font-size: 25px;

          margin-bottom: 7px;

        }


        .kpi-title {

          color: #64748b;

          font-size: 14px;

          font-weight: 700;

          margin-bottom: 9px;

        }


        .kpi-value {

          font-size: 34px;

          font-weight: 800;

          color: #172033;

          line-height: 1.1;

        }


        .kpi-subtitle {

          margin-top: 10px;

          color: #94a3b8;

          font-size: 13px;

        }


        .chart-section {

          margin-top: 38px;

        }


        .chart-card {

          background:
            rgba(
              255,
              255,
              255,
              0.97
            );

          border:
            1px solid #dbe4f0;

          border-radius: 16px;

          padding: 24px;

          margin-bottom: 22px;

          box-shadow:
            0 10px 28px
            rgba(
              15,
              23,
              42,
              0.05
            );

        }


        .chart-card h3 {

          text-align: center;

          margin: 0;

          font-size: 23px;

          color: #172033;

        }


        .chart-description {

          text-align: center;

          color: #64748b;

          margin:
            10px 0 18px;

        }


        .empty-chart {

          height: 430px;

          display: flex;

          align-items: center;

          justify-content: center;

          color: #64748b;

          font-size: 16px;

        }


        .custom-tooltip {

          background: #ffffff;

          border:
            1px solid #2563eb;

          border-radius: 10px;

          padding:
            12px 15px;

          min-width: 190px;

          box-shadow:
            0 12px 30px
            rgba(
              15,
              23,
              42,
              0.18
            );

        }


        .tooltip-date {

          color: #111827;

          font-weight: 800;

          font-size: 14px;

          padding-bottom: 8px;

          margin-bottom: 8px;

          border-bottom:
            1px solid #e5e7eb;

        }


        .tooltip-row {

          display: flex;

          align-items: center;

          justify-content: space-between;

          gap: 20px;

          padding: 4px 0;

          font-size: 13px;

        }


        .tooltip-label {

          font-weight: 600;

        }


        .tooltip-value {

          color: #111827;

        }


        .pipeline-section {

          margin-top: 55px;

          text-align: center;

        }


        .pipeline-section h2 {

          margin: 0;

          font-size: 28px;

        }


        .pipeline-section > p {

          color: #64748b;

          margin-top: 8px;

        }


        .pipeline {

          display: flex;

          align-items: center;

          justify-content: center;

          gap: 12px;

          overflow-x: auto;

          padding:
            25px 5px;

        }


        .pipeline-card {

          min-width: 145px;

          min-height: 145px;

          background:
            rgba(
              255,
              255,
              255,
              0.95
            );

          border:
            1px solid #dbe4f0;

          border-radius: 15px;

          padding:
            20px 12px;

          display: flex;

          flex-direction: column;

          justify-content: center;

          align-items: center;

          box-shadow:
            0 8px 22px
            rgba(
              15,
              23,
              42,
              0.05
            );

        }


        .pipeline-icon {

          font-size: 27px;

          margin-bottom: 8px;

        }


        .pipeline-card h3 {

          margin:
            0 0 8px;

          font-size: 16px;

        }


        .pipeline-card span {

          color: #64748b;

          font-size: 12px;

        }


        .arrow {

          font-size: 27px;

          color: #2563eb;

          font-weight: 700;

        }


        .footer {

          text-align: center;

          margin-top: 45px;

          padding-top: 25px;

          border-top:
            1px solid #dbe4f0;

        }


        .footer h2 {

          margin: 0;

          font-size: 20px;

        }


        .footer p {

          color: #94a3b8;

          margin-top: 8px;

        }


        /* =================================================
           RESPONSIVE
        ================================================= */

        @media (max-width: 900px) {

          .app {

            padding: 20px;

          }


          .header h1 {

            font-size: 32px;

          }


          .system-info {

            grid-template-columns:
              repeat(2, 1fr);

          }


          .kpi-grid {

            grid-template-columns:
              repeat(2, 1fr);

          }

        }


        @media (max-width: 600px) {

          .app {

            padding: 14px;

          }


          .header {

            padding:
              25px 15px;

          }


          .header h1 {

            font-size: 26px;

          }


          .header-subtitle {

            font-size: 15px;

          }


          .header-actions {

            flex-direction: column;

          }


          .system-info {

            grid-template-columns: 1fr;

          }


          .kpi-grid {

            grid-template-columns: 1fr;

          }


          .pipeline {

            justify-content:
              flex-start;

          }


          .arrow {

            display: none;

          }

        }

      `}</style>

        </div>

      </main>

    </div>

  );
}


export default App;