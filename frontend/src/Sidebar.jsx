import React, { useEffect, useState } from "react";

function Sidebar() {
  const [alertCount, setAlertCount] = useState(0);

  const scrollToSection = (selector) => {
    const section = document.querySelector(selector);

    if (section) {
      section.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  useEffect(() => {
    const fetchAlertCount = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8001/security-alerts?limit=20"
        );

        if (!response.ok) {
          throw new Error("Failed to fetch alert count");
        }

        const data = await response.json();

        setAlertCount(data.length);
      } catch (error) {
        console.error("Unable to fetch security alert count");
      }
    };

    fetchAlertCount();

    const interval = setInterval(() => {
      fetchAlertCount();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="cyber-sidebar">

      {/* BRAND */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">🛡</div>

        <div>
          <div className="sidebar-brand-title">
            CYBERGUARD
          </div>

          <div className="sidebar-brand-subtitle">
            ANALYTICS
          </div>
        </div>
      </div>


      {/* NAVIGATION */}
      <nav className="sidebar-nav">

        <div
          className="sidebar-item active"
          onClick={() => scrollToSection(".cyber-main")}
        >
          <span className="sidebar-icon">⌂</span>
          <span>Dashboard</span>
        </div>


        <div
          className="sidebar-item"
          onClick={() =>
            scrollToSection(".security-alerts-section")
          }
        >
          <span className="sidebar-icon">♧</span>

          <span>Security Alerts</span>

          {alertCount > 0 && (
            <span className="sidebar-count">
              {alertCount}
            </span>
          )}
        </div>


        <div
          className="sidebar-item"
          onClick={() =>
            scrollToSection(".live-events-section")
          }
        >
          <span className="sidebar-icon">ϟ</span>
          <span>Live Events</span>
        </div>


        <div
          className="sidebar-item"
          onClick={() =>
            scrollToSection(".authentication-section")
          }
        >
          <span className="sidebar-icon">◉</span>
          <span>Authentication</span>
        </div>


        <div
          className="sidebar-item"
          onClick={() =>
            scrollToSection(".incidents-section")
          }
        >
          <span className="sidebar-icon">⚠</span>
          <span>Incidents</span>
        </div>


        <div
          className="sidebar-item"
          onClick={() =>
            scrollToSection(".assets-section")
          }
        >
          <span className="sidebar-icon">▣</span>
          <span>Assets</span>
        </div>


        <div
          className="sidebar-item"
          onClick={() =>
            scrollToSection(".analytics-section")
          }
        >
          <span className="sidebar-icon">▥</span>
          <span>Analytics</span>
        </div>


        <div
          className="sidebar-item"
          onClick={() =>
            scrollToSection(".pipeline-section")
          }
        >
          <span className="sidebar-icon">◈</span>
          <span>Data Pipeline</span>
        </div>


        <div
          className="sidebar-item"
          onClick={() =>
            scrollToSection(".reports-section")
          }
        >
          <span className="sidebar-icon">▤</span>
          <span>Reports</span>
        </div>


        <div
          className="sidebar-item"
          onClick={() =>
            scrollToSection(".settings-section")
          }
        >
          <span className="sidebar-icon">⚙</span>
          <span>Settings</span>
        </div>

      </nav>
    </aside>
  );
}

export default Sidebar;