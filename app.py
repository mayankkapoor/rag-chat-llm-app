from flask import Flask, request, jsonify
import openai
import psycopg2
from psycopg2.extras import DictCursor

app = Flask(__name__)

# Configuration
app.config['DATABASE_URI'] = os.environ.get('DATABASE_URI')  # Use an environment variable for your database URI

# Initialize OpenAI API
openai.api_key = 'YOUR_OPENAI_API_KEY'  # This could also be an environment variable

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
    app.run(debug=True)
