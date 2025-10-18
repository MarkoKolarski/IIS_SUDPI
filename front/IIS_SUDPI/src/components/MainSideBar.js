import React from "react";
import "../styles/MainSideBar.css";
import { useNavigate, NavLink } from "react-router-dom";
import { sidebarLinks } from "./MainSideBarLinks";

const MainSideBar = ({ isCollapsed, toggleSidebar }) => {
  const navigate = useNavigate();
  const userType = sessionStorage.getItem("user_type");
  const links = sidebarLinks[userType] || [];

  const icon = "★";
  const activeIcon = "⭐";

  const handleLogout = () => {
    sessionStorage.clear();
    navigate("/login");
  };

  const handleProfile = () => {
    console.log("Profile action");
     navigate('/profile');
  };

  return (
    <div className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      <div className="sidebar-header">
        {!isCollapsed && <h2 className="sidebar-title">Meni</h2>}
        <button className="collapse-btn" onClick={toggleSidebar}>
          {isCollapsed ? "☰" : "✖"}
        </button>
      </div>

      <nav className="sidebar-nav">
        {links.map((link, index) => (
          <NavLink
            key={index}
            to={link.href}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            {({ isActive }) => (
              <>
                <span className="nav-icon">{isActive ? activeIcon : icon}</span>
                {!isCollapsed && (
                  <div className="nav-text">
                    <span className="nav-title">{link.title}</span>
                    {link.description && (
                      <span className="nav-description">
                        {link.description}
                      </span>
                    )}
                  </div>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        {!isCollapsed && (
          <>
            <button onClick={handleProfile} className="footer-btn profile-btn">
              Profil
            </button>
            <button onClick={handleLogout} className="footer-btn logout-btn">
              Odjava
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default MainSideBar;
