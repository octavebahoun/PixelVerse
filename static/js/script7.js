// Toggle menu burger
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
