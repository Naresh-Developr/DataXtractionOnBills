import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
from .utils import (
    extract_text_from_pdf, extract_text_from_image, process_text_with_model,
    parse_bill_details, calculate_total_gst_amount, generate_monthly_summary,
    save_to_excel
)

main = Blueprint('main', __name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@main.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Ensure that multiple files are allowed
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        # Get the list of uploaded files
        files = request.files.getlist('file')
        if not files:
            return jsonify({'error': 'No selected files'}), 400

        all_bills_df = pd.DataFrame()  # To store all bill data
        bill_number = 1  # To keep track of bill numbers

        for file in files:
            if file and file.filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS:
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                # Process the file
                if filename.endswith('.pdf'):
                    pdf_text = extract_text_from_pdf(filepath)
                    bills_text = pdf_text.split("Delta Company")
                    bills_text = [bill for bill in bills_text if bill.strip()]

                    # Process each bill in the PDF
                    for bill_text in bills_text:
                        processed_text = process_text_with_model(bill_text)
                        bill_df = parse_bill_details(processed_text, f"Bill {bill_number}")
                        all_bills_df = pd.concat([all_bills_df, bill_df], ignore_index=True)
                        bill_number += 1

                else:
                    # For image files
                    image_text = extract_text_from_image(filepath)
                    processed_text = process_text_with_model(image_text)
                    bill_df = parse_bill_details(processed_text, f"Bill {bill_number}")
                    all_bills_df = pd.concat([all_bills_df, bill_df], ignore_index=True)
                    bill_number += 1

        # Save the consolidated DataFrame and summary to an Excel file
        output_filename = 'consolidated_report.xlsx'
        output_filepath = os.path.join(UPLOAD_FOLDER, output_filename)

        save_to_excel(all_bills_df, output_filepath)

        # Send the consolidated Excel file to the client
        return send_file(output_filepath, as_attachment=True, download_name=output_filename)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
