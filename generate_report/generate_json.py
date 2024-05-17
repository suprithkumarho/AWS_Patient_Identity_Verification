import json
import random
import os
from datetime import datetime, timedelta

# Patient details remain constant
patient_details = {
          "patient_id": {"S": "Bill-Gates"},
          "name": {"S": "Bill Gates"},
          "phone_number": {"S": "9112345680"},
          "gender": {"S": "Male"},
          "age": {"N": "65"},
          "address": {"S": "789 Microsoft Way, Redmond, WA"},
          "emergency_contact": {"S": "9876543212"},
          "blood_group": {"S": "B-"}
        }


# List of US states
us_states = [
    "California", "Texas", "Florida", "New York", "Pennsylvania",
    "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan"
]

# List of possible medications
medications = [
    "Metformin", "Lisinopril", "Levothyroxine", "Atorvastatin",
    "Amlodipine", "Metoprolol", "Omeprazole", "Losartan",
    "Albuterol", "Gabapentin", "Anvil"
]

# List of possible reasons for visits
#reasons_for_visit = [
#    "Annual Checkup", "Follow-up", "New Symptoms", "Medication Refill",
#    "Lab Results Review", "Blood Pressure Check", "Diabetes Management",
#    "Thyroid Check", "Heart Health Check", "Respiratory Issues"
#]

reasons_for_visit = [
    "Annual Checkup", "Follow-up", "New Symptoms", "Medication Refill",
    "Lab Results Review", "Blood Pressure Check", "Body Ache","Head Ache", 
    "Dental Check Up", "Food Poisioning", "Eye Check up", "Diabetes Management",
    "Thyroid Check", "Heart Health Check", "Respiratory Issues"
]


def random_date():
    start_date = datetime.now() - timedelta(days=7*365)
    end_date = datetime.now()
    return start_date + (end_date - start_date) * random.random()


def generate_visit_details(visit_id):
    state = random.choice(us_states)
    date_of_visit = random_date().strftime('%Y-%m-%d')
    hospital_name = f"Hospital in {state}"
    doctor_name = f"Dr. {random.choice(['John', 'Jane', 'Alex', 'Chris', 'Pat', 'Taylor'])} {random.choice(['Smith', 'Johnson', 'Brown', 'Williams', 'Jones'])}"
    reason_for_visit = random.choice(reasons_for_visit)
    blood_pressure = f"{random.randint(90, 140)}/{random.randint(60, 90)} mm Hg"
    blood_sugar = f"{random.randint(70, 140)} mg/dL"
    medication = random.choice(medications)
    doctor_comments = f"Comments for {reason_for_visit.lower()}"
    report_comments = f"Patient advised to {random.choice(['rest', 'exercise', 'follow-up', 'monitor blood pressure', 'take medications regularly'])}"

    return {
        "visit_id": {"S": visit_id},
        "patient_id": {"S": "Bill-Gates"},
        "Hospital_Name": {"S": hospital_name},
        "Date_of_Visit": {"S": date_of_visit},
        "Doctor_Name": {"S": doctor_name},
        "Reason_for_visit": {"S": reason_for_visit},
        "Blood_Pressure_Level": {"S": blood_pressure},
        "Blood_Sugar_Level": {"S": blood_sugar},
        "Medications_Prescribed": {"S": medication},
        "Doctor_Comments": {"S": doctor_comments},
        "report_url": {"S": f"https://suprith-face-security-system.s3.amazonaws.com/visit-reports/{visit_id}.pdf"},
        "report_comments": report_comments
    }


output_dir = "generated_json"
os.makedirs(output_dir, exist_ok=True)

for i in range(1, 7):
    visit_id = f"Visit{str(i).zfill(3)}"
    visit_details = generate_visit_details(visit_id)
    report_data = {
        "Patient_details": patient_details,
        "visit_details": visit_details
    }
    
    
    with open(os.path.join(output_dir, f"{visit_id}.json"), 'w') as json_file:
        json.dump(report_data, json_file, indent=2)

print("10 JSON files have been generated successfully.")
