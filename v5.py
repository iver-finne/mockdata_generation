import csv
import random
import os
from openai import OpenAI
from datetime import datetime

api_key = "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"
model = "gpt-3.5-turbo"
summary_file = 'summary.txt'
system_file = 'system.txt'
csv_dir = "./MEL_CSV"
client = OpenAI(api_key=api_key)

def escape_quotes(text):
    return text.replace('"', '""')

def get_random_industry_application():
    with open('industries.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        industry_application_list = [row for row in csv_reader]
    return random.choice(industry_application_list)

def generate_study_summary(industry, application):
    with open(summary_file, 'r') as file:
        summary_prompt = file.read().strip().format(industry=industry, application=application)
    response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": summary_prompt}])
    return response.choices[0].message.content.strip()

def inject_study_into_system_message(industry, application, study_summary):
    with open(system_file, 'r') as file:
        system_message = file.read().format(study=study_summary)
    return system_message

def write_to_csv(filename, content):
    with open(filename, "w", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([content])

if __name__ == "__main__":
    os.makedirs(csv_dir, exist_ok=True)
    print("Generating summaries and MEL content...")

    for _ in range(10):
        industry_application_info = get_random_industry_application()
        study_summary = generate_study_summary(industry_application_info['industry'], industry_application_info['application'])
        print(f"# Summary for {industry_application_info['industry']} - {industry_application_info['application']}")
        print(study_summary)

        system_message_with_study = inject_study_into_system_message(industry_application_info['industry'], industry_application_info['application'], study_summary)
        mel_response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": system_message_with_study}])
        mel_content = mel_response.choices[0].message.content.strip()
        csv_filename = f"{csv_dir}/{industry_application_info['industry']}_{industry_application_info['application']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        write_to_csv(csv_filename, mel_content)
        print("MEL CSV file generated.")

    print("Process completed.")