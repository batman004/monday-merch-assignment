# Backend Implementation Plan: E-commerce API (Track B)

## 1. Architectural Strategy
We will implement a **Layered Architecture**. This ensures strict separation of concerns:
* **Routers:** The "Doorway". Defines URLs and parameters.
* **Controllers:** The "Coordinator". Handles HTTP-specifics (status codes, headers) and calls Services.
* **Services:** The "Brain". Pure business logic and database queries. It knows nothing about HTTP.
* **Models/Schemas:** The "Data".

## 2. Technical Stack
* **Framework:** FastAPI
* **Database:** SQLite (dev) / PostgreSQL (prod ready)
* **ORM:** SQLAlchemy (Async)
* **Validation:** Pydantic

## 3. Directory Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # App entry point & Exception Handlers
│   ├── api/                    # INTERFACE LAYER
│   │   ├── __init__.py
│   │   ├── routers.py          # Defines endpoints (@router.get)
│   │   ├── controllers.py      # HTTP orchestration (success/fail responses)
│   │   ├── serializers.py      # Pydantic Schemas (Input/Output)
│   │   └── dependencies.py     # Request-scoped dependencies (get_db)
│   ├── services/               # BUSINESS LOGIC LAYER
│   │   ├── __init__.py
│   │   └── product_service.py  # Pure logic: Query building, filtering, sorting
│   ├── models/                 # DATA LAYER
│   │   ├── __init__.py
│   │   └── domain.py           # SQLAlchemy Models (Tables)
│   ├── core/                   # CONFIG LAYER
│   │   ├── __init__.py
│   │   ├── config.py           # Settings & Env Vars
│   │   └── database.py         # DB Engine & Session Management
│   └── utils/                  # SHARED HELPERS
│       └── pagination.py       # Helper to calculate offsets/pages
├── .env                        # Secrets
├── pyproject.toml              # Dependencies
└── README.md
````

-----

## 4\. Detailed Step-by-Step Plan

### Phase 1: Configuration & Database Setup

**Goal:** Initialize the project and connect to the database.

1.  **Setup `core/config.py`:** Use `pydantic-settings` to load env vars (DB URL, Debug mode).
2.  **Setup `core/database.py`:** Configure SQLAlchemy `create_async_engine` and `AsyncSession`.
3.  **Setup `main.py`:** Initialize `FastAPI()` and include a basic health check.

### Phase 2: Domain Modeling (The Schema)

**Goal:** Create the relational table structure.

1.  **File:** `models/domain.py`
2.  **Tasks:**
      * Define `Base` model.
      * Create `Category` (id, name, slug).
      * Create `Product` (id, title, description, price, inventory, category\_id).
      * Create `Order` & `OrderItem` (for schema completeness as per assignment).
      * **Crucial:** Define relationships (`products = relationship("Product", back_populates="category")`).

### Phase 3: Service Layer (The Logic)

**Goal:** Write the code that actually fetches data, independent of the API.

1.  **File:** `services/product_service.py`
2.  **Function:** `get_product_list(session, filter_params)`
3.  **Logic:**
      * Start with `select(Product)`.
      * If `search` term exists: add `.where(Product.title.ilike(f"%{term}%"))`.
      * If `category` exists: join Category and add `.where(Category.name == cat)`.
      * Apply pagination (limit/offset).
      * Execute and return results.

### Phase 4: API Layer (Interface)

**Goal:** Expose the service via HTTP.

**A. Serializers (`api/serializers.py`)**

  * Define `ProductResponse`: The JSON shape clients will see.
  * Define `ProductQuery`: A Pydantic model to parse/validate query params (`?search=...`).

**B. Controllers (`api/controllers.py`)**

  * Create `fetch_products(db, params)`:
      * Call `product_service.get_product_list`.
      * Handle empty states or errors (e.g., raise `HTTPException` if specific constraints fail).
      * Return the list of data to the router.

**C. (`api/routers.py`)** 

  * Define `GET /products`.
  * Inject `db` session.
  * Inject query params.
  * Call `controllers.fetch_products`.

### Phase 5: Production Polish

**Goal:** Meet the "Trade-off awareness" and "Documentation" criteria

1.  **Seed Data:** Create a startup event in `main.py` that checks if the DB is empty and adds 5-10 sample products.
2.  **Docs:** Write a `README.md` explaining:
      * How to run (Docker or local).
      * The Schema choice.
      * Why we split Controller vs Service.
3. **Containerization:** Write up a simple Dockerfile to containerise the application for easy reproducability and machine agnostic development. Optionally add option of using postgresql in a docker-compose setup
4. **Auth based endpoints:** Validate incoming requests using either a token based system or simpler email based user auth.
5. **Ensure propper logging**
6. **Add fault tolerance and fallback mechanisms:** Exception handling, manage DB server failures
7. **Security:** Sudden traffic burst, DOS, SQL injection