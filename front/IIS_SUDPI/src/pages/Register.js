import React, { useState } from 'react';
import axiosInstance from '../axiosInstance';
import '../styles/Register.css';

const Register = () => {
    const [formData, setFormData] = useState({
        ime_k: '',
        prz_k: '',
        mail_k: '',
        password: '',
        tip_k: '',
    });
    const [errors, setErrors] = useState({});
    const [message, setMessage] = useState('');

    const userTypes = [
        { value: 'logisticki_koordinator', label: 'Logistički koordinator' },
        { value: 'skladisni_operater', label: 'Skladišni operater' },
        { value: 'nabavni_menadzer', label: 'Nabavni menadžer' },
        { value: 'finansijski_analiticar', label: 'Finansijski analitičar' },
        { value: 'kontrolor_kvaliteta', label: 'Kontrolor kvaliteta' },
        { value: 'administrator', label: 'Administrator' },
    ];

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
            setFormData({  // Resetuj formu nakon uspešne registracije
                ime_k: '',
                prz_k: '',
                mail_k: '',
                password: '',
                tip_k: '',
            });
        } catch (error) {
            if (error.response && error.response.data) {
                setErrors(error.response.data);  // Dodeljivanje grešaka koje dolaze sa backend-a
            }
        }
    };

    return (
        <div className="register-container">
            <h2>Registracija</h2>
            
            {message && <p className="message success">{message}</p>}
            
            {errors.detail && <p className="message error">{errors.detail}</p>}

            <form onSubmit={handleSubmit} className="register-form">
                <input
                    type="text"
                    name="ime_k"
                    placeholder="Ime"
                    value={formData.ime_k}
                    onChange={handleChange}
                    required
                />
                {errors.ime_k && <p className="error-message">{errors.ime_k}</p>}

                <input
                    type="text"
                    name="prz_k"
                    placeholder="Prezime"
                    value={formData.prz_k}
                    onChange={handleChange}
                    required
                />
                {errors.prz_k && <p className="error-message">{errors.prz_k}</p>}

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

                <select
                    name="tip_k"
                    value={formData.tip_k}
                    onChange={handleChange}
                    required
                >
                    <option value="">Izaberite radno mesto</option>
                    {userTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                            {type.label}
                        </option>
                    ))}
                </select>
                {errors.tip_k && <p className="error-message">{errors.tip_k}</p>}

                <button type="submit">Potvrdi registraciju</button>
            </form>
        </div>
    );
};

export default Register;
