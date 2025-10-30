# -*- coding: utf-8 -*-
"""
인증 관련 라우트 (로그인, 로그아웃)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.data_service import DataService

auth_bp = Blueprint('auth', __name__)
data_service = DataService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = data_service.authenticate_user(email, password)
        
        if user:
            # 세션 설정
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']
            
            flash(f'{user["name"]}님 환영합니다!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('이메일 또는 비밀번호가 올바르지 않습니다.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """회원가입 (데모에서는 사용 안 함)"""
    if request.method == 'POST':
        flash('데모 버전에서는 회원가입을 지원하지 않습니다. 미리 등록된 계정을 사용해주세요.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

