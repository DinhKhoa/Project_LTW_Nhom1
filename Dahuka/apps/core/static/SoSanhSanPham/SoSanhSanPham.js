document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".compare-product-card").forEach((card) => {
    const visual = card.querySelector(".product-silhouette");
    card.addEventListener("mouseenter", () => {
      if (visual) visual.style.transform = "translateY(-4px)";
    });
    card.addEventListener("mouseleave", () => {
      if (visual) visual.style.transform = "translateY(0)";
    });
  });
});
