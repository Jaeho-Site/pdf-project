import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './pages/Login/Login';
import Signup from './pages/Signup/Signup';
import Main from './pages/Main/Main';
import CourseDetail from './pages/CourseDetail/CourseDetail';
import WeekMaterial from './pages/WeekMaterial/WeekMaterial';
import CreateCustomPDF from './pages/CreateCustomPDF/CreateCustomPDF';
import MyCustomPDFs from './pages/MyCustomPDFs/MyCustomPDFs';
import Notifications from './pages/Notifications/Notifications';
import CourseCreate from './pages/CourseCreate/CourseCreate';

// Protected Route 컴포넌트
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="container">로딩 중...</div>;
  }

  return user ? children : <Navigate to="/login" replace />;
};

// 교수 전용 Route
const ProfessorRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="container">로딩 중...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== 'professor') {
    return <Navigate to="/" replace />;
  }

  return children;
};

// 학생 전용 Route
const StudentRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="container">로딩 중...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== 'student') {
    return <Navigate to="/" replace />;
  }

  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* 로그인/회원가입 페이지 */}
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout>
              <Main />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/courses/:courseId"
        element={
          <ProtectedRoute>
            <Layout>
              <CourseDetail />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/courses/:courseId/week/:week"
        element={
          <ProtectedRoute>
            <Layout>
              <WeekMaterial />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/courses/:courseId/week/:week/create-custom"
        element={
          <StudentRoute>
            <Layout>
              <CreateCustomPDF />
            </Layout>
          </StudentRoute>
        }
      />

      <Route
        path="/my-custom-pdfs"
        element={
          <StudentRoute>
            <Layout>
              <MyCustomPDFs />
            </Layout>
          </StudentRoute>
        }
      />

      <Route
        path="/notifications"
        element={
          <ProtectedRoute>
            <Layout>
              <Notifications />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/courses/create"
        element={
          <ProfessorRoute>
            <Layout>
              <CourseCreate />
            </Layout>
          </ProfessorRoute>
        }
      />

      {/* 기본 리다이렉트 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
