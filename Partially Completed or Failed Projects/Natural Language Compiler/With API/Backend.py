import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)
genai.configure(api_key="AIzaSyCiQrXmDQFOzlCRWcZdqNyVNH6k7J9BqZ8")
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("E:\Projects\Natural Language Compiler\With API\Frontend.js", methods=['POST'])
def execute_instruction():
    instruction = request.json.get('instruction')
    
    # Generate content using the Gemini API
    response = model.generate_content(instruction)
    
    # Extract the result from the response
    execution_result = response.text  # Adapt based on actual response structure

    return jsonify({'result': execution_result})

if __name__ == '__main__':
    app.run(debug=True)
