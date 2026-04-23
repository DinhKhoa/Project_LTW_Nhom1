# Dahuka Project Structure

## 📂 Comprehensive Folder Tree
```text
Dahuka/
│
├── apps/                            # Django Applications (Logical Modules)
│   ├── account/                     # User Profiles, Authentication & Addresses
│   │   ├── migrations/              # DB Schema history
│   │   ├── api_views.py             # REST API endpoints for profile
│   │   ├── forms.py                 # Registration & profile forms
│   │   ├── models.py                # Customer & Address models
│   │   ├── urls.py                  # Account-specific routing
│   │   ├── views.py                 # Account management logic
│   │   └── templates/account/       # profile.html, address_list.html, etc.
│   │
│   ├── cart/                        # Shopping Cart Management
│   │   ├── apps.py                  # CartConfig initialization
│   │   ├── services.py              # Logic for adding/removing items
│   │   └── urls.py                  # /cart/ routing
│   │
│   ├── categories/                  # Product Categorization & Hierarchy
│   │   ├── apps.py                  # CategoriesConfig initialization
│   │   ├── models.py                # Category model (name, slug, image)
│   │   └── templates/categories/    # category_list.html, etc.
│   │
│   ├── core/                        # Public Website Logic & Catalog
│   │   ├── context_processors.py    # Global data (notification counts)
│   │   ├── urls.py                  # /catalog/, /comparison/ routing
│   │   ├── views.py                 # Home & public product list views
│   │   └── templates/core/          # home.html, view_products.html, etc.
│   │
│   ├── orders/                      # Order Processing & Management
│   │   ├── apps.py                  # OrdersConfig initialization
│   │   ├── models.py                # Order & OrderItem models
│   │   ├── services.py              # Order fulfillment logic
│   │   ├── urls.py                  # /orders/ routing
│   │   └── templates/orders/        # order_list.html, detail.html
│   │
│   ├── products/                    # Product Management & Inventory
│   │   ├── apps.py                  # ProductsConfig initialization
│   │   ├── models.py                # Product model (English fields)
│   │   ├── services.py              # Inventory & visibility logic
│   │   ├── static/                  # list_products.css, product_detail.css
│   │   ├── urls.py                  # /products/ (Admin) routing
│   │   └── templates/products/      # product_list.html, detail.html
│   │
│   ├── promotions/                  # Discounts & Marketing
│   │   ├── apps.py                  # PromotionsConfig initialization
│   │   ├── forms.py                 # PromotionsModelForm (Refactored)
│   │   ├── models.py                # Promotion model
│   │   └── templates/promotions/    # promotion_list.html, add_promotion.html
│   │
│   ├── tasks/                       # Technical/Installation Tasks
│   │   ├── apps.py                  # TasksConfig initialization
│   │   ├── models.py                # InstallationTask model
│   │   ├── static/tasks/            # task_installation.css, task_detail.css
│   │   └── templates/tasks/         # task_list.html, task_detail.html
│   │
│   └── warranty/                    # Service Centers & Warranty
│       ├── apps.py                  # WarrantyConfig initialization
│       ├── static/warranty/         # warranty.css, etc.
│       └── templates/warranty/      # warranty_list.html
│
├── Dahuka/                          # Project-level Configuration
│   ├── settings.py                  # Main project settings
│   ├── urls.py                      # Root URL routing (Entry point)
│   ├── asgi.py                      # Async server gateway
│   └── wsgi.py                      # Production server gateway
│
├── static/                          # Global Static Assets
│   ├── css/                         # dahuka.css (CSS Design System)
│   ├── img/                         # Logos, mascots, banners, UI assets
│   ├── orders/css/                  # Legacy donhang.css
│   └── vendor/                      # Third-party (Bootstrap, FontAwesome)
│
├── templates/                       # Layout & Registration Templates
│   ├── base.html                    # Main layout skeleton
│   └── registration/                # login.html, signin.html, etc.
│
├── media/                           # User-uploaded files (Local storage)
│   └── products/                    # Stored product images
│
├── artifacts/                       # Analysis & documentation artifacts
├── manage.py                        # Django CLI entry point
├── db.sqlite3                       # Local SQL Database
└── STRUCTURE.md                     # Current file (Project Map)
```
