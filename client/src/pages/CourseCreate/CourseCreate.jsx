import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { showToast } from '../../components/Toast/Toast';
import api from '../../utils/api';
import './CourseCreate.css';

const CourseCreate = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    course_name: '',
    year: 2025,
    semester: 1,
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await api.post('/api/courses/create', formData);
      showToast(`강의 "${formData.course_name}"이(가) 생성되었습니다.`, 'success');
      navigate(`/courses/${response.data.course_id}`);
    } catch (error) {
      showToast(error.response?.data?.message || '강의 생성 실패', 'danger');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card">
      <h1 className="form-title">📚 자료실 생성</h1>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="course_name">수업명 *</label>
          <input
            type="text"
            id="course_name"
            name="course_name"
            className="form-control"
            placeholder="예: 데이터베이스"
            value={formData.course_name}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="year">학년 *</label>
          <select
            id="year"
            name="year"
            className="form-control"
            value={formData.year}
            onChange={handleChange}
            required
          >
            <option value="2025">2025</option>
            <option value="2024">2024</option>
            <option value="2023">2023</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="semester">학기 *</label>
          <select
            id="semester"
            name="semester"
            className="form-control"
            value={formData.semester}
            onChange={handleChange}
            required
          >
            <option value="1">1학기</option>
            <option value="2">2학기</option>
          </select>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/')}
          >
            취소
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '생성 중...' : '자료실 생성'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CourseCreate;

