import json
import random
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_random_value(min_val, max_val, decimals=2):
    return round(random.uniform(min_val, max_val), decimals)

def generate_report_from_json(json_data, output_filename):
    
    pdf = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    
    title = Paragraph("Test Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    
    patient_details = [
        ["Name", json_data["Patient_details"]["name"]["S"]],
        ["Gender", json_data["Patient_details"]["gender"]["S"]],
        ["Age", json_data["Patient_details"]["age"]["N"]],
        ["Reported", json_data["visit_details"]["Date_of_Visit"]["S"]],
        ["Lab No.", json_data["visit_details"]["visit_id"]["S"]],
        ["Collected", json_data["visit_details"]["Date_of_Visit"]["S"]],
        ["A/c Status", "Final"],
        ["Collected at", json_data["visit_details"]["Hospital_Name"]["S"]],
        ["Processed at", "National Reference laboratory, Block E, Sector 18, ROHINI, DELHI 110085"],
    ]

    patient_table = Table(patient_details, colWidths=[120, 350])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(patient_table)
    elements.append(Spacer(1, 24))

    # Test results with random values
    test_results = [
        ["Test Name", "Results", "Units", "Bio. Ref. Interval"],
        ["Hemoglobin", generate_random_value(13.0, 17.0), "g/dL", "13.00 - 17.00"],
        ["Packed Cell Volume (PCV)", generate_random_value(40.0, 50.0), "%", "40.00 - 50.00"],
        ["RBC Count", generate_random_value(4.5, 5.5), "mill/mm3", "4.50 - 5.50"],
        ["MCV", generate_random_value(83.0, 101.0), "fL", "83.00 - 101.00"],
        ["MCH", generate_random_value(27.0, 32.0), "pg", "27.00 - 32.00"],
        ["MCHC", generate_random_value(31.5, 34.5), "g/dL", "31.50 - 34.50"],
        ["Red Cell Distribution Width (RDW)", generate_random_value(11.6, 14.0), "%", "11.60 - 14.00"],
        ["Total Leukocyte Count (TLC)", generate_random_value(4.0, 10.0), "thou/mm3", "4.00 - 10.00"],
        ["Segmented Neutrophils", generate_random_value(40.0, 80.0), "%", "40.00 - 80.00"],
        ["Lymphocytes", generate_random_value(20.0, 40.0), "%", "20.00 - 40.00"],
        ["Monocytes", generate_random_value(2.0, 10.0), "%", "2.00 - 10.00"],
        ["Eosinophils", generate_random_value(1.0, 6.0), "%", "1.00 - 6.00"],
        ["Basophils", generate_random_value(0.0, 2.0), "%", "<2.00"],
        ["Neutrophils", generate_random_value(2.0, 7.0), "thou/mm3", "2.00 - 7.00"],
        ["Lymphocytes", generate_random_value(1.0, 3.0), "thou/mm3", "1.00 - 3.00"],
        ["Monocytes", generate_random_value(0.2, 1.0), "thou/mm3", "0.20 - 1.00"],
        ["Eosinophils", generate_random_value(0.02, 0.5), "thou/mm3", "0.02 - 0.50"],
        ["Basophils", generate_random_value(0.02, 0.1), "thou/mm3", "0.02 - 0.10"],
        ["Platelet Count", generate_random_value(150, 410), "thou/mm3", "150.00 - 410.00"],
        ["Mean Platelet Volume", generate_random_value(6.5, 12.0), "fL", "6.5 - 12.0"],
    ]

    test_table = Table(test_results, colWidths=[200, 100, 100, 150])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(test_table)
    elements.append(Spacer(1, 24))

    
    report_comments = json_data["visit_details"].get("report_comments", "")
    notes = [
        "Notes:",
        report_comments
    ]

    for note in notes:
        elements.append(Paragraph(note, styles['Normal']))
        elements.append(Spacer(1, 12))

    # Disclaimer
    disclaimer = "Disclaimer: This report is not real and is generated for demo purposes only."
    elements.append(Paragraph(disclaimer, styles['Italic']))
    elements.append(Spacer(1, 24))

    # Build the PDF
    pdf.build(elements)

if __name__ == "__main__":
    input_dir = 'generated_json'
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r') as file:
                json_data = json.load(file)
            # Extract patient_id and date_of_visit to create the output filename
            patient_id = json_data["Patient_details"]["patient_id"]["S"]
            date_of_visit = json_data["visit_details"]["Date_of_Visit"]["S"]
            # Generate the report filename
            output_filename = os.path.join(input_dir, f"{patient_id}_{date_of_visit}.pdf")
            print(output_filename)
            # Generate the report
            generate_report_from_json(json_data, output_filename)

    print("Reports have been generated successfully.")
