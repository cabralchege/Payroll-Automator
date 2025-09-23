def calculate_nssf(gross_salary):
    """Calculate NSSF deduction (employee contribution) - 2025 rates"""
    tier1_limit = 8000
    tier2_limit = 72000
    rate = 0.06
    
    tier1 = min(gross_salary, tier1_limit) * rate  # Max: 480
    tier2 = max(0, min(gross_salary - tier1_limit, tier2_limit - tier1_limit)) * rate
    return round(min(tier1 + tier2, 4320), 2)  # Cap at 4,320

def calculate_shif(basic_salary):
    """Calculate SHIF deduction - 2.75% of gross, minimum 300"""
    shif_rate = 0.0275
    return round(max(basic_salary * shif_rate, 300), 2)

def calculate_ahl(gross_salary):
    """Calculate Affordable Housing Levy - 1.5% of gross"""
    return round(gross_salary * 0.015, 2)

def calculate_paye(taxable_pay):
    """Calculate PAYE tax after personal relief - 2025 rates"""
    personal_relief = 2400
    
    if taxable_pay <= 24000:
        tax = taxable_pay * 0.1
    elif taxable_pay <= 32333:
        tax = 2400 + (taxable_pay - 24000) * 0.25
    elif taxable_pay <= 500000:
        tax = 2400 + (32333 - 24000) * 0.25 + (taxable_pay - 32333) * 0.3
    elif taxable_pay <= 800000:
        tax = 2400+ (32333-24000) * 0.25 + (500000 - 32333) * 0.3 + (taxable_pay - 467000) * 0.325
    else:
        tax = 2400 + (32333-2400) * 0.25 +(500000-32333) * 0.3 + (800000 - 500000)* 0.325+ (taxable_pay - 800000) * 0.35
    return round(max(tax - personal_relief, 0), 2)

def calculate_payroll(employee_data, period):
    """Calculate complete payroll with all Kenyan statutory deductions"""
    # Calculate gross salary
    basic_salary = employee_data['basic_salary']
    benefits_total = sum(benefit['amount'] for benefit in employee_data['benefits'])
    gross_salary = employee_data['basic_salary'] + benefits_total
    
    # Statutory deductions
    nssf = calculate_nssf(gross_salary)
    ahl = calculate_ahl(gross_salary)
    shif = calculate_shif(basic_salary)

    # Taxable pay
    taxable_pay = gross_salary - nssf - ahl
    
    # PAYE
    paye = calculate_paye(taxable_pay)
    
    # Net pay
    total_deductions = nssf + ahl + paye + shif
    net_pay = gross_salary - total_deductions
    
    return {
        'period': period,
        'gross_salary': round(gross_salary, 2),
        'benefits_total': round(benefits_total, 2),
        'nssf': nssf,
        'ahl': ahl,
        'taxable_pay': round(taxable_pay, 2),
        'paye': paye,
        'shif': shif,
        'total_deductions': round(total_deductions, 2),
        'net_pay': round(net_pay, 2)
    }

# # Test the calculator
# if __name__ == "__main__":
#     test_data = {
#         'basic_salary': 40000,
#         'benefits': [{'amount': 10000}]
#     }
#     result = calculate_payroll(test_data, "2025-09")
#     print("Test Payroll Calculation:")
#     for key, value in result.items():
#         if isinstance(value, (int, float)):
#             print(f"{key}: KSh {value:,.2f}")
#         else:
#             print(f"{key}: {value}")