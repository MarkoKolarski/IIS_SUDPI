import React, { useState } from 'react';
import axiosInstance from '../axiosInstance';
import { useNavigate } from 'react-router-dom';
import '../styles/Login.css';
import NavBar from '../components/NavBar';

const Login = () => {
    const [formData, setFormData] = useState({
        mail_k: '',
        password: '',
    });
    const [errors, setErrors] = useState({});
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setErrors({ ...errors, [e.target.name]: '' });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});
        setMessage('');

        try {
            const response = await axiosInstance.post('login/', formData);
            setMessage('Uspešna prijava!');
            sessionStorage.setItem('access_token', response.data.access);
            sessionStorage.setItem('refresh_token', response.data.refresh);
            sessionStorage.setItem('user_type', response.data.user_type);
            sessionStorage.setItem('user_name', response.data.user_name);
            
            // Redirect based on user type
            if (response.data.user_type === 'finansijski_analiticar') {
                navigate('/dashboard-fa');
            } else {
                // For other user types, redirect to home or a generic dashboard
                navigate('/');
            }
        } catch (error) {
            if (error.response && error.response.data) {
                setErrors(error.response.data);
            }
        }
    };

    return (
        <>
            <NavBar />
            <div className="login-container">
                <h2>Prijava</h2>
                
                {message && <p className="message success">{message}</p>}
                
                {errors.detail && <p className="message error">{errors.detail}</p>}

                <form onSubmit={handleSubmit} className="login-form">
                    <input
                        type="email"
                        name="mail_k"
                        placeholder="Email"
                        value={formData.mail_k}
                        onChange={handleChange}
                        required
                    />
                    {errors.mail_k && <p className="error-message">{errors.mail_k}</p>}

                    <input
                        type="password"
                        name="password"
                        placeholder="Lozinka"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                    {errors.password && <p className="error-message">{errors.password}</p>}

                    <button type="submit">Prijavi se</button>
                </form>
            </div>
        </>
    );
};

export default Login;
