import os
from openai import OpenAI
from datetime import datetime

execsum_file = 'execsum.txt'

draft_dir = "./DRAFT"


api_key = "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"
model = "gpt-4-1106-preview"
intro_file = 'csvtointro.txt'
csv_dir = "./MEL_CSV"
md_dir = "./MEL_MD"
client = OpenAI(api_key=api_key)

def read_file_contents(file_path):
    with open(file_path, 'r') as file:
        return file.read()

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