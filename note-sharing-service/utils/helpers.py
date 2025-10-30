# -*- coding: utf-8 -*-
"""
헬퍼 함수
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from datetime import datetime

def login_required(f):
    """로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def professor_required(f):
    """교수 권한 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'professor':
            flash('교수만 접근할 수 있습니다.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """학생 권한 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'student':
            flash('학생만 접근할 수 있습니다.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def format_datetime(dt_str: str) -> str:
    """ISO 형식 datetime 문자열을 한국어 형식으로 변환"""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%Y년 %m월 %d일 %H:%M')
    except:
        return dt_str

def format_date(dt_str: str) -> str:
    """ISO 형식 datetime 문자열을 날짜만 표시"""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%Y-%m-%d')
    except:
        return dt_str

def format_filesize(size_bytes: int) -> str:
    """파일 크기를 읽기 쉬운 형식으로 변환"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

