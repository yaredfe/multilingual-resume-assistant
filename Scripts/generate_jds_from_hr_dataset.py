import os
import json
import pandas as pd

# === Paths ===
csv_path = "./data/aug_train.csv"
output_folder = "./data/job_descriptions/"
os.makedirs(output_folder, exist_ok=True)

# === Load Data ===
df = pd.read_csv(csv_path)

# === Clean & Filter ===
df = df.dropna(subset=["major_discipline", "experience", "education_level", "relevent_experience"])

# === Mappings for readability ===
experience_map = {
    "<1": "less than 1 year",
    "1": "1 year",
    "2": "2 years", "3": "3 years", "4": "4 years",
    "5": "5 years", "6": "6 years", "7": "7 years",
    "8": "8 years", "9": "9 years", "10": "10 years",
    "11": "11 years", "12": "12 years", "13": "13 years",
    "14": "14 years", "15": "15 years", "16": "16 years",
    "17": "17 years", "18": "18 years", "19": "19 years",
    "20": "20 years", ">20": "more than 20 years"
}

edu_map = {
    "Graduate": "Bachelor’s degree",
    "Masters": "Master’s degree",
    "Phd": "Ph.D.",
    "High School": "High School diploma",
    "Primary School": "Primary School education"
}

rel_exp_map = {
    "Has relevent experience": "Must have relevant industry experience",
    "No relevent experience": "Relevant experience is a plus but not required"
}

# === Generate JDs grouped by major_discipline ===
grouped = df.groupby("major_discipline")

for discipline, group in grouped:
    # Normalize file name
    title_slug = discipline.strip().replace(" ", "_").replace("/", "_").lower()

    # Mode values
    raw_exp = str(group["experience"].mode()[0])
    raw_edu = str(group["education_level"].mode()[0])
    raw_relexp = str(group["relevent_experience"].mode()[0])

    # Cleaned values
    exp = experience_map.get(raw_exp, f"{raw_exp} years of experience")
    edu = edu_map.get(raw_edu, raw_edu)
    relexp = rel_exp_map.get(raw_relexp, raw_relexp)

    # Create description and requirements
    jd = {
        "title": f"{discipline} Specialist",
        "description": (
            f"We are seeking a passionate {discipline} Specialist to join our team. "
            f"The ideal candidate will have a solid educational background and the ability to apply their knowledge to real-world projects."
        ),
        "requirements": [
            f"Minimum experience required: {exp}",
            f"Education level: {edu}",
            f"{relexp}"
        ],
        "skills": [discipline]
    }

    # Save JD as JSON
    file_path = os.path.join(output_folder, f"{title_slug}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(jd, f, indent=2)

print(f"SUCCESS: Generated {len(grouped)} enhanced job descriptions in: {output_folder}")
