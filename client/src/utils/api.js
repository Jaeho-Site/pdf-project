import axios from "axios";

const api = axios.create({
  baseURL: "https://course.o-r.kr",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    const user = JSON.parse(localStorage.getItem("user") || "null");
    if (user?.token) {
      config.headers.Authorization = `Bearer ${user.token}`;
    }
    // user_id를 헤더에 추가 (백엔드 인증용)
    if (user?.user_id) {
      config.headers["X-User-ID"] = user.user_id;
      config.headers["X-User-Role"] = user.role;
      config.headers["X-User-Email"] = user.email;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 에러 처리 (로그인 요청은 제외)
    if (
      error.response?.status === 401 &&
      !error.config.url.includes("/api/auth/login")
    ) {
      console.warn("⚠️ 401 Unauthorized - 세션 만료");
      // localStorage.removeItem("user"); // localStorage는 유지
      // window.location.href = "/login";  // 자동 리다이렉트 비활성화
    }
    return Promise.reject(error);
  }
);

export default api;
