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
      const response = await api.get('/api/custom-pdfs/my-list');
      setCustomPdfs(response.data.custom_pdfs || []);
    } catch (error) {
      console.error('나만의 PDF 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 파일명에서 특수문자 제거 및 안전한 파일명 생성
  const sanitizeFileName = (fileName) => {
    // 파일명에서 특수문자 제거 (한글, 영문, 숫자만 허용, 공백 제거)
    return fileName.replace(/[^가-힣a-zA-Z0-9]/g, '').trim();
  };

  // 중복 파일명 처리
  const getUniqueFileName = (baseFileName) => {
    const sanitized = sanitizeFileName(baseFileName);
    let fileName = sanitized.endsWith('.pdf') ? sanitized : `${sanitized}.pdf`;
    let counter = 1;
    
    // 다운로드 폴더에 같은 이름의 파일이 있는지 확인 (localStorage 사용)
    const downloadHistory = JSON.parse(localStorage.getItem('downloadHistory') || '[]');
    
    while (downloadHistory.some(item => item.fileName === fileName)) {
      const nameWithoutExt = sanitized.replace(/\.pdf$/i, '');
      fileName = `${nameWithoutExt}(${counter}).pdf`;
      counter++;
    }
    
    return fileName;
  };

  const handleDownload = async (customPdfId, pdf) => {
    try {
      const response = await api.get(`/api/custom-pdfs/${customPdfId}/download`, {
        responseType: 'blob',
      });
      
      // 파일명 생성: "강의명+주차+나만의자료.pdf" (공백 없이)
      const courseName = pdf?.course_name || '알 수 없음';
      const pdfWeek = pdf?.week || 0;
      
      // 파일명 생성 (공백 없이, 특수문자 제거)
      const baseFileName = `${sanitizeFileName(courseName)}${pdfWeek}주차나만의자료`;
      const downloadFileName = getUniqueFileName(baseFileName);
      
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', downloadFileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      // 다운로드 기록 저장
      const downloadHistory = JSON.parse(localStorage.getItem('downloadHistory') || '[]');
      downloadHistory.unshift({
        fileName: downloadFileName,
        timestamp: new Date().toISOString(),
        size: response.data.size
      });
      // 최근 50개만 저장
      localStorage.setItem('downloadHistory', JSON.stringify(downloadHistory.slice(0, 50)));
      
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
                    onClick={() => handleDownload(pdf.custom_pdf_id, pdf)}
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

