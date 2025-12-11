import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import { showToast } from '../../components/Toast/Toast';
import './CourseInvite.css';

const CourseInvite = () => {
  const { inviteCode } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);
  const [inviteInfo, setInviteInfo] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchInviteInfo();
  }, [inviteCode]);

  const fetchInviteInfo = async () => {
    try {
      const response = await api.get(`/api/courses/invite/${inviteCode}`);
      setInviteInfo(response.data);
      setLoading(false);
    } catch (error) {
      setError(error.response?.data?.message || '초대 정보를 불러올 수 없습니다.');
      setLoading(false);
    }
  };

  const handleJoinCourse = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (user.role !== 'student') {
      showToast('학생만 강의에 참가할 수 있습니다.', 'danger');
      return;
    }

    setJoining(true);

    try {
      const response = await api.post(`/api/courses/invite/${inviteCode}/join`);
      showToast(response.data.message, 'success');
      
      // 강의 페이지로 이동
      setTimeout(() => {
        navigate(`/courses/${response.data.course_id}`);
      }, 1000);
    } catch (error) {
      showToast(error.response?.data?.message || '강의 참가에 실패했습니다.', 'danger');
      setJoining(false);
    }
  };

  if (loading) {
    return (
      <div className="invite-page">
        <div className="invite-container">
          <div className="loading">로딩 중...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="invite-page">
        <div className="invite-container">
          <div className="invite-icon">❌</div>
          <h1 className="invite-title">초대 링크 오류</h1>
          <p className="error-message">{error}</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            메인으로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="invite-page">
      <div className="invite-container">
        <div className="invite-icon">📚</div>
        <h1 className="invite-title">강의 초대</h1>
        <p className="invite-subtitle">강의에 참가하시겠습니까?</p>

        <div className="course-info">
          <div className="course-name">{inviteInfo.course.course_name}</div>
          <div className="course-professor">
            👨‍🏫 {inviteInfo.course.professor_name}
          </div>
        </div>

        {!user ? (
          <div>
            <p style={{ marginBottom: '20px', color: '#666' }}>
              강의에 참가하려면 로그인이 필요합니다.
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/login')}>
              로그인하기
            </button>
          </div>
        ) : user.role === 'student' ? (
          <button
            className="btn btn-primary"
            onClick={handleJoinCourse}
            disabled={joining}
          >
            {joining ? '참가 중...' : '강의 참가하기'}
          </button>
        ) : (
          <p className="error-message">
            교수는 강의에 참가할 수 없습니다.
          </p>
        )}
      </div>
    </div>
  );
};

export default CourseInvite;

