import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { showToast } from '../../components/Toast/Toast';
import api from '../../utils/api';
import './CreateCustomPDF.css';

const CreateCustomPDF = () => {
  const { courseId, week } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [selectedPages, setSelectedPages] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [modalImage, setModalImage] = useState('');
  const [generating, setGenerating] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [currentStudentIndex, setCurrentStudentIndex] = useState(0);

  useEffect(() => {
    fetchMaterials();
  }, [courseId, week]);

  const fetchMaterials = async () => {
    try {
      const response = await api.get(`/api/courses/${courseId}/week/${week}/create-custom`);
      setCourse(response.data.course);
      setMaterials(response.data.materials || []);
    } catch (error) {
      console.error('자료 조회 실패:', error);
      const errorMessage = error.response?.data?.message || '자료를 불러올 수 없습니다.';
      showToast(errorMessage, 'danger');
      if (error.response?.status === 403) {
        // 마감일이 지나지 않았으면 이전 페이지로
        setTimeout(() => {
          navigate(`/courses/${courseId}/week/${week}`);
        }, 2000);
      }
    }
  };

  const handlePageToggle = (materialId, pageNum, studentName) => {
    const index = selectedPages.findIndex(
      (p) => p.material_id === materialId && p.page_num === pageNum
    );

    if (index >= 0) {
      // 선택 해제
      setSelectedPages(selectedPages.filter((_, i) => i !== index));
    } else {
      // 선택
      setSelectedPages([
        ...selectedPages,
        { material_id: materialId, page_num: pageNum, student_name: studentName },
      ]);
    }
  };

  const isPageSelected = (materialId, pageNum) => {
    return selectedPages.some(
      (p) => p.material_id === materialId && p.page_num === pageNum
    );
  };

  const handleGeneratePDF = async () => {
    if (selectedPages.length === 0) {
      showToast('페이지를 하나 이상 선택해주세요!', 'warning');
      return;
    }

    if (!window.confirm(`선택한 ${selectedPages.length}개의 페이지로 PDF를 생성하시겠습니까?`)) {
      return;
    }

    setGenerating(true);

    try {
      const response = await api.post(
        `/api/courses/${courseId}/week/${week}/generate-custom`,
        { selected_pages: selectedPages }
      );

      if (response.data.success) {
        showToast('✅ ' + response.data.message, 'success');
        navigate('/my-custom-pdfs');
      } else {
        showToast('❌ ' + response.data.message, 'danger');
      }
    } catch (error) {
      showToast('PDF 생성에 실패했습니다.', 'danger');
      console.error('PDF 생성 오류:', error);
    } finally {
      setGenerating(false);
    }
  };

  const clearSelection = () => {
    setSelectedPages([]);
  };

  const showImageModal = (imageSrc) => {
    setModalImage(imageSrc);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setModalImage('');
  };

  if (!course || materials.length === 0) {
    return (
      <div className="container">
        <p>로딩 중...</p>
      </div>
    );
  }

  // 최대 페이지 수 계산
  const maxPages = Math.max(...materials.map((m) => m.page_count));

  // 페이지 네비게이션
  const goToPreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
      setCurrentStudentIndex(0);
    }
  };

  const goToNextPage = () => {
    if (currentPage < maxPages) {
      setCurrentPage(currentPage + 1);
      setCurrentStudentIndex(0);
    }
  };

  // 학생 슬라이더 네비게이션
  const goToPreviousStudent = () => {
    if (currentStudentIndex > 0) {
      setCurrentStudentIndex(currentStudentIndex - 1);
    }
  };

  const goToNextStudent = () => {
    if (currentStudentIndex < materials.length - 1) {
      setCurrentStudentIndex(currentStudentIndex + 1);
    }
  };

  const currentMaterial = materials[currentStudentIndex];
  const hasPage = currentMaterial && currentPage <= currentMaterial.page_count;
  const isSelected = hasPage && isPageSelected(currentMaterial.material_id, currentPage);

  return (
    <div>
      <div className="page-header-custom">
        <div className="page-title-custom">✨ 나만의 필기 만들기</div>
        <div className="page-subtitle">
          {course.course_name} - {week}주차 | 마음에 드는 페이지를 선택하여 조합하세요
        </div>
      </div>

      <div className="instructions">
        <strong>📌 사용방법:</strong>
        <br />
        1. 각 학생의 필기에서 원하는 페이지를 클릭하여 선택하세요.
        <br />
        2. 선택한 페이지는 선택 순서대로 하나의 PDF로 합쳐집니다.
        <br />
        3. 이미지를 클릭하면 크게 미리볼 수 있습니다.
        <br />
        4. ⭐ 점수가 높은 필기가 먼저 표시됩니다.
      </div>

      {/* 페이지 네비게이션 */}
      <div className="page-navigation">
        <button
          className="btn btn-nav"
          onClick={goToPreviousPage}
          disabled={currentPage === 1}
        >
          ← 이전 페이지
        </button>
        <div className="page-indicator">
          <strong>페이지 {currentPage}</strong> / {maxPages}
        </div>
        <button
          className="btn btn-nav"
          onClick={goToNextPage}
          disabled={currentPage === maxPages}
        >
          다음 페이지 →
        </button>
      </div>

      {/* 수평 슬라이더 */}
      <div className="slider-container">
        <button
          className="slider-nav-btn slider-nav-left"
          onClick={goToPreviousStudent}
          disabled={currentStudentIndex === 0}
        >
          ‹
        </button>

        <div className="slider-content">
          {currentMaterial && (
            <div className="student-slide">
              <div style={{ 
                marginBottom: '0.5rem', 
                textAlign: 'center',
                fontWeight: 'bold',
                fontSize: '1.1rem'
              }}>
                {currentMaterial.uploader_name}
                {currentMaterial.quality_score !== null && currentMaterial.quality_score !== undefined && (
                  <span style={{
                    marginLeft: '0.5rem',
                    backgroundColor: currentMaterial.quality_score >= 8 ? '#4caf50' : 
                                   currentMaterial.quality_score >= 6 ? '#ff9800' : '#f44336',
                    color: 'white',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.9rem',
                    fontWeight: 'bold'
                  }}>
                    ⭐ {currentMaterial.quality_score.toFixed(1)}
                  </span>
                )}
              </div>
              {hasPage ? (
                <div
                  className={`page-preview-slider ${isSelected ? 'selected' : ''}`}
                  onClick={() =>
                    handlePageToggle(
                      currentMaterial.material_id,
                      currentPage,
                      currentMaterial.uploader_name
                    )
                  }
                >
                  <input
                    type="checkbox"
                    className="page-checkbox-slider"
                    checked={isSelected}
                    onChange={() => {}}
                  />
                  <img
                    src={`/api/storage/thumbnails/${currentMaterial.material_id}/page_${currentPage}.jpg`}
                    alt={`Page ${currentPage}`}
                    className="page-image-slider"
                    onClick={(e) => {
                      e.stopPropagation();
                      showImageModal(e.target.src);
                    }}
                  />
                  {isSelected && (
                    <div className="selection-badge-slider">
                      ✓ 선택됨 (순서: {selectedPages.findIndex(
                        p => p.material_id === currentMaterial.material_id && p.page_num === currentPage
                      ) + 1})
                    </div>
                  )}
                </div>
              ) : (
                <div className="no-page-slider">
                  <p>이 학생은 {currentPage}페이지가 없습니다</p>
                </div>
              )}
            </div>
          )}
        </div>

        <button
          className="slider-nav-btn slider-nav-right"
          onClick={goToNextStudent}
          disabled={currentStudentIndex === materials.length - 1}
        >
          ›
        </button>
      </div>

      {/* 학생 인디케이터 도트 */}
      <div className="student-indicators">
        {materials.map((material, index) => (
          <button
            key={material.material_id}
            className={`indicator-dot ${index === currentStudentIndex ? 'active' : ''}`}
            onClick={() => setCurrentStudentIndex(index)}
            title={material.uploader_name}
          />
        ))}
      </div>

      {/* 하단 액션 바 */}
      <div className="action-bar">
        <div className="selected-count">
          선택된 페이지: <span>{selectedPages.length}</span>개
        </div>
        <button className="btn btn-secondary" onClick={clearSelection}>
          선택 초기화
        </button>
        <button
          className="btn btn-success"
          onClick={handleGeneratePDF}
          disabled={generating}
        >
          {generating ? '생성 중...' : '📄 나만의 PDF 생성'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => navigate(`/courses/${courseId}/week/${week}`)}
        >
          취소
        </button>
      </div>

      {/* 이미지 모달 */}
      {showModal && (
        <div className="modal" onClick={closeModal}>
          <span className="modal-close">&times;</span>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <img src={modalImage} alt="Preview" />
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateCustomPDF;

