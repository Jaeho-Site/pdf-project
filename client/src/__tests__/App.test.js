import { test, describe } from "node:test";
import assert from "node:assert";

describe("기본 기능 테스트", () => {
  test("기본 타입 검증", () => {
    assert.strictEqual(typeof "string", "string");
    assert.strictEqual(typeof 123, "number");
    assert.strictEqual(typeof true, "boolean");
  });

  test("파일명 형식 검증", () => {
    const courseName = "심화프로젝트랩";
    const week = "1";
    const studentName = "홍길동";
    const fileName = `${courseName}${week}주차${studentName}.pdf`;

    assert.strictEqual(fileName, "심화프로젝트랩1주차홍길동.pdf");
    assert.ok(fileName.endsWith(".pdf"));
  });

  test("날짜 형식 검증", () => {
    const date = new Date();
    const isoString = date.toISOString();

    assert.ok(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(isoString));
  });
});
