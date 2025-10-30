import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import './CourseDetail.css';

const CourseDetail = () => {
  const { courseId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [weeksData, setWeeksData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourseDetail();
  }, [courseId]);

  const fetchCourseDetail = async () => {
    try {
      const response = await api.get(`/api/courses/${courseId}`);
      setCourse(response.data.course);
      setWeeksData(response.data.weeks_data || []);
    } catch (error) {
      console.error('강의 상세 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container">로딩 중...</div>;
  }

  if (!course) {
    return <div className="container">강의를 찾을 수 없습니다.</div>;
  }

  return (
    <div>
      <div className="course-header-section">
        <div className="course-title-large">{course.course_name}</div>
        <div className="course-info-large">
          {course.year}년 {course.semester}학기 |{' '}
          {user?.role === 'professor'
            ? `수강생 ${course.enrolled_students?.length || 0}명`
            : `${course.professor_name} 교수님`}
        </div>
      </div>

      <h2 style={{ marginBottom: '1.5rem', color: '#333' }}>주차별 자료</h2>

      <div className="weeks-grid">
        {weeksData.map((weekData) => (
          <div
            key={weekData.week}
            className="week-card"
            onClick={() => navigate(`/courses/${courseId}/week/${weekData.week}`)}
          >
            <div className="week-title">{weekData.week}주차</div>
            <div className="week-stats">
              <div>
                <span>📄 교수 자료:</span>
                <strong>{weekData.professor_count}</strong>
              </div>
              <div>
                <span>📝 학생 필기:</span>
                <strong>{weekData.student_count}</strong>
              </div>
              <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid #eee' }}>
                <span>👁️ 조회:</span>
                <strong>{weekData.total_views}</strong>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CourseDetail;

