import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { productsAPI } from '../services/api';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';

const CATEGORIES = [
  'Electronics',
  'Clothing',
  'Books',
  'Home & Garden',
  'Sports & Outdoors',
];

export default function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [notification, setNotification] = useState(null);
  const { addToCart } = useCart();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchProducts();
  }, [page, category, search]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: 12,
        ...(search && { search }),
        ...(category && { category }),
      };
      const data = await productsAPI.getProducts(params);
      setProducts(data.products);
      setTotalPages(data.total_pages);
    } catch (error) {
      console.error('Error fetching products:', error);
      if (error.response?.status === 401) {
        logout();
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (product) => {
    if (product.inventory > 0) {
      addToCart(product);
      setNotification(`Added ${product.title} to cart!`);
      setTimeout(() => setNotification(null), 3000);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchProducts();
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.logo}>Monday Merch</h1>
        <div style={styles.headerRight}>
          <button onClick={() => navigate('/cart')} style={styles.cartButton}>
            Cart
          </button>
          <button onClick={() => navigate('/orders')} style={styles.ordersButton}>
            Orders
          </button>
          <button onClick={logout} style={styles.logoutButton}>
            Logout
          </button>
        </div>
      </header>

      <div style={styles.content}>
        {notification && (
          <div style={styles.notification}>
            {notification}
          </div>
        )}
        <div style={styles.filters}>
          <form onSubmit={handleSearch} style={styles.searchForm}>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search products..."
              style={styles.searchInput}
            />
            <button type="submit" style={styles.searchButton}>
              Search
            </button>
          </form>

          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setPage(1);
            }}
            style={styles.categorySelect}
          >
            <option value="">All Categories</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <div style={styles.loading}>Loading products...</div>
        ) : (
          <>
            <div style={styles.productsGrid}>
              {products.map((product) => (
                <div key={product.id} style={styles.productCard}>
                  <div style={styles.productImage}>
                    {/* Placeholder for image - will be added later */}
                    <div style={styles.imagePlaceholder}>
                      {product.title.charAt(0)}
                    </div>
                  </div>
                  <div style={styles.productInfo}>
                    <h3 style={styles.productTitle}>{product.title}</h3>
                    <p style={styles.productDescription}>
                      {product.description || 'No description available'}
                    </p>
                    <div style={styles.productFooter}>
                      <span style={styles.productPrice}>
                        ${parseFloat(product.price).toFixed(2)}
                      </span>
                      <span style={styles.productInventory}>
                        {product.inventory > 0
                          ? `${product.inventory} in stock`
                          : 'Out of stock'}
                      </span>
                    </div>
                    <button
                      onClick={() => handleAddToCart(product)}
                      disabled={product.inventory === 0}
                      style={{
                        ...styles.addButton,
                        ...(product.inventory === 0 && styles.addButtonDisabled),
                      }}
                    >
                      {product.inventory > 0 ? 'Add to Cart' : 'Out of Stock'}
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div style={styles.pagination}>
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                style={styles.pageButton}
              >
                Previous
              </button>
              <span style={styles.pageInfo}>
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                style={styles.pageButton}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: 'white',
    padding: '16px 24px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    margin: 0,
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#333',
  },
  headerRight: {
    display: 'flex',
    gap: '12px',
  },
  cartButton: {
    padding: '8px 16px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  ordersButton: {
    padding: '8px 16px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  logoutButton: {
    padding: '8px 16px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '24px',
  },
  filters: {
    display: 'flex',
    gap: '16px',
    marginBottom: '24px',
    flexWrap: 'wrap',
  },
  searchForm: {
    display: 'flex',
    flex: 1,
    minWidth: '300px',
    gap: '8px',
  },
  searchInput: {
    flex: 1,
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '16px',
  },
  searchButton: {
    padding: '12px 24px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  categorySelect: {
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '16px',
    minWidth: '200px',
  },
  productsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '24px',
    marginBottom: '24px',
  },
  productCard: {
    backgroundColor: 'white',
    borderRadius: '8px',
    overflow: 'hidden',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
  },
  productImage: {
    width: '100%',
    height: '200px',
    backgroundColor: '#f0f0f0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  imagePlaceholder: {
    fontSize: '64px',
    color: '#ccc',
    fontWeight: 'bold',
  },
  productInfo: {
    padding: '16px',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
  },
  productTitle: {
    margin: '0 0 8px 0',
    fontSize: '18px',
    fontWeight: '600',
    color: '#333',
  },
  productDescription: {
    margin: '0 0 16px 0',
    fontSize: '14px',
    color: '#666',
    flex: 1,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
  },
  productFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },
  productPrice: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#007bff',
  },
  productInventory: {
    fontSize: '12px',
    color: '#666',
  },
  addButton: {
    padding: '10px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  },
  addButtonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed',
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '18px',
    color: '#666',
  },
  pagination: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '16px',
    marginTop: '24px',
  },
  pageButton: {
    padding: '8px 16px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  pageInfo: {
    fontSize: '16px',
    color: '#666',
  },
  notification: {
    position: 'fixed',
    top: '20px',
    right: '20px',
    backgroundColor: '#28a745',
    color: 'white',
    padding: '16px 24px',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    zIndex: 1000,
    fontSize: '16px',
    fontWeight: '500',
    animation: 'slideIn 0.3s ease-out',
  },
};
