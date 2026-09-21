import React from "react";
import ReactDOM from "react-dom/client";
import "./styles/theme.css";
import "./index.css";
import "./styles/redesign.css";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import "./styles/violet-dark-final.css";

import { ThemeProvider } from "./context/ThemeContext";

ReactDOM.createRoot(
  document.getElementById("root")
).render(
  <React.StrictMode>
    <ThemeProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>
);