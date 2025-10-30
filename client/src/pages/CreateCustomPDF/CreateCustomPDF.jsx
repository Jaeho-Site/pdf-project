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

  useEffect(() => {
    fetchMaterials();
  }, [courseId, week]);

  const fetchMaterials = async () => {
    try {
      const response = await api.get(`/courses/${courseId}/week/${week}/create-custom`);
      setCourse(response.data.course);
      setMaterials(response.data.materials || []);
    } catch (error) {
      console.error('자료 조회 실패:', error);
      showToast('자료를 불러올 수 없습니다.', 'danger');
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
        `/courses/${courseId}/week/${week}/generate-custom`,
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
      </div>

      <div className="matrix-container">
        <table className="page-matrix">
          <thead>
            <tr>
              <th className="student-name-cell">학생</th>
              {Array.from({ length: maxPages }, (_, i) => (
                <th key={i}>페이지 {i + 1}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {materials.map((material) => (
              <tr key={material.material_id}>
                <td className="student-name-cell">
                  {material.uploader_name}
                  <br />
                  <span style={{ fontSize: '0.85rem', color: '#666' }}>
                    ({material.uploader_id})
                  </span>
                </td>
                {Array.from({ length: maxPages }, (_, pageIndex) => {
                  const pageNum = pageIndex + 1;
                  const hasPage = pageNum <= material.page_count;
                  const isSelected = isPageSelected(material.material_id, pageNum);

                  return (
                    <td key={pageNum}>
                      {hasPage ? (
                        <div
                          className={`page-preview ${isSelected ? 'selected' : ''}`}
                          onClick={() =>
                            handlePageToggle(
                              material.material_id,
                              pageNum,
                              material.uploader_name
                            )
                          }
                        >
                          <input
                            type="checkbox"
                            className="page-checkbox"
                            checked={isSelected}
                            onChange={() => {}}
                          />
                          <img
                            src={`/api/storage/thumbnails/${material.material_id}/page_${pageNum}.jpg`}
                            alt={`Page ${pageNum}`}
                            className="page-image"
                            onClick={(e) => {
                              e.stopPropagation();
                              showImageModal(e.target.src);
                            }}
                          />
                          <div className="page-number">{pageNum}</div>
                        </div>
                      ) : (
                        <div style={{ color: '#ccc', textAlign: 'center' }}>-</div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
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

