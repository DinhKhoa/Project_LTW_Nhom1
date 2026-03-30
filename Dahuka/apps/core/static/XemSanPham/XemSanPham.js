document.addEventListener("DOMContentLoaded", () => {
  const products = document.querySelectorAll('.catalog-card');

  products.forEach((product) => {
    const visual = product.querySelector('.product-silhouette');
    const title = product.querySelector('h3');

    product.addEventListener("mouseenter", () => {
      if (visual) visual.style.transform = "translateY(-5px)";
      if (title) {
        title.style.transform = "translateY(-3px)";
        title.style.fontWeight = "bold";
      }
    });

    product.addEventListener("mouseleave", () => {
      if (visual) visual.style.transform = "translateY(0)";
      if (title) {
        title.style.transform = "translateY(0)";
        title.style.fontWeight = "500";
      }
    });
  });

  const filterBoxes = document.querySelectorAll(
    ".rectangle-2, .rectangle-3, .rectangle-4, .rectangle-5"
  );

  filterBoxes.forEach((box) => {
    box.style.cursor = "pointer";
    box.style.display = "flex";
    box.style.justifyContent = "center";
    box.style.alignItems = "center";

    box.addEventListener("click", () => {
      if (box.innerHTML === "") {
        box.innerHTML = '<span style="color: #0B6E4F; font-weight: bold;">✓</span>';
      } else {
        box.innerHTML = "";
      }
    });
  });

  const dropdownContainer = document.querySelector(".dropdown");
  const dropdownBtn = dropdownContainer.querySelector(".button");
  const currentLabel = dropdownBtn.querySelector(".label");

  // Tạo menu dropdown
  const menu = document.createElement("div");
  menu.className = "custom-dropdown-menu";
  menu.innerHTML = `
    <div class="menu-item">Mới nhất</div>
    <div class="menu-item">Bán chạy</div>
    <div class="menu-item">Giá từ thấp đến cao</div>
    <div class="menu-item">Giá từ cao đến thấp</div>
  `;
  dropdownContainer.appendChild(menu);

  // Mở/đóng menu khi nhấn nút
  dropdownBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    menu.classList.toggle("show");
  });

  // Hover và Click chọn option
  menu.querySelectorAll(".menu-item").forEach((item) => {
    item.addEventListener("mouseenter", () => {
      item.style.color = "#00bb66e4"; // Màu xanh như hình
      item.style.fontWeight = "bold";
    });
    item.addEventListener("mouseleave", () => {
      item.style.color = "#000000";
      item.style.fontWeight = "normal";
    });
    item.addEventListener("click", () => {
      currentLabel.innerText = item.innerText; // Đổi text nút chính
      menu.classList.remove("show");
    });
  });

  // Đóng menu nếu click ra ngoài
  window.addEventListener("click", () => {
    menu.classList.remove("show");
  });
});
