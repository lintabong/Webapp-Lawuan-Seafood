
from flask import Blueprint, render_template
from app.helpers.auth import login_required

financial_report_bp = Blueprint('financial_report', __name__)

@financial_report_bp.route('/financial-report')
@login_required
def financial_report():
    return render_template('report.html')
