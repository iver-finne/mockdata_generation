import csv
import random
import os
from openai import OpenAI
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import glob

api_key = "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"
model = "gpt-4-1106-preview"
intro_file = 'csvtointro.txt'
csv_dir = "./MEL"
md_dir = "./MEL_MD"
client = OpenAI(api_key=api_key)

def escape_quotes(text):
    return text.replace('"', '""')

def get_random_csv_file():
    files = glob.glob(f'{csv_dir}/*.csv')
    return random.choice(files) if files else None

def read_csv_content(csv_file):
    with open(csv_file, mode='r') as file:
        csv_reader = csv.reader(file)
        csv_content = [row for row in csv_reader]
    return csv_content

def generate_prompt_with_csv_content(csv_content):
    intro_text = open(intro_file, 'r').read().strip()
    csv_data = ' '.join([','.join(row) for row in csv_content])
    return f"{intro_text}\n\nCSV Data:\n{csv_data}"

def write_response_to_md(csv_file, response):
    md_filename = os.path.basename(csv_file).replace('.csv', '.md')
    os.makedirs(md_dir, exist_ok=True)
    md_filepath = os.path.join(md_dir, md_filename)
    with open(md_filepath, "w") as md_file:
        md_file.write(response)

def process_csv_file():
    csv_file = get_random_csv_file()
    if not csv_file:
        print("No CSV files found.")
        return
    print(f"Processing CSV file: {csv_file}")
    csv_content = read_csv_content(csv_file)
    prompt = generate_prompt_with_csv_content(csv_content)
    response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": prompt}, {"role": "user", "content": " "}]).choices[0].message.content
    write_response_to_md(csv_file, response)

def main():
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_csv_file) for _ in range(10)]
        for future in futures:
            future.result()

if __name__ == "__main__":
    main()
