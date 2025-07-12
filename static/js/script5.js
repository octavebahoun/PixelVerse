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

  // Scroll to top button
  const scrollBtn = document.getElementById("scrollBtn");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
      scrollBtn.style.display = "block";
    } else {
      scrollBtn.style.display = "none";
    }
  });

  scrollBtn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
});
