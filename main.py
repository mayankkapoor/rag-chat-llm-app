import os
import logging
import sys
from flask import request, jsonify
import openai
import psycopg2
from psycopg2.extras import DictCursor
from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from models import app

# Initialize OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Add logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# check if storage already exists
if not os.path.exists('./storage'):
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
    """
    Checks the health of the application's database connection.

    Returns:
        A JSON response indicating the status of the health check.
    """
    try:
        # Try to connect to the database
        connection = psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = connection.cursor()
        # Simple query to check the database connection
        cursor.execute('SELECT 1')
        cursor.close()
        connection.close()

        return jsonify({"status": "Healthy", "database": "Connected"}), 200
    except Exception as e:
        return jsonify({"status": "Unhealthy", "error": str(e)}), 500


def save_question_and_answer(question, answer):
    """
    Save a question and its corresponding answer to the database.

    Args:
        question (str): The question to be saved.
        answer (str): The answer to the question.

    Returns:
        None
    """
    # Connect to the database
    connection = psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = connection.cursor(cursor_factory=DictCursor)

    # Save data to database
    cursor.execute(
        'INSERT INTO questions (question, answer) VALUES (%s, %s)', (question, answer))
    connection.commit()

    cursor.close()
    connection.close()


@app.route('/ask', methods=['POST'])
def ask():
    """
    Process a question from the user and return an answer.

    Parameters:
    - question

    Returns:
    - The answer to the user's question.

    """
    question = request.json.get('question', '')

    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    print(type(response))
    answer = response.response

    # Save to database for display later
    save_question_and_answer(question, answer)

    return jsonify({"answer": answer})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
