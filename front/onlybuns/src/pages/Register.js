import React, { useState } from 'react';
import axiosInstance from '../axiosInstance';
import '../styles/Register.css';

const Register = () => {
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        password: '',
        confirm_password: '',
        first_name: '',
        last_name: '',
        location: '',
    });
    const [errors, setErrors] = useState({});
    const [message, setMessage] = useState('');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setErrors({ ...errors, [e.target.name]: '' });  // Resetovanje greške pri promeni polja
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});  // Resetuj greške pre nego što pošaljemo zahtev
        setMessage('');  // Resetuj prethodnu poruku

        try {
            const response = await axiosInstance.post('register/', formData);
            setMessage(response.data.message);  // Prikazujemo poruku koju backend vraća
        } catch (error) {
            if (error.response && error.response.data) {
                setErrors(error.response.data);  // Dodeljivanje grešaka koje dolaze sa backend-a
            }
        }
    };

    return (
        <div className="register-container">
            <h2>Registration</h2>
            
            {message && <p className="message success">{message}</p>}
            
            {errors.detail && <p className="message error">{errors.detail}</p>}

            <form onSubmit={handleSubmit} className="register-form">
                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                />
                {errors.email && <p className="error-message">{errors.email}</p>}

                <input
                    type="text"
                    name="username"
                    placeholder="Username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                />
                {errors.username && <p className="error-message">{errors.username}</p>}

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                />
                {errors.password && <p className="error-message">{errors.password}</p>}

                <input
                    type="password"
                    name="confirm_password"
                    placeholder="Confirm Password"
                    value={formData.confirm_password}
                    onChange={handleChange}
                    required
                />
                {errors.confirm_password && <p className="error-message">{errors.confirm_password}</p>}

                <input
                    type="text"
                    name="first_name"
                    placeholder="First Name"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                />
                {errors.first_name && <p className="error-message">{errors.first_name}</p>}

                <input
                    type="text"
                    name="last_name"
                    placeholder="Last Name"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                />
                {errors.last_name && <p className="error-message">{errors.last_name}</p>}

                <input
                    type="text"
                    name="location"
                    placeholder="Location"
                    value={formData.location}
                    onChange={handleChange}
                    required
                />
                {errors.location && <p className="error-message">{errors.location}</p>}

                <button type="submit">Register</button>
            </form>
        </div>
    );
};

export default Register;
