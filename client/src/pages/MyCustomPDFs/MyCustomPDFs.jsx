import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { showToast } from '../../components/Toast/Toast';
import api from '../../utils/api';
import './MyCustomPDFs.css';

const MyCustomPDFs = () => {
  const { user } = useAuth();
  const [customPdfs, setCustomPdfs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomPdfs();
  }, []);

  const fetchCustomPdfs = async () => {
    try {
      const response = await api.get('/custom-pdfs/my-list');
      setCustomPdfs(response.data.custom_pdfs || []);
    } catch (error) {
      console.error('나만의 PDF 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (customPdfId, fileName) => {
    try {
      const response = await api.get(`/custom-pdfs/${customPdfId}/download`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      showToast('다운로드 완료!', 'success');
    } catch (error) {
      showToast('다운로드 실패', 'danger');
    }
  };

  if (loading) {
    return <div className="container">로딩 중...</div>;
  }

  return (
    <div>
      <div className="page-header-custom-list">
        <div className="page-title-custom-list">✨ 나만의 필기 만들기</div>
        <div style={{ opacity: 0.9 }}>내가 만든 커스텀 PDF 목록</div>
      </div>

      {customPdfs.length > 0 ? (
        <div className="custom-pdfs-list">
          {customPdfs.map((pdf) => (
            <div key={pdf.custom_pdf_id} className="custom-pdf-card">
              <div className="pdf-header">
                <div style={{ flex: 1 }}>
                  <div className="pdf-title">{pdf.file_name}</div>
                  <div className="pdf-meta">
                    📚 {pdf.course_name} - {pdf.week}주차 |
                    📅 {new Date(pdf.created_at).toLocaleString()}
                  </div>
                </div>
                <div>
                  <button
                    className="btn btn-primary"
                    onClick={() => handleDownload(pdf.custom_pdf_id, pdf.file_name)}
                  >
                    다운로드
                  </button>
                </div>
              </div>

              <div className="page-selections">
                <div className="page-selections-title">
                  📄 선택한 페이지 ({pdf.page_selections?.length || 0}개)
                </div>
                <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
                  {pdf.page_selections?.map((selection, index) => (
                    <div key={index} className="page-selection-item">
                      {index + 1}. {selection.source_student_name}님의 {selection.page_num}페이지
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">📚</div>
          <p style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
            아직 만든 나만의 필기가 없습니다.
          </p>
          <p>
            강의 자료실에서 여러 학생들의 필기를 조합하여
            <br />
            나만의 완벽한 필기 자료를 만들어보세요!
          </p>
          <p style={{ marginTop: '2rem' }}>
            <button className="btn btn-primary" onClick={() => window.location.href = '/'}>
              강의 목록으로 이동
            </button>
          </p>
        </div>
      )}
    </div>
  );
};

export default MyCustomPDFs;

