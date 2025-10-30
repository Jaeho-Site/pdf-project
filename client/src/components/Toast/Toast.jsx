import { useState, useEffect } from 'react';
import './Toast.css';

let showToastFunction = null;

export const showToast = (message, type = 'info') => {
  if (showToastFunction) {
    showToastFunction(message, type);
  }
};

const Toast = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    showToastFunction = (message, type) => {
      const id = Date.now();
      setToasts(prev => [...prev, { id, message, type }]);
      
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, 5000);
    };

    return () => {
      showToastFunction = null;
    };
  }, []);

  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <div key={toast.id} className={`alert alert-${toast.type}`}>
          {toast.message}
        </div>
      ))}
    </div>
  );
};

export default Toast;

