import { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 세션 확인
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const signup = async (userData) => {
    try {
      const response = await api.post('/api/auth/signup', userData);
      return { 
        success: true,
        message: response.data.message 
      };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.message || '회원가입에 실패했습니다.' 
      };
    }
  };

  const login = async (email, password) => {
    try {
      console.log('🔐 로그인 시도:', email);
      const response = await api.post('/api/auth/login', { email, password });
      const userData = response.data.user;
      console.log('✅ 로그인 응답:', userData);
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      console.log('💾 localStorage 저장 완료');
      
      return { success: true };
    } catch (error) {
      console.error('❌ 로그인 실패:', error);
      return { 
        success: false, 
        message: error.response?.data?.message || '로그인에 실패했습니다.' 
      };
    }
  };

  const logout = async () => {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      console.error('로그아웃 API 호출 실패:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('user');
    }
  };

  return (
    <AuthContext.Provider value={{ user, signup, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

