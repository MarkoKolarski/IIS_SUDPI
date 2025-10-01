import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const isAuthenticated = sessionStorage.getItem("access_token");
  const userType = sessionStorage.getItem("user_type");

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(userType)) {
    // Redirect to the appropriate dashboard based on user type
    const dashboardMap = {
      logisticki_koordinator: "/dashboard-lk",
      skladisni_operater: "/dashboard-so",
      nabavni_menadzer: "/dashboard-nm",
      finansijski_analiticar: "/dashboard-fa",
      kontrolor_kvaliteta: "/dashboard-kk",
      administrator: "/dashboard-admin",
    };

    return <Navigate to={dashboardMap[userType] || "/login"} replace />;
  }

  return children;
};

export default ProtectedRoute;
