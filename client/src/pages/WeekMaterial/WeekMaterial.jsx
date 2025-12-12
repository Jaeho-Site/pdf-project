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
  const [uploadDeadline, setUploadDeadline] = useState(null);
  const [canUpload, setCanUpload] = useState(true);
  const [canView, setCanView] = useState(true);
  const [showDeadlineModal, setShowDeadlineModal] = useState(false);
  const [deadlineInput, setDeadlineInput] = useState('');
  const [settingDeadline, setSettingDeadline] = useState(false);

  useEffect(() => {
    fetchMaterials();
  }, [courseId, week, sortBy]);

  const fetchMaterials = async () => {
    try {
      const response = await api.get(`/api/courses/${courseId}/week/${week}?sort=${sortBy}`);
      setCourse(response.data.course);
      setProfessorMaterials(response.data.professor_materials || []);
      setStudentMaterials(response.data.student_materials || []);
      setUploadDeadline(response.data.upload_deadline);
      setCanUpload(response.data.can_upload ?? true);
      setCanView(response.data.can_view ?? true);
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
      // 백엔드에서 Content-Disposition 헤더로 파일명을 설정하므로
      // Content-Disposition 헤더에서 파일명 추출 시도
      const contentDisposition = response.headers['content-disposition'];
      let downloadFileName = fileName;
      
      if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (fileNameMatch && fileNameMatch[1]) {
          downloadFileName = fileNameMatch[1].replace(/['"]/g, '');
        }
      }
      
      // .pdf 확장자 보장
      if (!downloadFileName.endsWith('.pdf')) {
        downloadFileName += '.pdf';
      }
      
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', downloadFileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      showToast('다운로드 실패', 'danger');
    }
  };

  const handleView = async (materialId, fileName) => {
    try {
      const response = await api.get(`/api/materials/${materialId}/view`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      window.open(url, '_blank');
      // URL은 나중에 자동으로 정리됨
    } catch (error) {
      showToast('미리보기 실패', 'danger');
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
          <p style={{ marginBottom: '1rem' }}>
            📤 PDF 파일 업로드 {user?.role === 'professor' ? '(교수 자료)' : '(학생 필기)'}
          </p>
          
          {/* 교수용 마감일 설정 */}
          {user?.role === 'professor' && (
            <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              {uploadDeadline ? (
                <>
                  <span style={{ fontSize: '0.9rem' }}>
                    ⏰ 학생 업로드 마감일: <strong>{new Date(uploadDeadline).toLocaleString('ko-KR')}</strong>
                  </span>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.85rem' }}
                    onClick={() => {
                      setDeadlineInput(uploadDeadline);
                      setShowDeadlineModal(true);
                    }}
                  >
                    수정
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                  onClick={() => {
                    const now = new Date();
                    now.setDate(now.getDate() + 7); // 기본값: 7일 후
                    setDeadlineInput(now.toISOString().slice(0, 16));
                    setShowDeadlineModal(true);
                  }}
                >
                  📅 학생 업로드 마감일 설정
                </button>
              )}
            </div>
          )}
          
          {/* 학생용 마감일 표시 */}
          {user?.role === 'student' && uploadDeadline && (
            <div style={{ 
              marginBottom: '1rem', 
              padding: '0.75rem', 
              backgroundColor: canUpload ? '#e8f5e9' : '#ffebee',
              borderRadius: '4px',
              fontSize: '0.9rem'
            }}>
              {canUpload ? (
                <>⏰ 업로드 마감일: <strong>{new Date(uploadDeadline).toLocaleString('ko-KR')}</strong></>
              ) : (
                <>❌ 업로드 기간이 종료되었습니다. (마감일: {new Date(uploadDeadline).toLocaleString('ko-KR')})</>
              )}
            </div>
          )}
          
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setUploadFile(e.target.files[0])}
            style={{ marginBottom: '1rem' }}
            disabled={!canUpload && user?.role === 'student'}
          />
          <br />
          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={uploading || (!canUpload && user?.role === 'student')}
          >
            {uploading ? '업로드 중...' : canUpload || user?.role === 'professor' ? '업로드' : '업로드 기간 종료'}
          </button>
        </form>
      </div>
      
      {/* 마감일 설정 모달 */}
      {showDeadlineModal && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setShowDeadlineModal(false)}
        >
          <div 
            style={{
              backgroundColor: 'white',
              padding: '2rem',
              borderRadius: '8px',
              minWidth: '400px',
              maxWidth: '90%'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ marginBottom: '1rem' }}>학생 업로드 마감일 설정</h3>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                마감일 및 시간:
              </label>
              <input
                type="datetime-local"
                value={deadlineInput}
                onChange={(e) => setDeadlineInput(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  fontSize: '1rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              />
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setShowDeadlineModal(false)}
                disabled={settingDeadline}
              >
                취소
              </button>
              <button
                className="btn btn-primary"
                onClick={async () => {
                  if (!deadlineInput) {
                    showToast('마감일을 입력해주세요.', 'warning');
                    return;
                  }
                  
                  setSettingDeadline(true);
                  try {
                    await api.post(`/api/courses/${courseId}/week/${week}/deadline`, {
                      deadline: new Date(deadlineInput).toISOString()
                    });
                    showToast('마감일이 설정되었습니다.', 'success');
                    setShowDeadlineModal(false);
                    fetchMaterials();
                  } catch (error) {
                    showToast(error.response?.data?.message || '마감일 설정 실패', 'danger');
                  } finally {
                    setSettingDeadline(false);
                  }
                }}
                disabled={settingDeadline}
              >
                {settingDeadline ? '설정 중...' : '설정'}
              </button>
            </div>
          </div>
        </div>
      )}

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
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleView(material.material_id, material.file_name)}
                  >
                    보기
                  </button>
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
            {user?.role === 'professor' && <><br />위의 업로드 영역에서 PDF를 업로드하세요.</>}
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
                <option value="score">점수순</option>
              </select>
            </div>

            <div className="materials-list">
              {studentMaterials.map((material) => (
                <div key={material.material_id} className="material-item">
                  <div className="material-info">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div className="material-name">{material.file_name}</div>
                      {material.quality_score !== null && material.quality_score !== undefined && (
                        <span style={{
                          backgroundColor: material.quality_score >= 8 ? '#4caf50' : 
                                         material.quality_score >= 6 ? '#ff9800' : '#f44336',
                          color: 'white',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.85rem',
                          fontWeight: 'bold'
                        }}>
                          ⭐ {material.quality_score.toFixed(1)}
                        </span>
                      )}
                    </div>
                    <div className="material-meta">
                      {material.uploader_name} | {new Date(material.upload_date).toLocaleString()} |
                      페이지: {material.page_count} | 👁️ {material.view_count} | ⬇️{' '}
                      {material.download_count}
                    </div>
                  </div>
                  <div className="material-actions">
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleView(material.material_id, material.file_name)}
                    >
                      보기
                    </button>
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

