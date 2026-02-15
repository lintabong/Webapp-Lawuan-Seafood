
from flask import (
    Blueprint, render_template, request, 
    redirect, session, url_for
)
from app.lib.supabase_client import supabase

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return redirect(url_for('web.main.login'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            res = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
        except Exception:
            return render_template(
                'login.html',
                error='Cant Login'
            )

        if res.session:
            session['access_token'] = res.session.access_token
            session['refresh_token'] = res.session.refresh_token
            session['expires_at'] = res.session.expires_at
            session['user'] = {
                'id': res.user.id,
                'email': res.user.email
            }
            return redirect('/dashboard')

        return render_template(
            'login.html',
            error='Wrong Email or Password'
        )

    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
