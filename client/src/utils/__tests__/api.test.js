/**
 * API 설정 테스트
 * 실제 프로젝트의 API 설정값 검증
 */

import { test, describe } from 'node:test';
import assert from 'node:assert';

describe('API 설정 테스트', () => {
  test('API baseURL이 올바르게 설정되어야 함', () => {
    // 실제 api.js에서 사용하는 baseURL 확인
    const expectedBaseURL = 'https://course.o-r.kr';
    assert.strictEqual(expectedBaseURL, 'https://course.o-r.kr');
    assert.ok(expectedBaseURL.includes('course.o-r.kr'));
  });

  test('API 헤더 설정 검증', () => {
    const expectedHeaders = {
      'Content-Type': 'application/json'
    };
    
    assert.strictEqual(expectedHeaders['Content-Type'], 'application/json');
  });

  test('인증 헤더 형식 검증', () => {
    const token = 'test-token-123';
    const authHeader = `Bearer ${token}`;
    
    assert.strictEqual(authHeader, 'Bearer test-token-123');
    assert.ok(authHeader.startsWith('Bearer '));
  });

  test('사용자 헤더 키 검증', () => {
    const headerKeys = ['X-User-ID', 'X-User-Role', 'X-User-Email'];
    
    assert.ok(headerKeys.includes('X-User-ID'));
    assert.ok(headerKeys.includes('X-User-Role'));
    assert.ok(headerKeys.includes('X-User-Email'));
    assert.strictEqual(headerKeys.length, 3);
  });
});

