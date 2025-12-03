// Base URL of your FastAPI backend
const API_BASE_URL = "";

document.addEventListener("DOMContentLoaded", () => {
  // === LOGIN LOGIC ===
  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("loginEmail").value;
      const password = document.getElementById("loginPassword").value;

      try {
        // نکته مهم: استفاده از URLSearchParams برای ارسال Form Data
        const formData = new URLSearchParams();
        formData.append("username", email); // OAuth2 همیشه دنبال 'username' می‌گردد حتی اگر ایمیل باشد
        formData.append("password", password);

        const response = await fetch(`${API_BASE_URL}api/v1/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded", // هدر مخصوص فرم
          },
          body: formData, // ارسال دیتا به صورت فرم، نه JSON
        });

        const data = await response.json();

        if (response.ok) {
          console.log("Login Successful:", data);

          // ذخیره توکن
          localStorage.setItem("accessToken", data.access_token);
          localStorage.setItem("tokenType", data.token_type);

          // ریدایرکت به داشبورد
          // اگر داشبورد را جدا اجرا می‌کنی (مثلا Live Server)، آدرس نسبی کار می‌کند
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
        // برای ثبت‌نام (Register) چون از Pydantic مدل استفاده کردی، همون JSON درسته
        const response = await fetch(`${API_BASE_URL}api/v1/users/`, {
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
          // سوییچ خودکار به تب لاگین
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
