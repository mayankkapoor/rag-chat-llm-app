from flask import Flask, request, jsonify
import openai
import psycopg2
import os
from psycopg2.extras import DictCursor
from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
import logging
import sys

app = Flask(__name__)

# Configuration
app.config['DATABASE_URI'] = os.environ.get('DATABASE_URI')  # Use an environment variable for your database URI

# Initialize OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')  # This could also be an environment variable

# Add logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# check if storage already exists
if (not os.path.exists('./storage')):
    # load the documents and create the index
    documents = SimpleDirectoryReader('./data').load_data()
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    index.storage_context.persist()
else:
    # load the existing index
    storage_context = StorageContext.from_defaults(persist_dir='./storage')
    index = load_index_from_storage(storage_context)

@app.route('/', methods=['GET'])
def health_check():
    try:
        # Try to connect to the database
        connection = psycopg2.connect(app.config['DATABASE_URI'])
        cursor = connection.cursor()
        cursor.execute('SELECT 1')  # Simple query to check the database connection
        print("DB SELECT 1 query exected")
        cursor.close()
        connection.close()
        
        return jsonify({"status": "Healthy", "database": "Connected"}), 200
    except Exception as e:
        return jsonify({"status": "Unhealthy", "error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question', '')

    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    print(type(response))
    answer = response.response

    # # Save to database (optional)
    # save_question_and_answer(question, answer)

    return jsonify({"answer": answer})

def save_question_and_answer(question, answer):
    # Connect to the database
    connection = psycopg2.connect(app.config['DATABASE_URI'])
    cursor = connection.cursor(cursor_factory=DictCursor)

    # Save data to database
    cursor.execute('INSERT INTO questions (question, answer) VALUES (%s, %s)', (question, answer))
    connection.commit()

    cursor.close()
    connection.close()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
