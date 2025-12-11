import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { showToast } from '../../components/Toast/Toast';
import api from '../../utils/api';
import './CourseDetail.css';

const CourseDetail = () => {
  const { courseId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [weeksData, setWeeksData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inviteCode, setInviteCode] = useState('');
  const [showInviteModal, setShowInviteModal] = useState(false);

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

  const handleCreateInviteLink = async () => {
    try {
      const response = await api.post(`/api/courses/${courseId}/invite`, {});
      setInviteCode(response.data.invitation_code);
      setShowInviteModal(true);
      showToast('초대 링크가 생성되었습니다!', 'success');
    } catch (error) {
      showToast('초대 링크 생성에 실패했습니다.', 'danger');
    }
  };

  const handleCopyInviteLink = () => {
    const inviteUrl = `${window.location.origin}/invite/${inviteCode}`;
    navigator.clipboard.writeText(inviteUrl);
    showToast('초대 링크가 복사되었습니다!', 'success');
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
        {user?.role === 'professor' && (
          <button
            className="btn btn-secondary"
            onClick={handleCreateInviteLink}
            style={{ marginTop: '15px' }}
          >
            🔗 초대 링크 생성
          </button>
        )}
      </div>

      {/* 초대 링크 모달 */}
      {showInviteModal && (
        <div className="modal-overlay" onClick={() => setShowInviteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>강의 초대 링크</h3>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              학생들에게 이 링크를 공유하세요.
            </p>
            <div style={{
              background: '#f8f9fa',
              padding: '15px',
              borderRadius: '8px',
              marginBottom: '20px',
              wordBreak: 'break-all',
              fontSize: '14px'
            }}>
              {window.location.origin}/invite/{inviteCode}
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn btn-primary" onClick={handleCopyInviteLink}>
                📋 링크 복사
              </button>
              <button className="btn btn-secondary" onClick={() => setShowInviteModal(false)}>
                닫기
              </button>
            </div>
          </div>
        </div>
      )}

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

