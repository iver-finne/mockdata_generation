
import csv
import os
from openai import OpenAI

client = OpenAI(
    organization='org-gYeLrXsHjG8NgN5f5aryjfxo',
)

with open('prompt.txt', 'r') as file:
    system_message = file.read()
with open('equipment_list.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_headers = ['Tag', 'Description', 'Status', 'Type', 'System', 'Responsible', 'Dimensions', 'Weight', 'Voltage', 'Current', 'Frequency', 'IP_Rating']
    csv_writer.writerow(csv_headers)

    def get_response(prompt_text):
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": prompt_text}],
            max_tokens=2048
        )
        return response['choices'][0]['message']['content']

    csv_content = get_response(system_message)
    csv_data = csv_content.strip().split('\n')
    
    for row in csv_data[1:]: 
        csv_writer.writerow(row.split(','))

context_length = os.path.getsize('equipment_list.csv')
print(f"Total context window length: {context_length}")
