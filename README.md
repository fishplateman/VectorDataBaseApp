# VectorDataBaseApp

This project utilizes Streamlit for managing API keys. To get started, you need to generate your Pinecone and GPT API keys and place them in `./streamlit/secrets.toml` in the following format:

```toml
gpt-api-key = "your_gpt_api_key_here"
pinecone-api-key = "your_pinecone_api_key_here"
```
Before running the project, ensure you have created your Pinecone database and obtained your GPT API key. Don't forget to update the index value in the code to match the name of your database.

# Running the Project
Use the command below to run the project:
```
python3.8 -m streamlit run main.py
```
This command will open a browser interface.

# How to Use
Upon launching, you will be greeted with an instruction:

"I am your Vector Database assistant bot. How can I assist you? If you need to store content, please input the command: save:[content you want to store]. If you need to perform a comparison, please input the command: get:[content you want to compare]."

However, you can also input in natural language. For instance, you might say "I want to save [article1]". After adding this text into your vector database, the system will respond with a data ID. You can then rephrase article1, input it into the chatbox to see if the Vector Database detects the similarity. The system will return the top 5 similar data IDs along with their similarity scores.

This tool can be particularly useful for detecting plagiarism.