from flask import Flask, request, send_file, render_template_string
import pandas as pd
import io
import pdfplumber

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(open("index.html", encoding="utf-8").read())

@app.route('/convert', methods=['POST'])
def convert_pdf_to_excel():
    file = request.files.get('pdf_file')
    if not file:
        return 'No file uploaded', 400

    output = io.BytesIO()
    all_tables = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table)
                all_tables.append(df)

    if not all_tables:
        return 'No tables found in PDF', 400

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for i, table_df in enumerate(all_tables):
            sheet_name = f"Page_{i+1}"
            table_df.to_excel(writer, sheet_name=sheet_name, index=False)

    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     download_name='bank_statement.xlsx', as_attachment=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)