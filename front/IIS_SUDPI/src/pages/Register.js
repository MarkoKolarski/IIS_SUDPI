import React, { useState } from "react";
import { Link } from "react-router-dom";
import axiosInstance from "../axiosInstance";
import "../styles/Register.css";
import MainSideBar from "../components/MainSideBar";
import PageTransition from "../components/PageTransition";

const INITIAL_FORM_DATA = {
  ime_k: "",
  prz_k: "",
  mail_k: "",
  password: "",
  password_confirm: "",
  tip_k: "",
};

const normalizeErrorText = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).join(" ");
  }

  if (typeof value === "string") {
    return value;
  }

  if (value && typeof value === "object") {
    if (typeof value.detail === "string") {
      return value.detail;
    }

    if (typeof value.message === "string") {
      return value.message;
    }
  }

  return "";
};

const Register = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [formData, setFormData] = useState(INITIAL_FORM_DATA);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState({ type: "", text: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isAdmin = sessionStorage.getItem("user_type") === "administrator";

  const userTypes = [
    { value: "logisticki_koordinator", label: "Logistički koordinator" },
    { value: "skladisni_operater", label: "Skladišni operater" },
    { value: "nabavni_menadzer", label: "Nabavni menadžer" },
    { value: "finansijski_analiticar", label: "Finansijski analitičar" },
    { value: "kontrolor_kvaliteta", label: "Kontrolor kvaliteta" },
    { value: "administrator", label: "Administrator" },
  ];

  const getFieldError = (fieldName) => normalizeErrorText(errors[fieldName]);

  const validateForm = () => {
    const validationErrors = {};
    const namePattern = /^[A-Za-zČĆŽŠĐčćžšđ\s'-]{2,}$/;
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const ime = formData.ime_k.trim();
    const prezime = formData.prz_k.trim();
    const email = formData.mail_k.trim();
    const password = formData.password;

    if (!ime) {
      validationErrors.ime_k = "Ime je obavezno.";
    } else if (!namePattern.test(ime)) {
      validationErrors.ime_k = "Ime mora imati najmanje 2 karaktera i sadržati samo slova.";
    }

    if (!prezime) {
      validationErrors.prz_k = "Prezime je obavezno.";
    } else if (!namePattern.test(prezime)) {
      validationErrors.prz_k = "Prezime mora imati najmanje 2 karaktera i sadržati samo slova.";
    }

    if (!email) {
      validationErrors.mail_k = "Email adresa je obavezna.";
    } else if (!emailPattern.test(email)) {
      validationErrors.mail_k = "Unesite ispravnu email adresu.";
    }

    if (!password) {
      validationErrors.password = "Lozinka je obavezna.";
    } else if (password.length < 8) {
      validationErrors.password = "Lozinka mora imati najmanje 8 karaktera.";
    } else if (/^\d+$/.test(password)) {
      validationErrors.password = "Lozinka ne može biti samo numerička.";
    }

    if (!formData.password_confirm) {
      validationErrors.password_confirm = "Potvrda lozinke je obavezna.";
    } else if (formData.password_confirm !== password) {
      validationErrors.password_confirm = "Lozinke se ne poklapaju.";
    }

    if (!formData.tip_k) {
      validationErrors.tip_k = "Izaberite radno mesto korisnika.";
    }

    setErrors(validationErrors);
    return Object.keys(validationErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: "" }));

    if (message.text) {
      setMessage({ type: "", text: "" });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      setMessage({ type: "error", text: "Ispravite označena polja i pokušajte ponovo." });
      return;
    }

    setErrors({});
    setMessage({ type: "", text: "" });
    setIsSubmitting(true);

    const payload = {
      ime_k: formData.ime_k.trim(),
      prz_k: formData.prz_k.trim(),
      mail_k: formData.mail_k.trim().toLowerCase(),
      password: formData.password,
      tip_k: formData.tip_k,
    };

    try {
      const response = await axiosInstance.post("register/", payload);

      setMessage({
        type: "success",
        text: response.data?.message || "Korisnik je uspešno registrovan.",
      });

      setFormData(INITIAL_FORM_DATA);
    } catch (error) {
      const responseData = error.response?.data;

      if (responseData && typeof responseData === "object") {
        const nextErrors = {};

        Object.entries(responseData).forEach(([fieldName, value]) => {
          const normalized = normalizeErrorText(value);
          if (normalized && !["detail", "error", "non_field_errors", "details"].includes(fieldName)) {
            nextErrors[fieldName] = normalized;
          }
        });

        const generalMessage =
          normalizeErrorText(responseData.detail) ||
          normalizeErrorText(responseData.error) ||
          normalizeErrorText(responseData.non_field_errors) ||
          normalizeErrorText(responseData.details);

        setErrors(nextErrors);
        setMessage({
          type: "error",
          text:
            generalMessage ||
            (Object.keys(nextErrors).length > 0
              ? "Registracija nije uspela. Proverite unete podatke."
              : "Registracija nije uspela. Pokušajte ponovo."),
        });
      } else {
        setMessage({
          type: "error",
          text: "Greška pri komunikaciji sa serverom. Pokušajte ponovo.",
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleSidebar = () => {
    setSidebarCollapsed((prev) => !prev);
  };

  return (
    <PageTransition>
      <div
        className={`register-wrapper ${
          isSidebarCollapsed ? "sidebar-collapsed" : ""
        } ${
          isAdmin ? "has-sidebar" : "no-sidebar"
        }`}
      >
        {isAdmin && (
          <MainSideBar
            isCollapsed={isSidebarCollapsed}
            toggleSidebar={toggleSidebar}
          />
        )}
        <main className="register-main-content">
          <header className="register-header">
            <h1>Registracija korisnika</h1>
          </header>

          <section className="register-content">
            <div className="register-card">
              <div className="register-card-header">
                <h2>Kreiranje novog naloga</h2>
                <p>Popunite podatke i dodelite korisniku odgovarajuću ulogu u sistemu.</p>
              </div>

              <div className="register-card-body">
                {message.text && (
                  <div
                    className={`register-message ${message.type}`}
                    role={message.type === "error" ? "alert" : "status"}
                    aria-live="polite"
                  >
                    {message.text}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="register-form" noValidate>
                  <div className="register-form-grid">
                    <div className="register-form-group">
                      <label htmlFor="ime_k" className="register-form-label">
                        Ime
                      </label>
                      <input
                        id="ime_k"
                        type="text"
                        name="ime_k"
                        className={`register-form-control ${
                          getFieldError("ime_k") ? "is-invalid" : ""
                        }`}
                        placeholder="Unesite ime"
                        value={formData.ime_k}
                        onChange={handleChange}
                        autoComplete="given-name"
                        required
                      />
                      {getFieldError("ime_k") && (
                        <p className="register-error-message">{getFieldError("ime_k")}</p>
                      )}
                    </div>

                    <div className="register-form-group">
                      <label htmlFor="prz_k" className="register-form-label">
                        Prezime
                      </label>
                      <input
                        id="prz_k"
                        type="text"
                        name="prz_k"
                        className={`register-form-control ${
                          getFieldError("prz_k") ? "is-invalid" : ""
                        }`}
                        placeholder="Unesite prezime"
                        value={formData.prz_k}
                        onChange={handleChange}
                        autoComplete="family-name"
                        required
                      />
                      {getFieldError("prz_k") && (
                        <p className="register-error-message">{getFieldError("prz_k")}</p>
                      )}
                    </div>

                    <div className="register-form-group register-form-group-full">
                      <label htmlFor="mail_k" className="register-form-label">
                        Email adresa
                      </label>
                      <input
                        id="mail_k"
                        type="email"
                        name="mail_k"
                        className={`register-form-control ${
                          getFieldError("mail_k") ? "is-invalid" : ""
                        }`}
                        placeholder="primer@firma.com"
                        value={formData.mail_k}
                        onChange={handleChange}
                        autoComplete="email"
                        required
                      />
                      {getFieldError("mail_k") && (
                        <p className="register-error-message">{getFieldError("mail_k")}</p>
                      )}
                    </div>

                    <div className="register-form-group">
                      <label htmlFor="password" className="register-form-label">
                        Lozinka
                      </label>
                      <input
                        id="password"
                        type="password"
                        name="password"
                        className={`register-form-control ${
                          getFieldError("password") ? "is-invalid" : ""
                        }`}
                        placeholder="Unesite lozinku"
                        value={formData.password}
                        onChange={handleChange}
                        autoComplete="new-password"
                        required
                      />
                      <p className="register-password-hint">
                        Najmanje 8 karaktera i ne sme biti samo numerička.
                      </p>
                      {getFieldError("password") && (
                        <p className="register-error-message">{getFieldError("password")}</p>
                      )}
                    </div>

                    <div className="register-form-group">
                      <label htmlFor="password_confirm" className="register-form-label">
                        Potvrda lozinke
                      </label>
                      <input
                        id="password_confirm"
                        type="password"
                        name="password_confirm"
                        className={`register-form-control ${
                          getFieldError("password_confirm") ? "is-invalid" : ""
                        }`}
                        placeholder="Ponovite lozinku"
                        value={formData.password_confirm}
                        onChange={handleChange}
                        autoComplete="new-password"
                        required
                      />
                      {getFieldError("password_confirm") && (
                        <p className="register-error-message">{getFieldError("password_confirm")}</p>
                      )}
                    </div>

                    <div className="register-form-group register-form-group-full">
                      <label htmlFor="tip_k" className="register-form-label">
                        Radno mesto
                      </label>
                      <select
                        id="tip_k"
                        name="tip_k"
                        className={`register-form-control register-form-select ${
                          getFieldError("tip_k") ? "is-invalid" : ""
                        }`}
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
                      {getFieldError("tip_k") && (
                        <p className="register-error-message">{getFieldError("tip_k")}</p>
                      )}
                    </div>
                  </div>

                  <div className="register-actions">
                    <button type="submit" className="register-submit-btn" disabled={isSubmitting}>
                      {isSubmitting ? "Registrujem korisnika..." : "Potvrdi registraciju"}
                    </button>
                  </div>
                </form>

                <p className="register-auth-switch">
                  Već imate nalog? <Link to="/login">Prijavite se</Link>
                </p>
              </div>
            </div>
          </section>
        </main>
      </div>
    </PageTransition>
  );
};

export default Register;
