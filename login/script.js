const form = document.getElementById("loginForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const emailError = document.getElementById("emailError");
const passwordError = document.getElementById("passwordError");
const formNote = document.getElementById("formNote");
const togglePassword = document.getElementById("togglePassword");
const submitBtn = document.getElementById("submitBtn");

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MIN_PASSWORD_LENGTH = 8;

function setFieldError(input, errorEl, message) {
  input.classList.toggle("invalid", Boolean(message));
  errorEl.textContent = message || "";
}

function validateEmail() {
  const value = emailInput.value.trim();

  if (!value) {
    setFieldError(emailInput, emailError, "Email or username is required.");
    return false;
  }

  if (value.includes("@") && !EMAIL_PATTERN.test(value)) {
    setFieldError(emailInput, emailError, "Enter a valid email address.");
    return false;
  }

  setFieldError(emailInput, emailError, "");
  return true;
}

function validatePassword() {
  const value = passwordInput.value;

  if (!value) {
    setFieldError(passwordInput, passwordError, "Password is required.");
    return false;
  }

  if (value.length < MIN_PASSWORD_LENGTH) {
    setFieldError(
      passwordInput,
      passwordError,
      `Password must be at least ${MIN_PASSWORD_LENGTH} characters.`,
    );
    return false;
  }

  setFieldError(passwordInput, passwordError, "");
  return true;
}

togglePassword.addEventListener("click", () => {
  const isHidden = passwordInput.type === "password";
  passwordInput.type = isHidden ? "text" : "password";
  togglePassword.textContent = isHidden ? "Hide" : "Show";
});

emailInput.addEventListener("blur", validateEmail);
passwordInput.addEventListener("blur", validatePassword);

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const isEmailValid = validateEmail();
  const isPasswordValid = validatePassword();

  formNote.classList.remove("success", "error");

  if (!isEmailValid || !isPasswordValid) {
    formNote.classList.add("error");
    formNote.textContent = "Please fix the errors above.";
    return;
  }

  submitBtn.disabled = true;
  formNote.textContent = "Signing in...";

  try {
    const response = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: emailInput.value.trim(),
        password: passwordInput.value,
      }),
    });

    const result = await response.json().catch(() => ({}));

    formNote.classList.remove("success", "error");
    if (response.ok && result.success) {
      formNote.classList.add("success");
      formNote.textContent = result.message || "Login successful.";
    } else {
      formNote.classList.add("error");
      formNote.textContent = result.message || "Invalid credentials.";
    }
  } catch (err) {
    formNote.classList.remove("success");
    formNote.classList.add("error");
    formNote.textContent = "Could not reach the server. Please try again.";
  } finally {
    submitBtn.disabled = false;
  }
});
