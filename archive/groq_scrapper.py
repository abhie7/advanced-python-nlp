import os
import json
import re
import pandas as pd
from pdfminer.high_level import extract_text
from groq import Groq
from system_prompt import prompt
from openpyxl import load_workbook
from openpyxl.utils.exceptions import IllegalCharacterError

system_prompt = prompt

def extract_pdf_text(pdf_path):
    try:
        return extract_text(pdf_path)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def process_resume_groq(pdf_path, groq_client):
    resume_text = extract_pdf_text(pdf_path)
    if not resume_text:
        return None
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": resume_text},
        ],
        temperature=0.2,
        max_tokens=8192,
        top_p=1,
        stream=False,
    )

    response_content = response.choices[0].message.content
    print(response_content)
    if not response_content.strip():
        print(f"\nNo content received from Groq API for {pdf_path}. Skipping.")
        return None

    try:
        json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in the response content")
        response_dict = json.loads(json_match.group(0))
    except (json.JSONDecodeError, ValueError) as e:
        print(f"\nError decoding JSON for {pdf_path}: {e}")
        print(f"\nReceived content: {response_content}")
        return None

    return {
        "resume_filename": os.path.basename(pdf_path),
        "resume_text": resume_text,
        "skills": response_dict.get("skills", [])
    }

def save_json(output, output_path):
    with open(output_path, 'w') as json_file:
        json.dump(output, json_file, indent=4)
        print(f"Saved JSON response for {output['resume_filename']} to {output_path}")

def replace_non_printable_chars(s):
    return ''.join(c if c.isprintable() else '?' for c in s)

def sanitize_non_printable_chars(value):
    if isinstance(value, dict):
        return {k: sanitize_non_printable_chars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_non_printable_chars(item) for item in value]
    elif isinstance(value, str):
        return replace_non_printable_chars(value)
    else:
        return value

def convert_json_to_excel(json_directory, excel_output_path):
    all_data = []

    # Load existing data from Excel if it exists
    existing_filenames = set()
    if os.path.exists(excel_output_path):
        try:
            existing_df = pd.read_excel(excel_output_path)
            existing_filenames = set(existing_df['resume_filename'].tolist())
        except Exception as e:
            print(f"Error reading existing Excel file: {e}")

    for json_file in os.listdir(json_directory):
        if json_file.endswith('.json'):
            with open(os.path.join(json_directory, json_file), 'r') as file:
                data = json.load(file)
                sanitized_data = sanitize_non_printable_chars(data)
                if sanitized_data['resume_filename'] not in existing_filenames:
                    all_data.append(sanitized_data)

    rows = []
    for data in all_data:
        row = [data['resume_filename'], data['resume_text']]
        for skill in data.get('skills', []):
            row.append(skill['skill_name'])
            row.append(', '.join(skill.get('skill_variations', [])))
        rows.append(row)

    headers = ["resume_filename", "resume_text"]
    max_skills = max(len(data.get('skills', [])) for data in all_data)
    for i in range(1, max_skills + 1):
        headers.append(f"skill_{i}")
        headers.append(f"variation_{i}")

    df = pd.DataFrame(rows, columns=headers)

    try:
        if os.path.exists(excel_output_path):
            with pd.ExcelWriter(excel_output_path, mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
        else:
            df.to_excel(excel_output_path, index=False, header=True)
        print(f"Converted JSON files to Excel at {excel_output_path}")
    except IllegalCharacterError as e:
        print(f"Error writing to Excel: {e}")

def main(input_directory, output_directory, excel_output_path, api_key):
    os.makedirs(output_directory, exist_ok=True)
    groq_client = Groq(api_key=api_key)

    pdf_files = [f for f in os.listdir(input_directory) if f.endswith('.pdf')]

    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(input_directory, pdf_file)
        json_output_path = os.path.join(output_directory, f"{os.path.splitext(pdf_file)[0]}.json")

        if os.path.exists(json_output_path):
            print(f"JSON file for {pdf_file} already exists. Skipping.")
            continue

        output = process_resume_groq(pdf_file_path, groq_client)
        if output:
            save_json(output, json_output_path)

    convert_json_to_excel(output_directory, excel_output_path)

if __name__ == "__main__":
    main(
        input_directory=r'/Users/abhiraj/Espresso/Developer_Stuff/repos/groq-scrapping/input_resumes',
        output_directory=r'/Users/abhiraj/Espresso/Developer_Stuff/repos/groq-scrapping/output/jsons',
        excel_output_path=r'/Users/abhiraj/Espresso/Developer_Stuff/repos/groq-scrapping/output/resumes_output.xlsx',
        api_key="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"
    )