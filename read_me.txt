
The summarize script.
How it works:
This script is made to chat with python files.
First the script iterates through the files in the specified folder.
Llama3 then generates short summeries along with some metadata to each file.
After that, the user can ask a question and press enter.
One of the Llama3 agents searches the json file for the most relevant summery and hands the file path 
over to the assistant agent.
The assistant takes the content of the file as context in the prompt, along with the question asked by the user and generates a response.
The user has the option to ask again.
The previous interactions is saved in a log and is used as context for the next query.
The user has the option to clear the history log.

improvements for making it robust: 
* Give feedback to the user when the context window is getting full.
* Additional error handling.
* Improved prompt engineering

Example query: Give me the complete code of the snake game but modify the code and change the color of the snake to yellow. Remeber to give me the COMPLETE code so that i can just copy and paste it.

Embeddings.
model="text-embedding-3-large"
I use ast to parse the code into blocks of classes, functions and top level code. 
I have kept the embedding script very simple by just taking a query and outputing the 4 best results.
If i would develop this more i would have used a similar strategy as i did to the summarize script, and use an llm to first
let it evaluate the response from the vector database and then fetch the entire content from the most relevent file.

