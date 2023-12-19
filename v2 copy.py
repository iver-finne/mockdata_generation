import csv
import random
import os
from openai import OpenAI
from datetime import datetime

# Setup API key and model
api_key = "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"
model = "gpt-4-1106-preview"
summary_file = 'summary.txt'
system_file = 'system.txt'
csv_dir = "./MEL_CSV"
client = OpenAI(api_key=api_key)

# Utility function to escape quotes for CSV compliance
def escape_quotes(text):
    return text.replace('"', '""')

# Function to get a random industry and application from the CSV file
def get_random_industry_application():
    with open('industries.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        industry_application_list = [row for row in csv_reader]
    return random.choice(industry_application_list)

# Function to generate a study summary using the chat completion endpoint
def generate_study_summary(industry, application):
    with open(summary_file, 'r') as file:
        summary_prompt = file.read().strip().format(industry=industry, application=application)
    response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": summary_prompt}])
    return response.choices[0].message.content.strip()

# Function to insert the study summary into the system message template
def inject_study_into_system_message(industry, application, study_summary):
    with open(system_file, 'r') as file:
        system_message = file.read()
    return system_message.format(industry=industry, application=application, study=study_summary)

# Function to write the MEL content to a CSV file
def write_to_csv(filename, content):
    with open(filename, "w", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([content])

# Main execution flow
if __name__ == "__main__":
    os.makedirs(csv_dir, exist_ok=True)
    print("Welcome! Press Enter to start or type a number (1-10) for multiple entries.")
    while True:
        user_input = input()
        iterations = int(user_input) if user_input.isdigit() and 1 <= int(user_input) <= 10 else 1
        
        industry_application_info = get_random_industry_application()
        study_summary = generate_study_summary(industry_application_info['Industry'], industry_application_info['Application'])
        print("# Summary")
        print(study_summary)
        
        if input("Is the summary okay? (yes/no): ").lower() == "yes":
            system_message_with_study = inject_study_into_system_message(industry_application_info['Industry'], industry_application_info['Application'], study_summary)
            mel_response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": system_message_with_study}])
            mel_content = mel_response.choices[0].message.content.strip()
            csv_filename = f"{csv_dir}/{industry_application_info['Industry']}_{industry_application_info['Application']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            write_to_csv(csv_filename, mel_content)
            print("MEL CSV file generated.")
        else:
            print("Please regenerate the summary.")
            continue
        
        if input("Generate another summary? (yes/no): ").lower() == "no":
            break
