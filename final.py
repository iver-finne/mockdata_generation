import csv
import random
import os
import glob
from openai import OpenAI
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

api_key = "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"
model = "gpt-4-1106-preview"
prompt_file = 'prompt.txt'
intro_file = 'csvtointro.txt'
execsum_file = 'execsum.txt'
csv_dir = "./MEL_CSV"
md_dir = "./MEL_MD"
draft_dir = "./DRAFT"
client = OpenAI(api_key=api_key)

def escape_quotes(text):
    return text.replace('"', '""')

def read_file_contents(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def get_random_industry():
    with open('industries.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        industry_list = [row for row in csv_reader]
    return random.choice(industry_list)

def generate_prompt_with_industry(system_message, industry_info):
    return system_message.format(industry=industry_info['industry'], application=industry_info['application'])

def write_responses_with_industry():
    industry_info = get_random_industry()
    system_message = read_file_contents(prompt_file).strip()
    industry_prompt = generate_prompt_with_industry(system_message, industry_info)
    formatted_industry = industry_info['industry'].replace(' ', '_').replace('&', 'and')
    formatted_application = industry_info['application'].replace(' ', '_').replace(',', '')
    os.makedirs(csv_dir, exist_ok=True)
    csv_filename = f"{csv_dir}/log_{formatted_industry}_{formatted_application}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": industry_prompt}, {"role": "user", "content": " "}]).choices[0].message.content
    with open(csv_filename, "w") as csv_file:
        csv_file.write(f'"{escape_quotes(response)}"\n')

def get_random_csv_file():
    files = glob.glob(f'{csv_dir}/*.csv')
    return random.choice(files) if files else None

def read_csv_content(csv_file):
    with open(csv_file, mode='r') as file:
        csv_reader = csv.reader(file)
        csv_content = [row for row in csv_reader]
    return csv_content

def generate_prompt_with_csv_content(csv_content):
    intro_text = read_file_contents(intro_file).strip()
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
    csv_content = read_csv_content(csv_file)
    prompt = generate_prompt_with_csv_content(csv_content)
    response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": prompt}, {"role": "user", "content": " "}]).choices[0].message.content
    write_response_to_md(csv_file, response)

def generate_prompt_from_files(csv_content, md_content):
    execsum_text = read_file_contents(execsum_file)
    return f"{execsum_text}\n\nCSV Data:\n{csv_content}\n\nMD Content:\n{md_content}"

def write_response_to_draft(unique_name, md_content, response):
    draft_filepath = os.path.join(draft_dir, f"{unique_name}.md")
    os.makedirs(draft_dir, exist_ok=True)
    with open(draft_filepath, "w") as draft_file:
        draft_file.write(md_content + "\n\n" + response)

def process_files(unique_name):
    csv_file_path = os.path.join(csv_dir, f"{unique_name}.csv")
    md_file_path = os.path.join(md_dir, f"{unique_name}.md")

    if not os.path.exists(csv_file_path) or not os.path.exists(md_file_path):
        print(f"Files not found for unique name: {unique_name}")
        return

    csv_content = read_file_contents(csv_file_path)
    md_content = read_file_contents(md_file_path)

        
    prompt = generate_prompt_from_files(csv_content, md_content)
    response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": prompt}, {"role": "user", "content": " "}]).choices[0].message.content
    write_response_to_draft(unique_name, md_content, response)

def main():
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(write_responses_with_industry) for _ in range(10)]
        for future in futures:
            future.result()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_csv_file) for _ in range(10)]
        for future in futures:
            future.result()

    csv_files = os.listdir(csv_dir)
    md_files = os.listdir(md_dir)
    for csv_file in csv_files:
        unique_name = os.path.splitext(csv_file)[0]
        if f"{unique_name}.md" in md_files:
            process_files(unique_name)
        else:
            print(f"MD file missing for {unique_name}")

if __name__ == "__main__":
    main()