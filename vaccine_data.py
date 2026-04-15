# Approximation of CDC/WHO vaccination schedule
# Keys are age in months, values are lists of vaccine names.

VACCINE_SCHEDULE = {
    0: ["Hepatitis B (1st Dose)"],
    1: ["Hepatitis B (2nd Dose)"],
    2: [
        "Rotavirus (1st Dose)",
        "DTaP (1st Dose)",
        "Hib (1st Dose)",
        "Pneumococcal conjugate (1st Dose)",
        "Inactivated poliovirus (1st Dose)"
    ],
    4: [
        "Rotavirus (2nd Dose)",
        "DTaP (2nd Dose)",
        "Hib (2nd Dose)",
        "Pneumococcal conjugate (2nd Dose)",
        "Inactivated poliovirus (2nd Dose)"
    ],
    6: [
        "Hepatitis B (3rd Dose)",
        "DTaP (3rd Dose)",
        "Pneumococcal conjugate (3rd Dose)",
        "Inactivated poliovirus (3rd Dose)",
        "Influenza (Yearly)"
    ],
    12: [
        "Hib (3rd Dose)",
        "Pneumococcal conjugate (4th Dose)",
        "MMR (1st Dose)",
        "VAR (1st Dose)",
        "Hepatitis A (1st Dose)"
    ],
    15: [
        "DTaP (4th Dose)"
    ],
    18: [
        "Hepatitis A (2nd Dose)"
    ],
    48: [
        "DTaP (5th Dose)",
        "Inactivated poliovirus (4th Dose)",
        "MMR (2nd Dose)",
        "VAR (2nd Dose)"
    ],
    132: [ # 11-12 years
        "Meningococcal (1st Dose)",
        "Tdap",
        "HPV (1st Dose)"
    ],
    138: [ # Approx 11.5 years (6 months after HPV 1)
        "HPV (2nd Dose)"
    ],
    192: [ # 16 years
        "Meningococcal (2nd Dose)"
    ]
}

def generate_vaccine_records(child):
    from models import VaccineRecord
    from dateutil.relativedelta import relativedelta
    import datetime

    records = []
    for months, vaccines in VACCINE_SCHEDULE.items():
        # Calculate the due date based on the child's DOB and the required age (in months)
        due_date = child.dob + relativedelta(months=months)
        for vaccine_name in vaccines:
            record = VaccineRecord(
                child_id=child.id,
                vaccine_name=vaccine_name,
                due_date=due_date,
                completed=False
            )
            records.append(record)
    return records
