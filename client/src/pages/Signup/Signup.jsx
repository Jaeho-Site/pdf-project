import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { showToast } from '../../components/Toast/Toast';
import './Signup.css';

const Signup = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    role: 'student'
  });
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleRoleChange = (role) => {
    if (role === 'professor') {
      alert('교수 로그인은 사전인증이 필요합니다.');
      return;
    }
    setFormData({
      ...formData,
      role
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 교수 회원가입 차단
    if (formData.role === 'professor') {
      alert('교수 로그인은 사전인증이 필요합니다.');
      return;
    }

    // 유효성 검사
    if (!formData.email || !formData.password || !formData.name) {
      showToast('모든 필드를 입력해주세요.', 'danger');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      showToast('비밀번호가 일치하지 않습니다.', 'danger');
      return;
    }

    if (formData.password.length < 6) {
      showToast('비밀번호는 최소 6자 이상이어야 합니다.', 'danger');
      return;
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      showToast('올바른 이메일 형식이 아닙니다.', 'danger');
      return;
    }

    setLoading(true);

    const result = await signup({
      email: formData.email,
      password: formData.password,
      name: formData.name,
      role: formData.role
    });

    if (result.success) {
      showToast('회원가입이 완료되었습니다! 로그인해주세요.', 'success');
      navigate('/login');
    } else {
      showToast(result.message, 'danger');
    }

    setLoading(false);
  };

  return (
    <div className="signup-page">
      <div className="signup-container">
        <div className="logo">필기자료 공유 서비스</div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">이름</label>
            <input
              type="text"
              id="name"
              name="name"
              className="form-control"
              placeholder="홍길동"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">이메일</label>
            <input
              type="email"
              id="email"
              name="email"
              className="form-control"
              placeholder="example@student.ac.kr"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              name="password"
              className="form-control"
              placeholder="최소 6자 이상"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">비밀번호 확인</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              className="form-control"
              placeholder="비밀번호를 다시 입력하세요"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>역할</label>
            <div className="role-selector">
              <div
                className={`role-option ${formData.role === 'student' ? 'active' : ''}`}
                onClick={() => handleRoleChange('student')}
              >
                👨‍🎓 학생
              </div>
              <div
                className={`role-option ${formData.role === 'professor' ? 'active' : ''}`}
                onClick={() => handleRoleChange('professor')}
              >
                👨‍🏫 교수
              </div>
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '가입 중...' : '회원가입'}
          </button>
        </form>

        <div className="login-link">
          이미 계정이 있으신가요? <Link to="/login">로그인</Link>
        </div>
      </div>
    </div>
  );
};

export default Signup;

