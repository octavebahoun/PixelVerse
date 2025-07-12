// Fonction asynchrone pour envoyer un "like" au serveur proposer par kevin
// et mettre à jour le compteur d'un clic sur une image.

async function likeImage(imageName) {
  try {
    const response = await fetch(`/like/${encodeURIComponent(imageName)}`, {
      method: "POST", // méthode POST pour signaler un like
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Récupération de la réponse JSON du serveur
    const data = await response.json();

    if (data.success) {
      // Sélectionne le span qui affiche le nombre de likes
      const span = document.getElementById(
        `like-count-${CSS.escape(imageName)}`
      );
      if (span) {
        // Incrémente le compteur affiché
        span.textContent = parseInt(span.textContent) + 1;
      }

      // Désactive le bouton like pour éviter les multiples clics
      const btn = document.querySelector(`button[data-image="${imageName}"]`);
      if (btn) {
        btn.disabled = true;
        btn.textContent = "Liked ✓";
      }
    } else if (data.error) {
      // Affiche un message d'erreur si serveur renvoie une erreur
      alert(data.error);
    }
  } catch (err) {
    // En cas d'erreur réseau ou autre, on log l'erreur et affiche une alerte
    console.error(err);
    alert("Erreur lors de l'envoi du like.");
  }
}

// --- Animation fade-in des sections au scroll ---
document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll("section");

  const observerOptions = {
    root: null,
    rootMargin: "0px",
    threshold: 0.15,
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("fade-in");
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  sections.forEach((section) => {
    section.classList.add("fade-out");
    observer.observe(section);
  });
});

// --- Bouton "Back to Top" ---
const backToTopBtn = document.createElement("button");
backToTopBtn.textContent = "⬆️";
backToTopBtn.id = "backToTop";
document.body.appendChild(backToTopBtn);

Object.assign(backToTopBtn.style, {
  position: "fixed",
  bottom: "30px",
  right: "30px",
  padding: "0.5rem 1rem",
  fontSize: "1.5rem",
  border: "none",
  borderRadius: "5px",
  backgroundColor: "blueviolet",
  color: "white",
  cursor: "pointer",
  display: "none",
  zIndex: "1000",
});

window.addEventListener("scroll", () => {
  if (window.scrollY > 300) {
    backToTopBtn.style.display = "block";
  } else {
    backToTopBtn.style.display = "none";
  }
});

backToTopBtn.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// --- Effet visuel sur les liens du footer au clic ---
const footerLinks = document.querySelectorAll("footer a");

footerLinks.forEach((link) => {
  link.addEventListener("click", () => {
    link.classList.add("clicked");
    setTimeout(() => {
      link.classList.remove("clicked");
    }, 300);
  });
});

// --- Menu déroulant (dropdown) ---
document.querySelector(".dropbtn").addEventListener("click", () => {
  document.querySelector(".dropdown-content").classList.toggle("show");
});

window.addEventListener("click", (e) => {
  if (!e.target.matches(".dropbtn")) {
    document.querySelectorAll(".dropdown-content").forEach((dd) => {
      dd.classList.remove("show");
    });
  }
});

// Fonction pour créer le HTML d’une image + boutons
function createGalleryItem(image, likes) {
  const div = document.createElement("div");
  div.classList.add("gallery-item");

  const img = document.createElement("img");
  img.src = `/static/images/${image}`;
  img.alt = image;

  const likeSection = document.createElement("div");
  likeSection.classList.add("like-section");

  // Bouton téléchargement
  const downloadLink = document.createElement("a");
  downloadLink.href = `/static/images/${image}`;
  downloadLink.setAttribute("download", "");
  downloadLink.classList.add("download-btn");
  downloadLink.title = "Télécharger l'image";
  downloadLink.textContent = "⬇️";

  // Bouton like
  const likeBtn = document.createElement("button");
  likeBtn.setAttribute("aria-label", "Like");
  likeBtn.textContent = "❤️";
  likeBtn.setAttribute("data-image", image); // important pour désactivation bouton après like
  likeBtn.onclick = () => likeImage(image);

  // Compteur de likes
  const likeCountSpan = document.createElement("span");
  likeCountSpan.id = `like-count-${image}`;
  likeCountSpan.textContent = likes;

  // Texte likes
  const likesText = document.createTextNode(" likes");

  // Ajout des éléments dans likeSection
  likeSection.appendChild(downloadLink);
  likeSection.appendChild(likeBtn);
  likeSection.appendChild(likeCountSpan);
  likeSection.appendChild(likesText);

  // Assemblage final
  div.appendChild(img);
  div.appendChild(likeSection);

  return div;
}
function likeImage(imageName) {
  fetch("/like", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ image_name: imageName, action: "like" }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        document.getElementById("like-count-" + imageName).innerText =
          data.like_count;
      } else {
        alert(data.message);
      }
    })
    .catch((error) => console.error("Erreur :", error));
}

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
