import axios from 'axios';

const api = axios.create({
  baseURL: '',  // 프록시 사용하므로 빈 문자열
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // 세션 쿠키 전송
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (user?.token) {
      config.headers.Authorization = `Bearer ${user.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

