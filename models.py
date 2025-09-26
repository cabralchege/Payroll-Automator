from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# Create SQLAlchemy instance here
db = SQLAlchemy()

# User auth
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)  
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    employees = db.relationship('Employee', backref='owner', lazy=True)

    # Login helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.String(20), primary_key=True)
    kra_pin = db.Column(db.String(15), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    basic_salary = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    # owner = db.relationship("User", back_populates="employees")

    # Relationship
    # payrolls = db.relationship('Payroll', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    def full_name(self):
        names = [self.first_name]
        if self.middle_name and self.middle_name.strip():
            names.append(self.middle_name)
        names.append(self.last_name)
        return " ".join(names)
    
    def __repr__(self):
        return f'<Employee {self.id}: {self.full_name()}>'

class Payroll(db.Model):
    __tablename__ = 'payroll'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), db.ForeignKey('employees.id'), nullable=False)
    period = db.Column(db.String(7), nullable=False)  # YYYY-MM
    gross_salary = db.Column(db.Float, nullable=False)
    nssf = db.Column(db.Float, nullable=False)
    ahl = db.Column(db.Float, nullable=False)
    shif = db.Column(db.Float, nullable=False)
    paye = db.Column(db.Float, nullable=False)
    net_pay = db.Column(db.Float, nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship("Employee", backref="payrolls")

    def __repr__(self):
        return f'<Payroll {self.employee_id} - {self.period}>'