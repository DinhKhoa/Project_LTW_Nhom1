# Dahuka Project Structure

## 📂 Comprehensive Folder Tree

```text
Dahuka/
│
├── .agents/                         # Agent-specific configurations
│   └── rules/                       # Project-specific AI rules
│       └── ruleforprojectdahuka.md  # Core development rules
│
├── apps/                            # Django Applications (Logical Modules)
│   ├── account/                     # User Profiles, Authentication & Addresses
│   │   ├── migrations/              # DB Schema history
│   │   ├── static/account/          # account-specific JS (cancel_order.js)
│   │   ├── templates/               # my_orders.html, my_order_detail.html, addresses.html, etc.
│   │   ├── admin.py                 # Admin registration for account models
│   │   ├── api_views.py             # REST API endpoints for profile
│   │   ├── apps.py                  # AccountConfig
│   │   ├── create_staff.py          # Script for creating staff users
│   │   ├── forms.py                 # Registration & profile forms
│   │   ├── models.py                # Customer & Address models
│   │   ├── selectors.py             # Business logic query selectors
│   │   ├── services.py              # Business logic services
│   │   ├── signals.py               # Post-save signals for user/customer
│   │   ├── tests.py                 # Unit tests for account
│   │   ├── urls.py                  # Account-specific routing
│   │   └── views.py                 # Account management logic
│   │
│   ├── cart/                        # Shopping Cart Management
│   │   ├── migrations/              # Cart migrations
│   │   ├── static/cart/             # cart.js, cart.css
│   │   ├── templates/cart/          # cart_detail.html
│   │   ├── templatetags/            # cart_tags.py (cart item count)
│   │   ├── admin.py                 # Admin registration
│   │   ├── apps.py                  # CartConfig
│   │   ├── context_processors.py    # Cart in global context
│   │   ├── forms.py                 # Cart item forms
│   │   ├── models.py                # Cart & CartItem models
│   │   ├── services.py              # Logic for adding/removing items
│   │   └── urls.py                  # /cart/ routing
│   │
│   ├── categories/                  # Product Categorization & Hierarchy
│   │   ├── migrations/              # Category migrations
│   │   ├── admin.py                 # Category admin
│   │   ├── apps.py                  # CategoriesConfig
│   │   ├── models.py                # Category model (name, slug, image)
│   │   ├── urls.py                  # Category routing
│   │   └── templates/categories/    # category_list.html
│   │
│   ├── core/                        # Public Website Logic & Catalog
│   │   ├── migrations/              # Core migrations
│   │   ├── context_processors.py    # Global data (notification counts)
│   │   ├── forms.py                 # Public-facing forms
│   │   ├── models.py                # Banner & public settings models
│   │   ├── selectors.py             # Public product selectors
│   │   ├── urls.py                  # /catalog/, /comparison/ routing
│   │   ├── views.py                 # Home & public product list views
│   │   └── templates/core/          # home.html, view_products.html, etc.
│   │
│   ├── orders/                      # Order Processing & Management
│   │   ├── migrations/              # Order migrations
│   │   ├── static/orders/           # orders.css, orders.js
│   │   ├── admin.py                 # Order admin
│   │   ├── apps.py                  # OrdersConfig
│   │   ├── models.py                # Order & OrderItem models
│   │   ├── selectors.py             # Order query logic
│   │   ├── services.py              # Order fulfillment logic
│   │   ├── urls.py                  # /orders/ routing
│   │   └── templates/orders/        # order_list.html, detail.html, checkout.html
│   │
│   ├── products/                    # Product Management & Inventory
│   │   ├── migrations/              # Product migrations
│   │   ├── static/products/         # product_detail.css, list_products.css
│   │   ├── admin.py                 # Product admin
│   │   ├── apps.py                  # ProductsConfig
│   │   ├── models.py                # Product model (English fields)
│   │   ├── services.py              # Inventory & visibility logic
│   │   ├── urls.py                  # /products/ routing
│   │   └── templates/products/      # product_list.html, detail.html
│   │
│   ├── promotions/                  # Discounts & Marketing
│   │   ├── migrations/              # Promotion migrations
│   │   ├── forms.py                 # PromotionsModelForm
│   │   ├── admin.py                 # Promotion admin
│   │   ├── apps.py                  # PromotionsConfig
│   │   ├── models.py                # Promotion model
│   │   ├── urls.py                  # /promotions/ routing
│   │   └── templates/promotions/    # promotion_list.html, add_promotion.html
│   │
│   ├── tasks/                       # Technical/Installation Tasks (Staff Portal)
│   │   ├── migrations/              # Task migrations
│   │   ├── static/tasks/            # task_installation.css, task_detail.css, task_detail.js
│   │   ├── admin.py                 # Task admin
│   │   ├── apps.py                  # TasksConfig
│   │   ├── models.py                # No models (uses apps.orders.Order)
│   │   ├── urls.py                  # /tasks/ routing
│   │   └── templates/tasks/         # task_list.html, task_detail.html
│   │
│   └── warranty/                    # Service Centers & Warranty
│       ├── migrations/              # Warranty migrations
│       ├── static/warranty/         # warranty.css, warranty.js
│       ├── admin.py                 # Warranty admin
│       ├── apps.py                  # WarrantyConfig
│       ├── models.py                # Warranty models
│       ├── services.py              # Warranty lookup logic
│       ├── urls.py                  # /warranty/ routing
│       ├── views.py                 # Warranty lookup views
│       └── templates/warranty/      # warranty_list.html, lookup.html
│
├── Dahuka/                          # Project-level Configuration
│   ├── settings.py                  # Main project settings
│   ├── urls.py                      # Root URL routing
│   ├── asgi.py                      # Async server gateway
│   └── wsgi.py                      # WSGI server gateway
│
├── static/                          # Global Static Assets
│   ├── css/                         # dahuka.css (Global Design System)
│   ├── img/                         # UI assets, logos, banners
│   ├── vendor/                      # Bootstrap, FontAwesome, Google Fonts
│   └── js/                          # Global JS utilities
│
├── templates/                       # Shared Templates
│   ├── base.html                    # Root template skeleton
│   ├── account_base.html            # Shared layout for account views
│   ├── partials/                    # _pagination.html
│   └── registration/                # login.html, signup.html
│
├── media/                           # User-uploaded files
│   └── products/                    # Product images
│
├── document/                        # Documentation
│   └── STRUCTURE.md                 # Project structure (This file)
│
├── .venv/                           # Python Virtual Environment (Ignored)
├── manage.py                        # Django entry point
├── db.sqlite3                       # Database file
├── requirements.txt                 # Dependencies
└── README.md                        # Project introduction
```
