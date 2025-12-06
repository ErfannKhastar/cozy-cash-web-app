/**
 * @file auth.js
 * @description Handles user authentication logic including Login and Registration.
 * Manages API communication for authentication and local storage of JWT tokens.
 */

// Base URL of your FastAPI backend
const API_BASE_URL = "api/v1";

document.addEventListener("DOMContentLoaded", () => {
  // === LOGIN LOGIC ===
  const loginForm = document.getElementById("loginForm");

  /**
   * Handles the Login form submission.
   * Sends credentials using 'application/x-www-form-urlencoded' format
   * as required by OAuth2PasswordRequestForm in FastAPI.
   */
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("loginEmail").value;
      const password = document.getElementById("loginPassword").value;

      try {
        // NOTE: OAuth2 expects form data, not JSON.
        const formData = new URLSearchParams();
        formData.append("username", email); // Field must be 'username'
        formData.append("password", password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded", // هدر مخصوص فرم
          },
          body: formData, // ارسال دیتا به صورت فرم، نه JSON
        });

        const data = await response.json();

        if (response.ok) {
          console.log("Login Successful:", data);

          // Store JWT token and type
          localStorage.setItem("accessToken", data.access_token);
          localStorage.setItem("tokenType", data.token_type);

          // Redirect to Dashboard
          window.location.href = "/dashboard";
        } else {
          console.error("Login Failed:", data);
          alert(`Login Failed: ${data.detail || "Invalid credentials"}`);
        }
      } catch (error) {
        console.error("Network Error:", error);
        alert("Could not connect to the server. Is backend running?");
      }
    });
  }

  // === REGISTER LOGIC ===
  const registerForm = document.getElementById("registerForm");

  if (registerForm) {
    /**
     * Handles the Registration form submission.
     * Sends user data as JSON to create a new account.
     */
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("registerEmail").value;
      const password = document.getElementById("registerPassword").value;
      const confirmPassword = document.getElementById("confirmPassword").value;

      if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/users/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            password: password,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          alert("Registration successful! Please log in.");
          // Automatically switch to Login tab
          const loginTab = new bootstrap.Tab(
            document.querySelector("#login-tab")
          );
          loginTab.show();
        } else {
          alert(`Registration Failed: ${data.detail || "Error"}`);
        }
      } catch (error) {
        console.error("Error:", error);
        alert("Network error.");
      }
    });
  }
});
