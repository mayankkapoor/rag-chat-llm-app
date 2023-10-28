from flask import Flask, request, jsonify
import openai
import psycopg2
import os
from psycopg2.extras import DictCursor

app = Flask(__name__)

# Configuration
app.config['DATABASE_URI'] = os.environ.get('DATABASE_URI')  # Use an environment variable for your database URI

# Initialize OpenAI API
openai.api_key = 'YOUR_OPENAI_API_KEY'  # This could also be an environment variable

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

    response = openai.Completion.create(prompt=question, max_tokens=150)
    answer = response.choices[0].text.strip()

    # Save to database (optional)
    save_question_and_answer(question, answer)

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
    app.run(debug=False, host="0.0.0.0", port=8080)
