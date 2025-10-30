import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { showToast } from '../../components/Toast/Toast';
import api from '../../utils/api';
import './WeekMaterial.css';

const WeekMaterial = () => {
  const { courseId, week } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [professorMaterials, setProfessorMaterials] = useState([]);
  const [studentMaterials, setStudentMaterials] = useState([]);
  const [sortBy, setSortBy] = useState('latest');
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchMaterials();
  }, [courseId, week, sortBy]);

  const fetchMaterials = async () => {
    try {
      const response = await api.get(`/api/courses/${courseId}/week/${week}?sort=${sortBy}`);
      setCourse(response.data.course);
      setProfessorMaterials(response.data.professor_materials || []);
      setStudentMaterials(response.data.student_materials || []);
    } catch (error) {
      console.error('자료 조회 실패:', error);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    
    if (!uploadFile) {
      showToast('파일을 선택해주세요.', 'warning');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      await api.post(`/api/courses/${courseId}/week/${week}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      showToast('업로드 완료!', 'success');
      setUploadFile(null);
      fetchMaterials();
    } catch (error) {
      showToast(error.response?.data?.message || '업로드 실패', 'danger');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (materialId, fileName) => {
    try {
      const response = await api.get(`/api/materials/${materialId}/download`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      showToast('다운로드 실패', 'danger');
    }
  };

  if (!course) {
    return <div className="container">로딩 중...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="breadcrumb">
            <Link to="/">홈</Link> &gt;{' '}
            <Link to={`/courses/${courseId}`}>{course.course_name}</Link> &gt; {week}주차
          </div>
          <h1>{week}주차 자료</h1>
        </div>
      </div>

      {/* 업로드 영역 */}
      <div className="upload-area">
        <form onSubmit={handleFileUpload}>
          <p style={{ marginBottom: '1rem' }}>📤 PDF 파일 업로드</p>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setUploadFile(e.target.files[0])}
            style={{ marginBottom: '1rem' }}
          />
          <br />
          <button type="submit" className="btn btn-primary" disabled={uploading}>
            {uploading ? '업로드 중...' : '업로드'}
          </button>
        </form>
      </div>

      {/* 교수 자료 */}
      <div className="section">
        <div className="section-title">📄 교수 자료</div>
        {professorMaterials.length > 0 ? (
          <div className="materials-list">
            {professorMaterials.map((material) => (
              <div key={material.material_id} className="material-item">
                <div className="material-info">
                  <div className="material-name">{material.file_name}</div>
                  <div className="material-meta">
                    {material.uploader_name} | {new Date(material.upload_date).toLocaleString()} |
                    페이지: {material.page_count} | 다운로드: {material.download_count}
                  </div>
                </div>
                <div className="material-actions">
                  <a
                    href={`/api/materials/${material.material_id}/view`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary"
                  >
                    보기
                  </a>
                  <button
                    className="btn btn-primary"
                    onClick={() => handleDownload(material.material_id, material.file_name)}
                  >
                    다운로드
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#999', textAlign: 'center', padding: '2rem' }}>
            업로드된 교수 자료가 없습니다.
          </p>
        )}
      </div>

      {/* 학생 필기 */}
      <div className="section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div className="section-title">📝 학생 필기</div>
          {user?.role === 'student' && studentMaterials.length > 0 && (
            <button
              className="btn btn-success"
              onClick={() => navigate(`/courses/${courseId}/week/${week}/create-custom`)}
            >
              ✨ 나만의 필기 만들기
            </button>
          )}
        </div>

        {studentMaterials.length > 0 ? (
          <>
            {/* 정렬 필터 */}
            <div className="filter-bar">
              <label>정렬:</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="latest">최신순</option>
                <option value="name">이름순</option>
                <option value="popular">인기순</option>
                <option value="downloads">다운로드순</option>
              </select>
            </div>

            <div className="materials-list">
              {studentMaterials.map((material) => (
                <div key={material.material_id} className="material-item">
                  <div className="material-info">
                    <div className="material-name">{material.file_name}</div>
                    <div className="material-meta">
                      {material.uploader_name} | {new Date(material.upload_date).toLocaleString()} |
                      페이지: {material.page_count} | 👁️ {material.view_count} | ⬇️{' '}
                      {material.download_count}
                    </div>
                  </div>
                  <div className="material-actions">
                    <a
                      href={`/api/materials/${material.material_id}/view`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary"
                    >
                      보기
                    </a>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleDownload(material.material_id, material.file_name)}
                    >
                      다운로드
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p style={{ color: '#999', textAlign: 'center', padding: '2rem' }}>
            업로드된 학생 필기가 없습니다.
            {user?.role === 'student' && <><br />첫 번째로 필기를 공유해보세요!</>}
          </p>
        )}
      </div>
    </div>
  );
};

export default WeekMaterial;

