import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import './Main.css';

const Main = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await api.get('/api/courses');
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('강의 목록 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container">로딩 중...</div>;
  }

  return (
    <div>
      <div className="welcome-section">
        <h1>안녕하세요, {user?.name}님! 👋</h1>
        <p>
          {user?.role === 'professor'
            ? '강의를 관리하고 학습 자료를 공유하세요.'
            : '강의 자료를 확인하고 나만의 필기를 만들어보세요.'}
        </p>
      </div>

      <div className="section-header">
        <h2 className="section-title">
          {user?.role === 'professor' ? '담당 강의' : '수강 강의'}
        </h2>
        {user?.role === 'professor' && (
          <button 
            className="btn btn-primary"
            onClick={() => navigate('/courses/create')}
          >
            + 자료실 생성
          </button>
        )}
      </div>

      {courses.length > 0 ? (
        <div className="courses-grid">
          {courses.map((course) => (
            <div
              key={course.course_id}
              className="course-card"
              onClick={() => navigate(`/courses/${course.course_id}`)}
            >
              <div className="course-header">
                <div>
                  <div className="course-title">{course.course_name}</div>
                  <div className="course-semester">
                    {course.year}년 {course.semester}학기
                  </div>
                  {user?.role === 'student' && (
                    <div className="course-professor">
                      👨‍🏫 {course.professor_name}
                    </div>
                  )}
                </div>
              </div>

              <div className="course-footer">
                {user?.role === 'professor'
                  ? `수강생: ${course.enrolled_students?.length || 0}명`
                  : '강의실 입장 →'}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">📚</div>
          <p>
            {user?.role === 'professor'
              ? '담당하는 강의가 없습니다.'
              : '수강 중인 강의가 없습니다.'}
          </p>
          {user?.role === 'professor' && (
            <p style={{ marginTop: '1rem' }}>
              <button 
                className="btn btn-primary"
                onClick={() => navigate('/courses/create')}
              >
                자료실 생성하기
              </button>
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default Main;

