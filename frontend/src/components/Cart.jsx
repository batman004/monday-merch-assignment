import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import { ordersAPI } from '../services/api';

export default function Cart() {
  const { cart, updateQuantity, removeFromCart, getTotalPrice, clearCart } = useCart();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCheckout = async () => {
    if (cart.length === 0) return;

    setLoading(true);
    setError('');

    try {
      const orderData = {
        items: cart.map((item) => ({
          product_id: item.id,
          quantity: item.quantity,
        })),
        // Shipping address will use user's address from backend
      };

      await ordersAPI.createOrder(orderData);
      clearCart();
      navigate('/orders');
    } catch (err) {
      console.error('Error creating order:', err);
      setError(err.response?.data?.detail || 'Failed to create order');
      if (err.response?.status === 401) {
        logout();
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  if (cart.length === 0) {
    return (
      <div style={styles.container}>
        <div style={styles.emptyCart}>
          <h2>Your cart is empty</h2>
          <button onClick={() => navigate('/products')} style={styles.shopButton}>
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1 style={styles.title}>Shopping Cart</h1>

        {error && <div style={styles.error}>{error}</div>}

        <div style={styles.cartItems}>
          {cart.map((item) => (
            <div key={item.id} style={styles.cartItem}>
              <div style={styles.itemImage}>
                <div style={styles.imagePlaceholder}>{item.title.charAt(0)}</div>
              </div>
              <div style={styles.itemInfo}>
                <h3 style={styles.itemTitle}>{item.title}</h3>
                <p style={styles.itemPrice}>${parseFloat(item.price).toFixed(2)}</p>
              </div>
              <div style={styles.itemControls}>
                <div style={styles.quantityControls}>
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                    style={styles.quantityButton}
                  >
                    -
                  </button>
                  <span style={styles.quantity}>{item.quantity}</span>
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    style={styles.quantityButton}
                  >
                    +
                  </button>
                </div>
                <button
                  onClick={() => removeFromCart(item.id)}
                  style={styles.removeButton}
                >
                  Remove
                </button>
              </div>
              <div style={styles.itemTotal}>
                ${(parseFloat(item.price) * item.quantity).toFixed(2)}
              </div>
            </div>
          ))}
        </div>

        <div style={styles.summary}>
          <div style={styles.summaryRow}>
            <span>Subtotal:</span>
            <span>${getTotalPrice().toFixed(2)}</span>
          </div>
          <div style={styles.summaryRow}>
            <span>Total:</span>
            <span style={styles.total}>${getTotalPrice().toFixed(2)}</span>
          </div>
          <button
            onClick={handleCheckout}
            disabled={loading}
            style={styles.checkoutButton}
          >
            {loading ? 'Processing...' : 'Checkout'}
          </button>
          <button
            onClick={() => navigate('/products')}
            style={styles.continueButton}
          >
            Continue Shopping
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '24px',
  },
  content: {
    maxWidth: '1000px',
    margin: '0 auto',
  },
  title: {
    fontSize: '32px',
    marginBottom: '24px',
    color: '#333',
  },
  emptyCart: {
    textAlign: 'center',
    padding: '60px 20px',
  },
  shopButton: {
    padding: '12px 24px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    marginTop: '16px',
  },
  error: {
    backgroundColor: '#fee',
    color: '#c33',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '16px',
  },
  cartItems: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '24px',
    marginBottom: '24px',
  },
  cartItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '16px 0',
    borderBottom: '1px solid #eee',
  },
  itemImage: {
    width: '80px',
    height: '80px',
    backgroundColor: '#f0f0f0',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  imagePlaceholder: {
    fontSize: '32px',
    color: '#ccc',
    fontWeight: 'bold',
  },
  itemInfo: {
    flex: 1,
  },
  itemTitle: {
    margin: '0 0 8px 0',
    fontSize: '18px',
    color: '#333',
  },
  itemPrice: {
    margin: 0,
    fontSize: '14px',
    color: '#666',
  },
  itemControls: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    alignItems: 'center',
  },
  quantityControls: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  quantityButton: {
    width: '32px',
    height: '32px',
    border: '1px solid #ddd',
    backgroundColor: 'white',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '18px',
  },
  quantity: {
    minWidth: '40px',
    textAlign: 'center',
    fontSize: '16px',
  },
  removeButton: {
    padding: '6px 12px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  itemTotal: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#333',
    minWidth: '100px',
    textAlign: 'right',
  },
  summary: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '24px',
  },
  summaryRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '12px',
    fontSize: '16px',
  },
  total: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#007bff',
  },
  checkoutButton: {
    width: '100%',
    padding: '16px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '18px',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginTop: '16px',
  },
  continueButton: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    marginTop: '12px',
  },
};
