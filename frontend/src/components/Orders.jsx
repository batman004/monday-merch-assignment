import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ordersAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const data = await ordersAPI.getOrders();
      setOrders(data);
    } catch (error) {
      console.error('Error fetching orders:', error);
      if (error.response?.status === 401) {
        logout();
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <div style={styles.header}>
          <h1 style={styles.title}>My Orders</h1>
          <button onClick={() => navigate('/products')} style={styles.backButton}>
            Back to Products
          </button>
        </div>

        {loading ? (
          <div style={styles.loading}>Loading orders...</div>
        ) : orders.length === 0 ? (
          <div style={styles.emptyOrders}>
            <h2>No orders yet</h2>
            <button onClick={() => navigate('/products')} style={styles.shopButton}>
              Start Shopping
            </button>
          </div>
        ) : (
          <div style={styles.ordersList}>
            {orders.map((order) => (
              <div key={order.id} style={styles.orderCard}>
                <div style={styles.orderHeader}>
                  <div>
                    <h3 style={styles.orderId}>Order #{order.id}</h3>
                    <p style={styles.orderDate}>
                      {new Date(order.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div style={styles.orderStatus}>
                    <span
                      style={{
                        ...styles.statusBadge,
                        ...(order.status === 'COMPLETED' && styles.statusCompleted),
                        ...(order.status === 'PENDING' && styles.statusPending),
                        ...(order.status === 'CANCELLED' && styles.statusCancelled),
                      }}
                    >
                      {order.status}
                    </span>
                    <p style={styles.orderTotal}>
                      ${parseFloat(order.total_amount).toFixed(2)}
                    </p>
                  </div>
                </div>

                <div style={styles.orderItems}>
                  {order.order_items?.map((item) => (
                    <div key={item.id} style={styles.orderItem}>
                      <div style={styles.itemImage}>
                        <div style={styles.imagePlaceholder}>
                          {item.product?.title?.charAt(0) || '?'}
                        </div>
                      </div>
                      <div style={styles.itemDetails}>
                        <h4 style={styles.itemTitle}>
                          {item.product?.title || 'Product'}
                        </h4>
                        <p style={styles.itemInfo}>
                          Quantity: {item.quantity} × ${parseFloat(item.price_at_purchase).toFixed(2)}
                        </p>
                      </div>
                      <div style={styles.itemTotal}>
                        ${(parseFloat(item.price_at_purchase) * item.quantity).toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>

                {order.shipping_street && (
                  <div style={styles.shippingAddress}>
                    <strong>Shipping Address:</strong>
                    <p>
                      {order.shipping_street}
                      <br />
                      {order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}
                      <br />
                      {order.shipping_country}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
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
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  title: {
    fontSize: '32px',
    margin: 0,
    color: '#333',
  },
  backButton: {
    padding: '10px 20px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '18px',
    color: '#666',
  },
  emptyOrders: {
    textAlign: 'center',
    padding: '60px 20px',
    backgroundColor: 'white',
    borderRadius: '8px',
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
  ordersList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  orderCard: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  orderHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '20px',
    paddingBottom: '20px',
    borderBottom: '2px solid #eee',
  },
  orderId: {
    margin: '0 0 8px 0',
    fontSize: '20px',
    color: '#333',
  },
  orderDate: {
    margin: 0,
    fontSize: '14px',
    color: '#666',
  },
  orderStatus: {
    textAlign: 'right',
  },
  statusBadge: {
    display: 'inline-block',
    padding: '6px 12px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 'bold',
    marginBottom: '8px',
  },
  statusPending: {
    backgroundColor: '#ffc107',
    color: '#000',
  },
  statusCompleted: {
    backgroundColor: '#28a745',
    color: 'white',
  },
  statusCancelled: {
    backgroundColor: '#dc3545',
    color: 'white',
  },
  orderTotal: {
    margin: 0,
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#007bff',
  },
  orderItems: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  orderItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '12px',
    backgroundColor: '#f8f9fa',
    borderRadius: '4px',
  },
  itemImage: {
    width: '60px',
    height: '60px',
    backgroundColor: '#e9ecef',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  imagePlaceholder: {
    fontSize: '24px',
    color: '#adb5bd',
    fontWeight: 'bold',
  },
  itemDetails: {
    flex: 1,
  },
  itemTitle: {
    margin: '0 0 4px 0',
    fontSize: '16px',
    color: '#333',
  },
  itemInfo: {
    margin: 0,
    fontSize: '14px',
    color: '#666',
  },
  itemTotal: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#333',
  },
  shippingAddress: {
    marginTop: '20px',
    paddingTop: '20px',
    borderTop: '1px solid #eee',
    fontSize: '14px',
    color: '#666',
  },
};
