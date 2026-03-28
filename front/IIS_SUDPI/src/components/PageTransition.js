import React from "react";
import styles from "../styles/PageTransition.module.css";

const PageTransition = ({ children }) => {
  return <div className={styles.pageTransition}>{children}</div>;
};

export default PageTransition;