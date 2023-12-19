import csv
import random
import os
from openai import OpenAI
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

api_key = "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"
model = "gpt-4-1106-preview"
prompt_file = 'prompt.txt'
csv_dir = "./MEL_CSV"
client = OpenAI(api_key=api_key)

def escape_quotes(text):
    return text.replace('"', '""')

def get_random_industry():
    with open('industries.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        industry_list = [row for row in csv_reader]
    return random.choice(industry_list)

def generate_prompt_with_industry(system_message, industry_info):
    return system_message.format(industry=industry_info['industry'], application=industry_info['application'])

def write_responses_with_industry():
    industry_info = get_random_industry()  
    print(f"Generating MEL case for: {industry_info['industry']} - {industry_info['application']}")
    system_message = open(prompt_file, 'r').read().strip()
    industry_prompt = generate_prompt_with_industry(system_message, industry_info)
    formatted_industry = industry_info['industry'].replace(' ', '_').replace('&', 'and')
    formatted_application = industry_info['application'].replace(' ', '_').replace(',', '')
    os.makedirs(csv_dir, exist_ok=True)
    csv_filename = f"{csv_dir}/log_{formatted_industry}_{formatted_application}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": industry_prompt}, {"role": "user", "content": " "}]).choices[0].message.content
    with open(csv_filename, "w") as csv_file:
        csv_file.write(f'"{escape_quotes(response)}"\n')

def main():
    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            futures = [executor.submit(write_responses_with_industry) for _ in range(10)]
            for future in futures:
                future.result()

if __name__ == "__main__":
    main()
