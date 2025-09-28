import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/NavBar.css';

const Navbar = () => {
    return (
        <nav className="navbar">
            <h1 className="title">
                <Link to="/" className="title-link">Centar za dobavljače</Link>
            </h1>
            <ul className="nav-links">
                <li><Link to="/login">Login</Link></li>
                <li><Link to="/register">Register</Link></li>
            </ul>
        </nav>
    );
};

export default Navbar;
