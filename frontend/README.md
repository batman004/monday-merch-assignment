# Monday Merch Frontend

React frontend for the Monday Merch e-commerce platform.

## Features

- User authentication (JWT-based)
- Product browsing with search and category filters
- Shopping cart functionality
- Order creation and viewing
- Responsive design

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env` file (optional, defaults to `http://localhost:8000`):
   ```bash
   cp .env.example .env
   ```

   Edit `.env` if your backend is running on a different URL:
   ```
   VITE_API_URL=http://localhost:8000
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Open browser to `http://localhost:5173`

## Test Accounts

- `test@example.com` / `testpassword123`
- `john.doe@example.com` / `password123`
- `jane.smith@example.com` / `password123`

## Project Structure

```
src/
├── components/      # React components
│   ├── Login.jsx    # Login page
│   ├── Products.jsx # Product listing page
│   ├── Cart.jsx     # Shopping cart
│   └── Orders.jsx   # Order history
├── contexts/         # React contexts
│   ├── AuthContext.jsx  # Authentication state
│   └── CartContext.jsx  # Shopping cart state
├── services/        # API services
│   └── api.js       # API client
└── App.jsx          # Main app with routing
```

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.
