import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { showToast } from "../../components/Toast/Toast";
import api from "../../utils/api";
import "./Login.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  // 페이지 로드 시 이미 로그인된 사용자는 메인 페이지로 리다이렉트
  useEffect(() => {
    if (!authLoading && user) {
      navigate("/", { replace: true });
    }
  }, [user, authLoading, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await login(email, password);

      if (result.success) {
        showToast("로그인 성공!", "success");
        // 상태 업데이트를 위한 짧은 딜레이 후 리다이렉트
        setTimeout(() => {
          setLoading(false);
          navigate("/", { replace: true });
        }, 100);
      } else {
        showToast(result.message, "danger");
        setLoading(false);
      }
    } catch (error) {
      console.error("로그인 오류:", error);
      showToast("로그인 중 오류가 발생했습니다.", "danger");
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="logo">필기자료 공유 서비스</div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">이메일</label>
            <input
              type="email"
              id="email"
              className="form-control"
              placeholder="example@student.ac.kr"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              className="form-control"
              placeholder="비밀번호를 입력하세요"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "로그인 중..." : "로그인"}
          </button>
        </form>

        <div className="signup-link">
          계정이 없으신가요? <Link to="/signup">회원가입</Link>
        </div>

        <div className="test-accounts">
          <h3>📝 테스트 계정</h3>
          <div className="account-list">
            <strong>교수:</strong>
            <br />
            • kim.prof@university.ac.kr / prof1234
            <br />
            • lee.prof@university.ac.kr / prof5678
            <br />
            <br />
            <strong>학생:</strong>
            <br />
            • hong@student.ac.kr / student1
            <br />
            • kim@student.ac.kr / student2
            <br />• lee@student.ac.kr / student3
          </div>

        </div>
      </div>
    </div>
  );
};

export default Login;
