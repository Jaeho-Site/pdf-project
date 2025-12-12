import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { showToast } from '../../components/Toast/Toast';
import api from '../../utils/api';
import './Main.css';

const Main = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteCode, setInviteCode] = useState('');
  const [joining, setJoining] = useState(false);

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

  const handleJoinByCode = async (code = null) => {
    const codeToUse = code || inviteCode.trim();
    if (!codeToUse) {
      showToast('초대 코드를 입력해주세요.', 'danger');
      return;
    }

    setJoining(true);

    try {
      const response = await api.post(`/api/courses/invite/${codeToUse}/join`);
      showToast(response.data.message, 'success');
      setShowInviteModal(false);
      setInviteCode('');
      fetchCourses(); // 강의 목록 새로고침
      
      // 강의 페이지로 이동
      setTimeout(() => {
        navigate(`/courses/${response.data.course_id}`);
      }, 1000);
    } catch (error) {
      showToast(error.response?.data?.message || '강의 참가에 실패했습니다.', 'danger');
    } finally {
      setJoining(false);
    }
  };

  // 추천 초대 코드 (이교수의 심화프로젝트랩[ALL])
  const RECOMMENDED_INVITE_CODE = 'ZR6Hsr5nkHg';

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
        {user?.role === 'professor' ? (
          <button 
            className="btn btn-primary"
            onClick={() => navigate('/courses/create')}
          >
            + 자료실 생성
          </button>
        ) : (
          <button 
            className="btn btn-success"
            onClick={() => setShowInviteModal(true)}
          >
            🔗 초대 코드로 참가
          </button>
        )}
      </div>

      {/* 초대 코드 입력 모달 */}
      {showInviteModal && (
        <div className="modal-overlay" onClick={() => setShowInviteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>강의 초대 코드 입력</h3>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              교수님께 받은 초대 코드를 입력하세요.
            </p>
            <input
              type="text"
              className="form-control"
              placeholder="초대 코드 입력 (예: AbCdEfGh)"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value)}
              style={{ marginBottom: '20px' }}
            />
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                className="btn btn-primary" 
                onClick={handleJoinByCode}
                disabled={joining}
                style={{ flex: 1 }}
              >
                {joining ? '참가 중...' : '참가하기'}
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={() => {
                  setShowInviteModal(false);
                  setInviteCode('');
                }}
                style={{ flex: 1 }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}

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
          {user?.role === 'student' && (
            <div style={{ 
              marginTop: '2rem', 
              padding: '1.5rem', 
              backgroundColor: '#f8f9fa', 
              borderRadius: '8px',
              border: '2px solid #4CAF50',
              maxWidth: '500px',
              margin: '2rem auto 0'
            }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.5rem',
                marginBottom: '1rem',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                color: '#4CAF50'
              }}>
                ✨ 추천 강의
              </div>
              <p style={{ marginBottom: '1rem', color: '#666' }}>
                이교수의 <strong>"심화프로젝트랩[ALL]"</strong> 강의에 참가하시겠어요?
              </p>
              <div style={{ 
                display: 'flex', 
                gap: '0.5rem', 
                alignItems: 'center',
                marginBottom: '1rem',
                padding: '0.75rem',
                backgroundColor: 'white',
                borderRadius: '4px',
                border: '1px solid #ddd'
              }}>
                <span style={{ color: '#999', fontSize: '0.9rem' }}>초대 코드:</span>
                <code style={{ 
                  flex: 1, 
                  padding: '0.5rem', 
                  backgroundColor: '#f5f5f5', 
                  borderRadius: '4px',
                  fontFamily: 'monospace',
                  fontSize: '0.9rem',
                  fontWeight: 'bold'
                }}>
                  {RECOMMENDED_INVITE_CODE}
                </code>
              </div>
              <button 
                className="btn btn-success"
                onClick={() => handleJoinByCode(RECOMMENDED_INVITE_CODE)}
                disabled={joining}
                style={{ width: '100%', fontSize: '1rem', padding: '0.75rem' }}
              >
                {joining ? '참가 중...' : '🎯 이 강의에 참가하기'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Main;

