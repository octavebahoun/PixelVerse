const form = document.querySelector("form");
const ageInput = document.getElementById("age");
const passwordInput = document.getElementById("password");
const submitBtn = document.querySelector('input[type="submit"]');

// Vérifie la force du mot de passe
function checkPasswordStrength(pwd) {
  // min 8 chars, au moins 1 majuscule, 1 minuscule et 1 chiffre
  return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(pwd);
}

form.addEventListener("submit", (e) => {
  e.preventDefault(); // bloque l'envoi pour validation

  const pwdVal = passwordInput.value;

  // Validation mot de passe
  if (!checkPasswordStrength(pwdVal)) {
    alert(
      "Mot de passe trop faible.\nMinimum 8 caractères, dont une majuscule, une minuscule et un chiffre."
    );
    passwordInput.focus();
    return;
  }

  // Confirmation avant envoi
  if (confirm("Confirmez-vous la soumission du formulaire ?")) {
    form.submit();
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const burger = document.getElementById("burger");
  const navLinks = document.getElementById("navLinks");
  const closeSidebar = document.getElementById("closeSidebar");

  burger.addEventListener("click", () => {
    navLinks.classList.toggle("show");
  });

  closeSidebar.addEventListener("click", () => {
    navLinks.classList.toggle("show");
  });
});
