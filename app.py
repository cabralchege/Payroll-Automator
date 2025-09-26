import os
import csv
import json
import re
import logging
from datetime import datetime
from io import StringIO, BytesIO
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from flask_login import login_manager, login_user, login_required, logout_user,current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash



# Import modules
from payroll_calculator import calculate_payroll
from generate_pdf import generate_payslip_pdf
from models import db, Employee, Payroll, User

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'automated-payroll-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payroll.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Initialize SQLAlchemy with the app
db.init_app(app)

# initializing login manager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        name = request.form.get('full_name', '').strip()

        if not email or not password:
            flash("Email and password required", "error")
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "error")
            return redirect(url_for('login'))

        user = User(email=email, full_name=name)
        user.set_password(password)
        # Optionally make the first created user admin
        if User.query.count() == 0:
            user.is_admin = True

        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials", "error")
            return render_template('login.html')
        login_user(user)
        flash("Logged in successfully", "success")
        return redirect(url_for('index'))
    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

# Create tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    period = request.args.get('period', f"{datetime.now().strftime('%Y-%m')}")
    if current_user.is_admin:
        employees = Employee.query.all()
    else:
        employees = Employee.query.filter_by(user_id=current_user.id).all()
    
    # Handle form submission
    if request.method == 'POST':
        # Get form data
        employee_id = request.form.get('employee_id', '').strip()
        kra_pin = request.form.get('kra_pin', '').strip()
        first_name = request.form.get('first_name', '').strip()
        middle_name = request.form.get('middle_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        basic_salary_str = request.form.get('basic_salary', '').strip()
        
        # Validate required fields
        if not all([employee_id, kra_pin, first_name, last_name, basic_salary_str]):
            flash('Please fill all required fields (* marked).', 'error')
            return render_template('index.html', employees=employees, period=period)
        
        # Validate salary
        try:
            basic_salary = float(basic_salary_str)
            if basic_salary < 0 :
                flash('Salary cannot be negative', 'error')
                return render_template('index.html', employees=employees, period=period)
        except ValueError:
            flash('Please enter a valid salary amount.', 'error')
            return render_template('index.html', employees=employees, period=period)
        
        # Validate KRA PIN format
        if not re.match(r'^A\d{9}[A-Z]$', kra_pin):
            flash('Invalid KRA PIN format. Use: AXXXXXXXXXX', 'error')
            return render_template('index.html', employees=employees, period=period)
        
        try:
            # Check if employee ID exists
            existing = Employee.query.filter_by(id=employee_id).first()
            if existing:
                flash('Employee ID already exists! Please use a different ID.', 'error')
                return render_template('index.html', employees=employees, period=period)
            
            # Create new employee
            employee = Employee(
                id=employee_id,
                kra_pin=kra_pin,
                first_name=first_name,
                middle_name=middle_name or '',
                last_name=last_name,
                basic_salary=basic_salary,
                user_id=current_user.id
            )
            db.session.add(employee)
            db.session.commit()
            
            # Parse benefits from JSON
            benefits_data = []
            benefits_json = request.form.get('benefits_data', '[]')
            try:
                benefits_list = json.loads(benefits_json)
                for benefit in benefits_list:
                    if benefit.get('name') and benefit.get('amount'):
                        try:
                            amount = float(benefit['amount'])
                            if amount > 0:
                                benefits_data.append({
                                    'name': benefit['name'][:50],  # Limit length
                                    'amount': amount
                                })
                        except ValueError:
                            continue
            except json.JSONDecodeError:
                pass  # No benefits or invalid JSON
            
            # Calculate payroll
            payroll_data = calculate_payroll({
                'basic_salary': basic_salary,
                'benefits': benefits_data
            }, period)
            
            # Save payroll record
            payroll = Payroll(
                employee_id=employee_id,
                period=period,
                gross_salary=float(payroll_data['gross_salary']),
                nssf=float(payroll_data['nssf']),
                shif=float(payroll_data['shif']),
                ahl=float(payroll_data['ahl']),
                paye=float(payroll_data['paye']),
              
                net_pay=float(payroll_data['net_pay'])
            )
            db.session.add(payroll)
            db.session.commit()
            
            flash(f'Employee {first_name} {last_name} added successfully!<br>Net Pay: KSh {payroll_data["net_pay"]:,.0f}', 'success')
            return redirect(url_for('index', period=period))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')
            print(f"Debug error: {e}")
    
    return render_template('index.html', employees=employees, period=period)

@app.route('/generate_payslip/<employee_id>/<period>')
def generate_payslip(employee_id, period):
    """Generate PDF payslip for specific employee."""
    try:
        logger.debug(f"Attempting to generate payslip for employee_id: {employee_id}, period: {period}")
        employee = Employee.query.get_or_404(employee_id)
        payroll = Payroll.query.filter_by(employee_id=employee_id, period=period).first()

        if not payroll:
            logger.warning(f"No payroll data found for employee {employee_id} in period {period}")
            flash('No payroll data found for this period. Please calculate payroll first.', 'error')
            return redirect(url_for('index'))
        
        if not current_user.is_admin and payroll.employee.user_id != current_user.id:
            flash('You are not authorized to view this payslip.', 'error')
            return redirect(url_for('index'))
        
        # Generate PDF
        pdf_buffer = generate_payslip_pdf(employee, payroll)
        logger.debug(f"Payslip PDF generated for {employee_id}")
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'payslip_{employee_id}_{period}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Error generating payslip for {employee_id}: {str(e)}", exc_info=True)
        flash(f'Error generating payslip: {str(e)}', 'error')
        return redirect(url_for('index'))
    
@app.route('/generate_p10/<period>')
def generate_p10(period):
    """Generate KRA P10 CSV report"""
    try:
        if current_user.is_admin or Employee.user_id == current_user.id:
            payroll_records = db.session.query(Payroll).join(Employee).filter(Payroll.period == period).all()
        else:
            payroll_records = db.session.query(Payroll).join(Employee).filter(
                Payroll.period == period, Employee.user_id == current_user.id).all()
        
        if not payroll_records:
            flash('No payroll data for this period', 'error')
            return redirect(url_for('index'))
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'PIN', 'Names', 'Gross_Pay', 'PAYE', 'NSSF', 
            'Other_Deductions', 'Taxable_Pay', 'Month_Year'
        ])
        
        # Data rows
        for payroll in payroll_records:
            employee = payroll.employee
            taxable_pay = payroll.gross_salary - payroll.nssf - payroll.ahl
            writer.writerow([
                employee.kra_pin,
                f'"{employee.first_name} {employee.middle_name} {employee.last_name}".strip()',
                f"{payroll.gross_salary:.2f}",
                f"{payroll.paye:.2f}",
                f"{payroll.nssf:.2f}",
                "0.00",
                f"{taxable_pay:.2f}",
                period
            ])
        
        # Summary row
        total_gross = sum(p.gross_salary for p in payroll_records)
        total_paye = sum(p.paye for p in payroll_records)
        writer.writerow([
            '', f'TOTAL ({len(payroll_records)} employees)',
            f"{total_gross:.2f}", f"{total_paye:.2f}", '', '', '', ''
        ])
        
        output.seek(0)
        filename = f'P10_Report_{period}.csv'
        
        return send_file(
            BytesIO(output.getvalue().encode('utf-8')),
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    except Exception as e:
        flash(f'Error generating P10 report: {str(e)}', 'error')
        print(f"P10 Error: {e}")
        return redirect(url_for('index'))

@app.route('/clear_employees', methods=['POST'])
@login_required
def clear_employees():
    try:
        if current_user.is_admin:
            # Admin: Delete all records from the Payroll table.
            deleted_count = db.session.query(Employee).delete()
            entity_name = "payroll"
        else:
            # Regular User: Delete only payrolls for employees they own.
            # This joins Payroll with Employee and filters by the current user's ID.
            deleted_count = db.session.query(Payroll).join(Employee).filter(
                Employee.user_id == current_user.id
            ).delete(synchronize_session=False)
            entity_name = "employee"
        db.session.commit() 
        flash("All employee records have been cleared.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error clearing employee records: {str(e)}", "error")
    return redirect(url_for('index'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)