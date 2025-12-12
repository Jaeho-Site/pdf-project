/**
 * 파일명 유틸리티 함수 테스트
 * 실제 프로젝트에서 사용하는 sanitizeFileName과 getUniqueFileName 로직 테스트
 */

import { test, describe } from 'node:test';
import assert from 'node:assert';

// 실제 프로젝트에서 사용하는 함수들을 복사하여 테스트
const sanitizeFileName = (fileName) => {
  // 파일명에서 특수문자 제거 (한글, 영문, 숫자만 허용, 공백 제거)
  return fileName.replace(/[^가-힣a-zA-Z0-9]/g, '').trim();
};

const getUniqueFileName = (baseFileName) => {
  const sanitized = sanitizeFileName(baseFileName);
  let fileName = sanitized.endsWith('.pdf') ? sanitized : `${sanitized}.pdf`;
  let counter = 1;
  
  // 다운로드 폴더에 같은 이름의 파일이 있는지 확인 (localStorage 사용)
  // 테스트 환경에서는 localStorage 대신 빈 배열 사용
  const downloadHistory = [];
  
  while (downloadHistory.some(item => item.fileName === fileName)) {
    const nameWithoutExt = sanitized.replace(/\.pdf$/i, '');
    fileName = `${nameWithoutExt}(${counter}).pdf`;
    counter++;
  }
  
  return fileName;
};

describe('파일명 유틸리티 함수 테스트', () => {
  beforeEach(() => {
    // 각 테스트 전에 localStorage 초기화
    localStorage.clear();
  });

  describe('sanitizeFileName', () => {
    test('한글, 영문, 숫자만 남기고 특수문자 제거', () => {
      assert.strictEqual(sanitizeFileName('강의명+주차+학생명.pdf'), '강의명주차학생명pdf');
      assert.strictEqual(sanitizeFileName('test@file#name$123.pdf'), 'testfilename123pdf');
      assert.strictEqual(sanitizeFileName('  공백제거테스트  '), '공백제거테스트');
    });

    test('한글 파일명 처리', () => {
      assert.strictEqual(sanitizeFileName('심화프로젝트랩'), '심화프로젝트랩');
      assert.strictEqual(sanitizeFileName('나만의자료'), '나만의자료');
    });

    test('영문과 숫자 조합 처리', () => {
      assert.strictEqual(sanitizeFileName('Course123Week5'), 'Course123Week5');
      assert.strictEqual(sanitizeFileName('file-name_123'), 'filename123');
    });

    test('빈 문자열 처리', () => {
      assert.strictEqual(sanitizeFileName(''), '');
      assert.strictEqual(sanitizeFileName('   '), '');
    });
  });

  describe('getUniqueFileName', () => {
    test('기본 파일명에 .pdf 확장자 추가', () => {
      assert.strictEqual(getUniqueFileName('testfile'), 'testfile.pdf');
      assert.strictEqual(getUniqueFileName('강의자료'), '강의자료.pdf');
    });

    test('이미 .pdf 확장자가 있으면 그대로 유지', () => {
      assert.strictEqual(getUniqueFileName('testfile.pdf'), 'testfile.pdf');
    });

    test('실제 프로젝트 파일명 형식 테스트', () => {
      // "강의명+주차+학생명" 형식
      const courseName = sanitizeFileName('심화프로젝트랩');
      const week = '1';
      const studentName = sanitizeFileName('홍길동');
      const baseFileName = `${courseName}${week}주차${studentName}`;
      
      assert.strictEqual(baseFileName, '심화프로젝트랩1주차홍길동');
      assert.strictEqual(getUniqueFileName(baseFileName), '심화프로젝트랩1주차홍길동.pdf');
    });

    test('나만의 자료 파일명 형식 테스트', () => {
      const courseName = sanitizeFileName('심화프로젝트랩');
      const week = '2';
      const baseFileName = `${courseName}${week}주차나만의자료`;
      
      assert.strictEqual(baseFileName, '심화프로젝트랩2주차나만의자료');
      assert.strictEqual(getUniqueFileName(baseFileName), '심화프로젝트랩2주차나만의자료.pdf');
    });
  });
});

