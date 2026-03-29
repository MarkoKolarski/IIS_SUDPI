import React, { useEffect, useMemo, useState } from "react";
import MainSideBar from "../components/MainSideBar";
import "../styles/EditProfile.css";
import axiosInstance from "../axiosInstance";
import PageTransition from "../components/PageTransition";

const INITIAL_PASSWORD_DATA = {
  password: "",
  password_confirm: "",
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

const normalizePersonalData = (data = {}) => ({
  ime_k: (data.ime_k || "").trim(),
  prz_k: (data.prz_k || "").trim(),
  mail_k: (data.mail_k || "").trim().toLowerCase(),
});

const mapRoleLabel = (tipK) => {
  const roleMap = {
    logisticki_koordinator: "Logistički koordinator",
    skladisni_operater: "Skladišni operater",
    nabavni_menadzer: "Nabavni menadžer",
    finansijski_analiticar: "Finansijski analitičar",
    kontrolor_kvaliteta: "Kontrolor kvaliteta",
    administrator: "Administrator",
  };

  return roleMap[tipK] || "";
};

const extractBackendErrorPayload = (responseData, allowedFields = []) => {
  const fieldErrors = {};

  if (responseData && typeof responseData === "object") {
    Object.entries(responseData).forEach(([fieldName, value]) => {
      if (!allowedFields.includes(fieldName)) {
        return;
      }

      const normalized = normalizeErrorText(value);
      if (normalized) {
        fieldErrors[fieldName] = normalized;
      }
    });
  }

  const generalMessage =
    normalizeErrorText(responseData?.detail) ||
    normalizeErrorText(responseData?.error) ||
    normalizeErrorText(responseData?.non_field_errors) ||
    normalizeErrorText(responseData?.details);

  return { fieldErrors, generalMessage };
};

const EditProfile = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [personalData, setPersonalData] = useState({
    ime_k: "",
    prz_k: "",
    mail_k: "",
  });
  const [initialPersonalData, setInitialPersonalData] = useState(null);
  const [userRole, setUserRole] = useState("");
  const [passwordData, setPasswordData] = useState(INITIAL_PASSWORD_DATA);
  const [loading, setLoading] = useState({
    personal: false,
    password: false,
  });
  const [initialLoading, setInitialLoading] = useState(true);
  const [message, setMessage] = useState({ type: "", text: "" });
  const [errors, setErrors] = useState({});

  const normalizedPersonalData = useMemo(
    () => normalizePersonalData(personalData),
    [personalData],
  );

  const normalizedInitialPersonalData = useMemo(
    () => normalizePersonalData(initialPersonalData || {}),
    [initialPersonalData],
  );

  const hasPersonalChanges = useMemo(() => {
    if (!initialPersonalData) {
      return false;
    }

    return (
      normalizedPersonalData.ime_k !== normalizedInitialPersonalData.ime_k ||
      normalizedPersonalData.prz_k !== normalizedInitialPersonalData.prz_k ||
      normalizedPersonalData.mail_k !== normalizedInitialPersonalData.mail_k
    );
  }, [initialPersonalData, normalizedInitialPersonalData, normalizedPersonalData]);

  const hasUnsavedChanges = hasPersonalChanges || Boolean(passwordData.password || passwordData.password_confirm);

  const getFieldError = (fieldName) => normalizeErrorText(errors[fieldName]);

  const clearFieldError = (fieldName) => {
    setErrors((prev) => ({ ...prev, [fieldName]: "" }));
  };

  const clearMultipleFieldErrors = (fieldNames) => {
    setErrors((prev) => {
      const nextErrors = { ...prev };
      fieldNames.forEach((fieldName) => {
        nextErrors[fieldName] = "";
      });
      return nextErrors;
    });
  };

  const validatePersonalData = () => {
    const validationErrors = {};
    const namePattern = /^[A-Za-zČĆŽŠĐčćžšđ\s'-]{2,}$/;
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!normalizedPersonalData.ime_k) {
      validationErrors.ime_k = "Ime je obavezno.";
    } else if (!namePattern.test(normalizedPersonalData.ime_k)) {
      validationErrors.ime_k = "Ime mora imati najmanje 2 karaktera i sadržati samo slova.";
    }

    if (!normalizedPersonalData.prz_k) {
      validationErrors.prz_k = "Prezime je obavezno.";
    } else if (!namePattern.test(normalizedPersonalData.prz_k)) {
      validationErrors.prz_k = "Prezime mora imati najmanje 2 karaktera i sadržati samo slova.";
    }

    if (!normalizedPersonalData.mail_k) {
      validationErrors.mail_k = "Email adresa je obavezna.";
    } else if (!emailPattern.test(normalizedPersonalData.mail_k)) {
      validationErrors.mail_k = "Unesite ispravnu email adresu.";
    }

    return validationErrors;
  };

  const validatePasswordData = () => {
    const validationErrors = {};

    if (!passwordData.password) {
      validationErrors.password = "Nova lozinka je obavezna.";
    } else if (passwordData.password.length < 8) {
      validationErrors.password = "Lozinka mora imati najmanje 8 karaktera.";
    } else if (/^\d+$/.test(passwordData.password)) {
      validationErrors.password = "Lozinka ne može biti samo numerička.";
    }

    if (!passwordData.password_confirm) {
      validationErrors.password_confirm = "Ponovljena lozinka je obavezna.";
    } else if (passwordData.password !== passwordData.password_confirm) {
      validationErrors.password_confirm = "Lozinke se ne poklapaju.";
    }

    return validationErrors;
  };

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setInitialLoading(true);
        const response = await axiosInstance.get("/api/user/profile/");
        const userData = response.data || {};

        const fetchedPersonalData = {
          ime_k: userData.ime_k || "",
          prz_k: userData.prz_k || "",
          mail_k: userData.mail_k || "",
        };

        setPersonalData(fetchedPersonalData);
        setInitialPersonalData(fetchedPersonalData);
        setUserRole(userData.tip_k_display || mapRoleLabel(userData.tip_k));
      } catch (err) {
        console.error("Error fetching user data:", err);
        setMessage({
          type: "error",
          text: "Greška pri učitavanju podataka korisnika.",
        });
      } finally {
        setInitialLoading(false);
      }
    };

    fetchUserData();
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed((prev) => !prev);
  };

  const handlePersonalChange = (e) => {
    const { name, value } = e.target;
    setPersonalData((prevState) => ({
      ...prevState,
      [name]: value,
    }));

    clearFieldError(name);

    if (message.text) {
      setMessage({ type: "", text: "" });
    }
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prevState) => ({
      ...prevState,
      [name]: value,
    }));

    clearFieldError(name);

    if (message.text) {
      setMessage({ type: "", text: "" });
    }
  };

  const handlePersonalSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = validatePersonalData();
    if (Object.keys(validationErrors).length > 0) {
      setErrors((prev) => ({ ...prev, ...validationErrors }));
      setMessage({ type: "error", text: "Ispravite označena polja i pokušajte ponovo." });
      return;
    }

    if (!hasPersonalChanges) {
      setMessage({ type: "info", text: "Nema izmena za čuvanje." });
      return;
    }

    setLoading((prev) => ({ ...prev, personal: true }));
    setMessage({ type: "", text: "" });
    clearMultipleFieldErrors(["ime_k", "prz_k", "mail_k"]);

    try {
      await axiosInstance.put("/api/user/profile/update/", {
        ...normalizedPersonalData,
        password: "",
        password_confirm: "",
      });

      const savedPersonalData = {
        ime_k: normalizedPersonalData.ime_k,
        prz_k: normalizedPersonalData.prz_k,
        mail_k: normalizedPersonalData.mail_k,
      };

      setPersonalData(savedPersonalData);
      setInitialPersonalData(savedPersonalData);
      setMessage({
        type: "success",
        text: "Lični podaci su uspešno ažurirani.",
      });
    } catch (err) {
      console.error("Error updating personal data:", err);

      const responseData = err.response?.data;
      const { fieldErrors, generalMessage } = extractBackendErrorPayload(responseData, [
        "ime_k",
        "prz_k",
        "mail_k",
      ]);

      setErrors((prev) => ({ ...prev, ...fieldErrors }));
      setMessage({
        type: "error",
        text:
          generalMessage ||
          (Object.keys(fieldErrors).length > 0
            ? "Ažuriranje nije uspelo. Proverite unete podatke."
            : "Greška pri ažuriranju ličnih podataka."),
      });
    } finally {
      setLoading((prev) => ({ ...prev, personal: false }));
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = validatePasswordData();
    if (Object.keys(validationErrors).length > 0) {
      setErrors((prev) => ({ ...prev, ...validationErrors }));
      setMessage({ type: "error", text: "Ispravite polja za lozinku i pokušajte ponovo." });
      return;
    }

    setLoading((prev) => ({ ...prev, password: true }));
    setMessage({ type: "", text: "" });
    clearMultipleFieldErrors(["password", "password_confirm"]);

    try {
      await axiosInstance.put("/api/user/profile/update/", {
        ...normalizedPersonalData,
        password: passwordData.password,
        password_confirm: passwordData.password_confirm,
      });

      setMessage({
        type: "success",
        text: "Lozinka je uspešno promenjena.",
      });

      setPasswordData(INITIAL_PASSWORD_DATA);
    } catch (err) {
      console.error("Error updating password:", err);

      const responseData = err.response?.data;
      const { fieldErrors, generalMessage } = extractBackendErrorPayload(responseData, [
        "password",
        "password_confirm",
      ]);

      setErrors((prev) => ({ ...prev, ...fieldErrors }));
      setMessage({
        type: "error",
        text:
          generalMessage ||
          normalizeErrorText(responseData?.password_confirm) ||
          "Greška pri promeni lozinke.",
      });
    } finally {
      setLoading((prev) => ({ ...prev, password: false }));
    }
  };

  const handleCancel = () => {
    if (hasUnsavedChanges) {
      const shouldLeave = window.confirm(
        "Imate nesačuvane izmene. Da li ste sigurni da želite da napustite ovu stranicu?",
      );

      if (!shouldLeave) {
        return;
      }
    }

    window.history.back();
  };

  if (initialLoading) {
    return (
      <PageTransition>
        <div className={`edit-profile-wrapper ${isSidebarCollapsed ? "sidebar-collapsed" : ""}`}>
          <MainSideBar
            isCollapsed={isSidebarCollapsed}
            toggleSidebar={toggleSidebar}
          />

          <main className="edit-profile-main">
            <header className="edit-profile-header">
              <h1>Izmena profila</h1>
            </header>

            <div className="edit-profile-content">
              <div className="edit-profile-loading-card">
                <div className="edit-profile-loading-message">Učitavanje podataka...</div>
              </div>
            </div>
          </main>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className={`edit-profile-wrapper ${isSidebarCollapsed ? "sidebar-collapsed" : ""}`}>
        <MainSideBar
          isCollapsed={isSidebarCollapsed}
          toggleSidebar={toggleSidebar}
          activePage="edit_profile"
        />

        <main className="edit-profile-main">
          <header className="edit-profile-header">
            <h1>Izmena profila</h1>
            <p>Ažurirajte lične podatke i sigurnosne postavke naloga.</p>
          </header>

          <div className="edit-profile-content">
            <div className="edit-profile-card">
              <div className="edit-profile-card-header">
                <h2>Korisnički profil</h2>
              </div>

              <div className="edit-profile-card-body">
                {message.text && (
                  <div
                    className={`edit-profile-message ${message.type}`}
                    role={message.type === "error" ? "alert" : "status"}
                    aria-live="polite"
                  >
                    {message.text}
                  </div>
                )}

                <div className="edit-profile-form-layout">
                  <section className={`edit-profile-section ${loading.personal ? "edit-profile-section-loading" : ""}`}>
                    <div className="edit-profile-section-header">
                      <h3>Osnovni podaci</h3>
                    </div>

                    <form onSubmit={handlePersonalSubmit} noValidate>
                      <div className="edit-profile-form-group">
                        <label htmlFor="ime_k" className="edit-profile-form-label">
                          Ime
                        </label>
                        <input
                          type="text"
                          id="ime_k"
                          name="ime_k"
                          className={`edit-profile-form-control ${
                            getFieldError("ime_k") ? "is-invalid" : ""
                          }`}
                          value={personalData.ime_k}
                          onChange={handlePersonalChange}
                          autoComplete="given-name"
                          placeholder="Unesite ime"
                          required
                        />
                        {getFieldError("ime_k") && (
                          <p className="edit-profile-error-message">{getFieldError("ime_k")}</p>
                        )}
                      </div>

                      <div className="edit-profile-form-group">
                        <label htmlFor="prz_k" className="edit-profile-form-label">
                          Prezime
                        </label>
                        <input
                          type="text"
                          id="prz_k"
                          name="prz_k"
                          className={`edit-profile-form-control ${
                            getFieldError("prz_k") ? "is-invalid" : ""
                          }`}
                          value={personalData.prz_k}
                          onChange={handlePersonalChange}
                          autoComplete="family-name"
                          placeholder="Unesite prezime"
                          required
                        />
                        {getFieldError("prz_k") && (
                          <p className="edit-profile-error-message">{getFieldError("prz_k")}</p>
                        )}
                      </div>

                      <div className="edit-profile-form-group">
                        <label htmlFor="mail_k" className="edit-profile-form-label">
                          Email adresa
                        </label>
                        <input
                          type="email"
                          id="mail_k"
                          name="mail_k"
                          className={`edit-profile-form-control ${
                            getFieldError("mail_k") ? "is-invalid" : ""
                          }`}
                          value={personalData.mail_k}
                          onChange={handlePersonalChange}
                          autoComplete="email"
                          placeholder="Unesite email adresu"
                          required
                        />
                        {getFieldError("mail_k") && (
                          <p className="edit-profile-error-message">{getFieldError("mail_k")}</p>
                        )}
                      </div>

                      <div className="edit-profile-form-group">
                        <label htmlFor="role_display" className="edit-profile-form-label">
                          Uloga
                        </label>
                        <input
                          type="text"
                          id="role_display"
                          className="edit-profile-form-control edit-profile-form-control-readonly"
                          value={userRole || "Nije dostupno"}
                          readOnly
                          disabled
                        />
                      </div>

                      <div className="edit-profile-button-section">
                        <button
                          type="submit"
                          className="edit-profile-btn edit-profile-btn-primary"
                          disabled={loading.personal || !hasPersonalChanges}
                        >
                          {loading.personal ? "Čuvanje..." : "Sačuvaj izmene"}
                        </button>
                      </div>
                    </form>
                  </section>

                  <section className={`edit-profile-section ${loading.password ? "edit-profile-section-loading" : ""}`}>
                    <div className="edit-profile-section-header">
                      <h3>Promena lozinke</h3>
                    </div>

                    <form onSubmit={handlePasswordSubmit} noValidate>
                      <div className="edit-profile-password-group">
                        <label htmlFor="password" className="edit-profile-form-label">
                          Nova lozinka
                        </label>
                        <input
                          id="password"
                          type="password"
                          name="password"
                          className={`edit-profile-form-control ${
                            getFieldError("password") ? "is-invalid" : ""
                          }`}
                          value={passwordData.password}
                          onChange={handlePasswordChange}
                          autoComplete="new-password"
                          placeholder="Unesite novu lozinku"
                        />
                        <p className="edit-profile-password-hint">
                          Lozinka treba da ima najmanje 8 karaktera i ne sme biti samo numerička.
                        </p>
                        {getFieldError("password") && (
                          <p className="edit-profile-error-message">{getFieldError("password")}</p>
                        )}
                      </div>

                      <div className="edit-profile-password-group">
                        <label htmlFor="password_confirm" className="edit-profile-form-label">
                          Potvrdite novu lozinku
                        </label>
                        <input
                          id="password_confirm"
                          type="password"
                          name="password_confirm"
                          className={`edit-profile-form-control ${
                            getFieldError("password_confirm") ? "is-invalid" : ""
                          }`}
                          value={passwordData.password_confirm}
                          onChange={handlePasswordChange}
                          autoComplete="new-password"
                          placeholder="Ponovite novu lozinku"
                        />
                        {getFieldError("password_confirm") && (
                          <p className="edit-profile-error-message">
                            {getFieldError("password_confirm")}
                          </p>
                        )}
                      </div>

                      <div className="edit-profile-button-section">
                        <button
                          type="submit"
                          className="edit-profile-btn edit-profile-btn-primary"
                          disabled={loading.password}
                        >
                          {loading.password ? "Čuvanje..." : "Promeni lozinku"}
                        </button>
                      </div>
                    </form>
                  </section>
                </div>

                <div className="edit-profile-global-actions">
                  <button
                    type="button"
                    className="edit-profile-btn edit-profile-btn-secondary"
                    onClick={handleCancel}
                  >
                    Odustani
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </PageTransition>
  );
};

export default EditProfile;