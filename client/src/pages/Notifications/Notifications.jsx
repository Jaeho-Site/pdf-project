import { useState, useEffect } from 'react';
import { showToast } from '../../components/Toast/Toast';
import api from '../../utils/api';
import './Notifications.css';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await api.get('/api/notifications');
      setNotifications(response.data.notifications || []);
    } catch (error) {
      console.error('알림 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.post(`/api/notifications/${notificationId}/read`);
      showToast('읽음 처리되었습니다.', 'success');
      fetchNotifications();
    } catch (error) {
      showToast('오류가 발생했습니다.', 'danger');
    }
  };

  if (loading) {
    return <div className="container">로딩 중...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🔔 알림</h1>
      </div>

      {notifications.length > 0 ? (
        <div className="notifications-list">
          {notifications.map((notification) => (
            <div
              key={notification.notification_id}
              className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
            >
              <div className="notification-content">
                <div className="notification-message">
                  {!notification.is_read && (
                    <span className="notification-badge">NEW</span>
                  )}
                  {notification.message}
                </div>
                <div className="notification-time">
                  {new Date(notification.created_at).toLocaleString()}
                </div>
              </div>

              {!notification.is_read && (
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '0.9rem' }}
                  onClick={() => markAsRead(notification.notification_id)}
                >
                  읽음 처리
                </button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">🔔</div>
          <p style={{ fontSize: '1.1rem' }}>알림이 없습니다.</p>
        </div>
      )}
    </div>
  );
};

export default Notifications;

