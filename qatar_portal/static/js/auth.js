/* ─── Helpers ────────────────────────────────────────────────── */
function showError(msg) {
  const el = document.getElementById("error-msg");
  if (!el) return;
  el.textContent = msg;
  el.classList.remove("hidden");
}
function hideError() {
  const el = document.getElementById("error-msg");
  if (el) el.classList.add("hidden");
}
function showSuccess(msg) {
  const el = document.getElementById("success-msg");
  if (!el) return;
  el.textContent = msg;
  el.classList.remove("hidden");
}
function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  btn.textContent = loading ? "Please wait..." : btn.dataset.label || btn.textContent;
}

/* Store original button labels */
document.addEventListener("DOMContentLoaded", () => {
  ["signup-btn", "login-btn", "submit-btn", "reset-btn"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.dataset.label = el.textContent;
  });
});

/* ─── US-1.1  SIGN UP ────────────────────────────────────────── */
async function handleSignup() {
  hideError();
  setLoading("signup-btn", true);

  const payload = {
    full_name:        document.getElementById("full_name").value.trim(),
    email:            document.getElementById("email").value.trim(),
    password:         document.getElementById("password").value,
    confirm_password: document.getElementById("confirm_password").value
  };

  try {
    const res  = await fetch("/api/auth/signup", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      showSuccess("Account created! Redirecting to login...");
      setTimeout(() => { window.location.href = "/login"; }, 1200);
    } else {
      showError(data.error || "Signup failed. Please try again.");
    }
  } catch (err) {
    showError("Network error. Please check your connection.");
  } finally {
    setLoading("signup-btn", false);
  }
}

/* ─── US-1.2  LOGIN ──────────────────────────────────────────── */
async function handleLogin() {
  hideError();
  setLoading("login-btn", true);

  const payload = {
    email:       document.getElementById("email").value.trim(),
    password:    document.getElementById("password").value,
    remember_me: document.getElementById("remember_me")?.checked || false
  };

  try {
    const res  = await fetch("/api/auth/login", {
      method:      "POST",
      headers:     { "Content-Type": "application/json" },
      credentials: "include",
      body:        JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      window.location.href = "/dashboard";
    } else {
      showError(data.error || "Invalid email or password.");
    }
  } catch (err) {
    showError("Network error. Please check your connection.");
  } finally {
    setLoading("login-btn", false);
  }
}

/* ─── LOGOUT ─────────────────────────────────────────────────── */
async function handleLogout() {
  try {
    await fetch("/api/auth/logout", {
      method:      "POST",
      credentials: "include"
    });
  } catch (_) {}
  window.location.href = "/login";
}

/* ─── US-1.3  FORGOT PASSWORD ────────────────────────────────── */
async function handleForgotPassword() {
  hideError();
  setLoading("submit-btn", true);

  const email = document.getElementById("email")?.value.trim();

  try {
    const res  = await fetch("/api/auth/forgot-password", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ email })
    });
    const data = await res.json();

    if (data.success) {
      document.getElementById("email-group")?.classList.add("hidden");
      document.getElementById("submit-btn")?.classList.add("hidden");
      showSuccess(data.data.message);
    } else {
      showError(data.error || "Something went wrong.");
    }
  } catch (err) {
    showError("Network error. Please check your connection.");
  } finally {
    setLoading("submit-btn", false);
  }
}

/* ─── US-1.3  RESET PASSWORD ─────────────────────────────────── */
async function handleResetPassword() {
  hideError();
  setLoading("reset-btn", true);

  // Get token from URL query param
  const params = new URLSearchParams(window.location.search);
  const token  = params.get("token");

  if (!token) {
    showError("Invalid reset link. Please request a new one.");
    setLoading("reset-btn", false);
    return;
  }

  const payload = {
    token,
    password:         document.getElementById("password").value,
    confirm_password: document.getElementById("confirm_password").value
  };

  try {
    const res  = await fetch("/api/auth/reset-password", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      showSuccess("Password reset! Redirecting to login...");
      setTimeout(() => { window.location.href = "/login"; }, 1500);
    } else {
      showError(data.error || "Reset failed. Please try again.");
    }
  } catch (err) {
    showError("Network error. Please check your connection.");
  } finally {
    setLoading("reset-btn", false);
  }
}

/* ─── Allow Enter key to submit forms ────────────────────────── */
document.addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;
  if (document.getElementById("signup-btn"))  handleSignup();
  if (document.getElementById("login-btn"))   handleLogin();
  if (document.getElementById("submit-btn"))  handleForgotPassword();
  if (document.getElementById("reset-btn"))   handleResetPassword();
});
