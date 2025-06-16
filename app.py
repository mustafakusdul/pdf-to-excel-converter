from flask import Flask, request, send_file, render_template_string
import pandas as pd
import io
import pdfplumber

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(open('index.html', encoding='utf-8').read())

@app.route('/convert', methods=['POST'])
def convert_pdf_to_excel():
    file = request.files.get('pdf_file')
    if not file or not file.filename.endswith('.pdf'):
        return 'Invalid file', 400

    output = io.BytesIO()

    with pdfplumber.open(file) as pdf:
        all_text = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\\n')
                for line in lines:
                    all_text.append([line])

        df = pd.DataFrame(all_text, columns=['Text'])
        df.to_excel(output, index=False, engine='xlsxwriter')

    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     download_name='converted.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
