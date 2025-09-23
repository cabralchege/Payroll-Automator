from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create SQLAlchemy instance here
db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.String(20), primary_key=True)
    kra_pin = db.Column(db.String(15), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    basic_salary = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    payrolls = db.relationship('Payroll', backref='employee', lazy=True, cascade='all, delete-orphan')
    
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
    paye = db.Column(db.Float, nullable=False)
    shif = db.Column(db.Float, nullable=False)
    net_pay = db.Column(db.Float, nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payroll {self.employee_id} - {self.period}>'