import React from 'react';
import '../styles/SideBar.css';
import { useNavigate, useLocation } from 'react-router-dom';

const SideBar = ({ isCollapsed, toggleSidebar }) => {
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        // Implement your logout logic here
        console.log("Logout action");
        navigate('/login');
    };

    const handleProfile = () => {
        // Implement your profile navigation logic here
        console.log("Profile action");
        // navigate('/profile');
    };

    return (
        <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
            <div className="sidebar-header">
                {!isCollapsed && <h2 className="sidebar-title">Meni</h2>}
                <button className="collapse-btn" onClick={toggleSidebar}>
                    {isCollapsed ? '☰' : '✖'}
                </button>
            </div>
            <nav className="sidebar-nav">
                <a href="/dashboard-fa" className={`nav-item ${location.pathname === '/dashboard-fa' ? 'active' : ''}`}>
                    <span className="nav-icon">{location.pathname === '/dashboard-fa' ? '⭐' : '★'}</span>
                    {!isCollapsed && (
                        <div className="nav-text">
                            <span className="nav-title">Kontrolna tabla</span>
                            <span className="nav-description">Pregled ključnih podataka i metrika</span>
                        </div>
                    )}
                </a>
                <a href="/invoice" className={`nav-item ${location.pathname === '/invoice' ? 'active' : ''}`}>
                    <span className="nav-icon">{location.pathname === '/invoice' ? '⭐' : '★'}</span>
                    {!isCollapsed && (
                        <div className="nav-text">
                            <span className="nav-title">Fakture</span>
                            <span className="nav-description">Upravljanje računima i plaćanjima</span>
                        </div>
                    )}
                </a>
                <a href="/reports" className={`nav-item ${location.pathname === '/reports' ? 'active' : ''}`}>
                    <span className="nav-icon">{location.pathname === '/reports' ? '⭐' : '★'}</span>
                    {!isCollapsed && (
                        <div className="nav-text">
                            <span className="nav-title">Izveštaji</span>
                            <span className="nav-description">Analiza troškova i performansi</span>
                        </div>
                    )}
                </a>
                <a href="/penalties" className={`nav-item ${location.pathname === '/penalties' ? 'active' : ''}`}>
                    <span className="nav-icon">{location.pathname === '/penalties' ? '⭐' : '★'}</span>
                    {!isCollapsed && (
                        <div className="nav-text">
                            <span className="nav-title">Penali</span>
                            <span className="nav-description">Evidencija i obračun kašnjenja</span>
                        </div>
                    )}
                </a>
            </nav>
            <div className="sidebar-footer">
                {!isCollapsed && (
                    <>
                        <button onClick={handleProfile} className="footer-btn profile-btn">Profil</button>
                        <button onClick={handleLogout} className="footer-btn logout-btn">Odjava</button>
                    </>
                )}
            </div>
        </div>
    );
};

export default SideBar;
