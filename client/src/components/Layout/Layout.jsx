import { useState, useEffect } from 'react';
import Header from './Header';
import Toast from '../Toast/Toast';

const Layout = ({ children }) => {
  const [unreadCount, setUnreadCount] = useState(0);

  // TODO: API에서 읽지 않은 알림 개수 가져오기
  useEffect(() => {
    // fetchUnreadCount();
  }, []);

  return (
    <div className="app">
      <Header unreadCount={unreadCount} />
      <main className="container">
        {children}
      </main>
      <Toast />
    </div>
  );
};

export default Layout;

