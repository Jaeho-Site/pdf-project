import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "./Header.css";

const Header = ({ unreadCount = 0 }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!user) return null;

  return (
    <header className="header">
      <div className="header-left">
        <Link to="/" className="logo">
          📚 필기자료 공유 서비스
        </Link>
      </div>

      <div className="header-right">
        <nav className="nav-links">
          <Link to="/" className="nav-link">
            홈
          </Link>
          {user.role === "student" && (
            <Link to="/my-custom-pdfs" className="nav-link">
              나만의 필기 만들기
            </Link>
          )}
        </nav>

        <div
          className="notification-badge"
          onClick={() => navigate("/notifications")}
          title="알림"
        >
          🔔
          {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
        </div>

        <div className="user-profile">
          <span className="user-name">{user.name}</span>
          <span className="user-role">
            ({user.role === "professor" ? "교수" : "학생"})
          </span>
        </div>

        <button onClick={handleLogout} className="btn-logout">
          로그아웃
        </button>
      </div>
    </header>
  );
};

export default Header;
