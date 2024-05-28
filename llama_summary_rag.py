from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
import glob
import json
import re


llm = ChatOllama(
    model="llama3",
    keep_alive=-1,
    temperature=0.8,
    max_new_tokens=1000
)


def extract_code_content():
    """This function extracts the content from all the files in the directory and calls the extract_summary function to generate a summary of the code in the file. The summaries are then stored in a json file"""
    directory_path = './games'  # Path to the directory containing the python files. Change this to whatever directory you want to chat with.

    python_files = glob.glob(os.path.join(directory_path, '*.py'))

    json_file_path = 'file_summaries.json'

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            file_summaries = json.load(json_file)
    else:
        file_summaries = {}

    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"This is the file: {file_path}")
            summary = extract_summary(content)
            file_summaries[file_path] = summary

        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(file_summaries, json_file, indent=4, ensure_ascii=False)


def extract_summary(content):
    """This function generates a summery of a python file and the summary of each logical block of code in the file."""
    prompt = ChatPromptTemplate.from_template(
        f"Extract a high-level summary of this file’s contents: {content}. Also write short summaries of each logical block of code in the file, with the line number of were the block begins.  Be structured. Do not generate any other text than the summary of the code.")

    chain = prompt | llm | StrOutputParser()

    return (chain.invoke({"content": "Python code",
                          "profession": "senior programmer"}))


def assistant(relevant_file, user_prompt, history_log = None):
    """This agent function helps the user based on the user's query using the file content as context."""
    with open(relevant_file, 'r') as file:
        file_content = file.read()

    if history_log:
        all_previous_prompts_and_responses = ". ".join([f"User asked: {p}. Assistant responded: {r}" for p, r in history_log])
    else:
        all_previous_prompts_and_responses = ""


    prompt_template = "You are a chatbot. Use the previous interactions as context: {all_previous_prompts_and_responses}. Here is the content of the relevant file: {file}. Here is the user's query: {query}. Help the user. If you don't know the answer, just say that you don't know, don't try to make up an answer. Keep the answer concise. Provide the answer only, no other text."

    prompt = ChatPromptTemplate.from_template(prompt_template)

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"file": file_content,
                         "query": user_prompt,
                         "all_previous_prompts_and_responses": all_previous_prompts_and_responses,
                         "profession": "senior programmer"})


def fetch_filepath(user_prompt):
    """Fetches the file path of the most relevant file based on the user's query."""
    with open('./file_summaries.json', 'r') as file:
        json_data = json.load(file)

    prompt_template = "Here are the summarizations of the codebase files: {summaries}. Here is the user's query: {query}. Extract the file path of the most relevant file based on the users query . If you don't know the answer, just say that you don't know, don't try to make up an answer. Always begin the answer with the file path of the relevant file.  Keep the answer concise. Provide the file path only, no other text."

    prompt = ChatPromptTemplate.from_template(prompt_template)

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"summaries": json.dumps(json_data, indent=4),
                         "query": user_prompt,
                         "profession": "senior programmer"})


def extract_file_path(text):
    """Formats the file path from the llm response"""
    pattern = r"(\./[^:]+)"
    match = re.search(pattern, text)
    if match:
        file_path = match.group(1).replace('"', '')
        return file_path
    return None


def clear_terminal():
    """Clear the terminal screen."""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':

    json_file_path = 'file_summaries.json'
    # Comment this out if you want to extract summaries from all the files in the directory. Otherwise the script will only use whats already in the json file.
    if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
        extract_code_content()
    # extract_code_content() # Uncomment this if you want to extract summaries from all the files in the directory. Otherwise the script will only use whats already in the json file.
    file_path = None
    history_log = []
    while True:
        clear_terminal()
        user_prompt = input("What do you want??: ")
        try:
            fetched_filepath = fetch_filepath(user_prompt)
            file_path = extract_file_path(fetched_filepath)
        except Exception as e:
            print("No file path found in the response.")

        print(f"FILEPATH: {file_path}")

        response = assistant(file_path, user_prompt, history_log)
        print(f"RESPONSE FROM ASSISTANT: {response}")
        history_log.append((user_prompt, response))

        print("")
        print("Do you want to ask again?")
        option = input("1. Yes\n2. Yes, but clear the history log\nPress enter to exit")
        if  option == '1':
            continue
        elif option == '2':
            history_log = []
            continue
        else:
            break
