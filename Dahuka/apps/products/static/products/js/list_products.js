document.addEventListener("DOMContentLoaded", () => {
  // 1. Hiệu ứng Hover cho thẻ sản phẩm (Catalog Card)
  const products = document.querySelectorAll('.catalog-card');

  products.forEach((product) => {
    const visual = product.querySelector('.product-silhouette'); // Hình ảnh/Khối màu sản phẩm
    const title = product.querySelector('h3'); // Tên sản phẩm

    // Khi di chuột vào: Nhấc sản phẩm lên và làm đậm tiêu đề
    product.addEventListener("mouseenter", () => {
      if (visual) visual.style.transform = "translateY(-5px)";
      if (title) {
        title.style.transform = "translateY(-3px)";
        title.style.fontWeight = "bold";
      }
    });

    // Khi di chuột ra: Trả về vị trí cũ
    product.addEventListener("mouseleave", () => {
      if (visual) visual.style.transform = "translateY(0)";
      if (title) {
        title.style.transform = "translateY(0)";
        title.style.fontWeight = "500";
      }
    });
  });

  // 2. Giả lập checkbox cho bộ lọc Sidebar (Click để hiện dấu ✓)
  const filterBoxes = document.querySelectorAll(
    ".rectangle-2, .rectangle-3, .rectangle-4, .rectangle-5"
  );

  filterBoxes.forEach((box) => {
    box.style.cursor = "pointer";
    box.style.display = "flex";
    box.style.justifyContent = "center";
    box.style.alignItems = "center";

    box.addEventListener("click", () => {
      // Toggle: Nếu trống thì thêm dấu tích, nếu có rồi thì xóa
      if (box.innerHTML === "") {
        box.innerHTML = '<span style="color: #0B6E4F; font-weight: bold;">✓</span>';
      } else {
        box.innerHTML = "";
      }
    });
  });

  // 3. Xử lý Dropdown Sắp xếp (Sort) tùy chỉnh
  const dropdownContainer = document.querySelector(".dropdown");
  const dropdownBtn = dropdownContainer.querySelector(".button");
  const currentLabel = dropdownBtn.querySelector(".label");

  // Tự tạo một menu menu ẩn bên dưới nút dropdown
  const menu = document.createElement("div");
  menu.className = "custom-dropdown-menu";
  menu.innerHTML = `
    <div class="menu-item">Mới nhất</div>
    <div class="menu-item">Bán chạy</div>
    <div class="menu-item">Giá từ thấp đến cao</div>
    <div class="menu-item">Giá từ cao đến thấp</div>
  `;
  dropdownContainer.appendChild(menu);

  // Nhấn nút để Hiện/Ẩn danh sách lựa chọn
  dropdownBtn.addEventListener("click", (e) => {
    e.stopPropagation(); // Tránh sự kiện click lan ra ngoài làm menu bị đóng ngay lập tức
    menu.classList.toggle("show");
  });

  // Xử lý khi nhấn chọn một phương thức sắp xếp
  menu.querySelectorAll(".menu-item").forEach((item) => {
    item.addEventListener("mouseenter", () => {
      item.style.color = "#00bb66e4"; 
      item.style.fontWeight = "bold";
    });
    item.addEventListener("mouseleave", () => {
      item.style.color = "#000000";
      item.style.fontWeight = "normal";
    });
    item.addEventListener("click", () => {
      currentLabel.innerText = item.innerText; // Đổi tên hiển thị trên nút chính
      menu.classList.remove("show"); // Đóng menu
    });
  });

  // Đóng menu tự động nếu người dùng click vào bất cứ đâu bên ngoài
  window.addEventListener("click", () => {
    menu.classList.remove("show");
  });
});
