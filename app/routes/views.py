from flask import Blueprint, render_template, redirect, url_for

views_bp = Blueprint('views', __name__)


@views_bp.route('/')
def index():
    """Redirect root path to login or dashboard."""
    return redirect(url_for('views.dashboard_view'))


@views_bp.route('/login')
def login_view():
    """Renders Login page."""
    return render_template('login.html')


@views_bp.route('/dashboard')
def dashboard_view():
    """Renders Main Operational Dashboard."""
    return render_template('dashboard.html', active_page='dashboard')


@views_bp.route('/students')
def students_view():
    """Renders Student Management page."""
    return render_template('students.html', active_page='students')


@views_bp.route('/allocations')
def allocations_view():
    """Renders Allocation Lifecycle page."""
    return render_template('allocations.html', active_page='allocations')


@views_bp.route('/finance')
def finance_view():
    """Renders Finance & Fee Collection page."""
    return render_template('finance.html', active_page='finance')


@views_bp.route('/visitors')
def visitors_view():
    """Renders Gate Security Visitor Management page."""
    return render_template('visitors.html', active_page='visitors')


@views_bp.route('/complaints')
def complaints_view():
    """Renders Grievance Complaints page."""
    return render_template('complaints.html', active_page='complaints')


@views_bp.route('/maintenance')
def maintenance_view():
    """Renders Maintenance & Repair Request page."""
    return render_template('maintenance.html', active_page='maintenance')


@views_bp.route('/reports')
def reports_view():
    """Renders Business Intelligence Reports page."""
    return render_template('reports.html', active_page='reports')
