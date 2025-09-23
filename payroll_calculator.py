def calculate_nssf(gross_salary):
    """Calculation of NSSF deductions.
    Tier 1 limit is 480
    Total limit is 4320"""
    tier1_limit = 8000
    tier2_limit = 72000
    rate = 0.06
    tier1 = min(gross_salary, tier1_limit) * rate 
    tier2 = max(0, min(gross_salary - tier1_limit, tier2_limit - tier1_limit)) * rate
    return min(tier1 + tier2, 4320) 

def calculate_shif(basic_pay):
    """Calculation of SHIF deduction(2.75%). A minimum contribution of 300"""
    shif_rate = 0.0275
    return max(basic_pay * shif_rate, 300) 

def calculate_ahl(gross_salary):
    """Calculate Affordable Housing Levy deduction(1.5%)."""
    return gross_salary * 0.015

def calculate_paye(taxable_pay):
    """Calculate PAYE after personal relief. Note PAYE hould not be negative"""
    personal_relief = 2400
    if taxable_pay <= 24000:
        tax = taxable_pay * 0.1
    elif taxable_pay <= 32333:
        tax = 2400 + (taxable_pay - 24000) * 0.25
    elif taxable_pay <= 500000:
        tax = 2400 + 2083.25 + (taxable_pay - 32333) * 0.3
    elif taxable_pay <= 800000:
        tax = 2400 + 2083.25 + 140300.1 + (taxable_pay - 500000) * 0.325
    else:
        tax = 2400 + 2083.25 + 140300.1 + 97500 + (taxable_pay - 800000) * 0.35
    return round(max(tax - personal_relief, 0), 2)

def calculate_payroll_items(employee):
    """Calculate payroll deductions and net pay."""
    basic_pay = employee["basic_pay"]
    gross_salary = employee["basic_pay"] + sum(employee["benefits"].values())
    nssf = calculate_nssf(gross_salary)
    ahl = calculate_ahl(gross_salary)
    shif = calculate_shif(basic_pay)
    taxable_pay = gross_salary - nssf - ahl - shif
    paye = calculate_paye(taxable_pay)
    
    total_deductions = nssf + ahl + paye + shif
    net_pay = gross_salary - total_deductions
    return {
        "gross_salary": round(gross_salary, 2),
        "basic_pay": round(basic_pay, 2),
        "nssf": round(nssf, 2),
        "ahl": round (ahl, 2),
        "paye": round(paye, 2),
        "shif": round(shif, 2),
        "total_deductions": round(total_deductions, 2),
        "net_pay": round(net_pay, 2)
    }

def main():
    """A function that the user inputs employee details and calculates the payroll details"""
    employee = {"id": "", "name": "", "basic_pay": 0.0, "benefits": {}}
    
    # Input employee details
    try:
        employee["id"] = input("Enter Employee ID: ").strip()
        employee["name"] = input("Enter Employee Name: ").strip()
        employee["basic_pay"] = float(input("Enter Basic Pay (KSh): "))
        if employee["basic_pay"] < 0:
            raise ValueError("Basic pay cannot be negative.")
        
        # Add benefits
        while True:
            add_benefit = input("Add a benefit? (y/n): ").lower()
            if add_benefit != 'y':
                break
            benefit_name = input("Enter benefit name (e.g., Commissions): ").strip()
            benefit_amount = float(input(f"Enter amount for {benefit_name} (KSh): "))
            if benefit_amount < 0:
                raise ValueError("Benefit amount cannot be negative.")
            employee["benefits"][benefit_name] = benefit_amount
    
    except ValueError as e:
        print(f"Error: {e}. Please enter valid numeric values.")
        return
    
    # Calculate payroll and print payslip
    payroll = calculate_payroll_items(employee)
    print_payslip(employee, payroll)
