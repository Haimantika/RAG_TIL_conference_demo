from flask import Flask, request, render_template
import fitz  # PyMuPDF
import requests
import os

app = Flask(__name__)

# Define the directory for uploaded files
UPLOAD_FOLDER = 'path/to/your/upload/folder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# Sample corpus: List of paragraphs on different topics
corpus = [
    "Climate change is the long-term alteration of temperature and typical weather patterns in a place.",
    "Machine learning is a type of artificial intelligence that allows software applications to become more accurate at predicting outcomes without being explicitly programmed.",
    "The stock market consists of exchanges where stocks, bonds, and other securities are bought and sold.",
    "Biodiversity refers to the variety and variability of life on Earth, crucial for ecosystems to function and humans to survive."
]


def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = ''
    for page in doc:
        text += page.get_text()
    return text


def retrieve_relevant_text(query):
    # Simple keyword-based retrieval for demonstration
    keywords = query.lower().split()
    relevant_texts = [text for text in corpus if any(
        keyword in text.lower() for keyword in keywords)]
    return ' '.join(relevant_texts)


def generate_summary(text, context):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "prompt": f"Summarize the following text:\n\n{text}\n\nRelevant information:\n{context}",
        "temperature": 0.7,
        "max_tokens": 150,
        "model": "gpt-3.5-turbo-instruct",
    }
    response = requests.post(
        "https://api.openai.com/v1/completions", json=data, headers=headers)
    response_data = response.json()
    if 'choices' in response_data and response_data['choices']:
        summary = response_data['choices'][0]['text'].strip()
        return "Here's the summary:\n" + summary
    else:
        error_message = response_data.get(
            'error', {}).get('message', 'Unknown error.')
        return f"Failed to generate summary. Error: {error_message}"


@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    if request.method == 'POST' and 'document' in request.files:
        file = request.files['document']
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            text = extract_text_from_pdf(filepath)
            context = retrieve_relevant_text(text)
            summary = generate_summary(text, context)
    return render_template('index.html', summary=summary)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf']


if __name__ == '__main__':
    app.run(debug=True)
