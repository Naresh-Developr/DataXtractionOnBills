import PyPDF2
import re
import pandas as pd
from datetime import datetime
from PIL import Image
from pytesseract import pytesseract
import google.generativeai as genai
import time
import google.api_core.exceptions

# Specify the path to the Tesseract executable
# pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path accordingly
pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
        print("Extracted PDF Page Text: ", text)  # Debugging
    return text

# Function to extract text from images using Tesseract
def extract_text_from_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

# Function to clean and extract numeric values from strings
def clean_value(value):
    value = value.replace('|', '').replace('₹', '').strip()
    value = re.sub(r'[^\d.]', '', value)  # Keep only digits and dots
    return float(value) if value else 0.0

# Function to convert date formats to "DD/MM/YYYY"
def convert_date_format(date_str):
    for fmt in ("%d-%b-%Y", "%d/%m/%Y", "%d-%b-%y", "%d/%m/%y"):
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime("%d/%m/%Y")
        except ValueError:
            continue
    return date_str  # Return as-is if no format matches

# Configure Google Generative AI
genai.configure(api_key="AIzaSyDETaemf56DFjmm4CABsmqo-_1YuWftbSo")  # Replace with your actual API key
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to process the extracted text with the generative model
def process_text_with_model(text):
    prompt = (
        "You are given the text extracted from an invoice or bill. Your task is to extract and organize the following details "
        "into a structured format for a DataFrame, ensuring that only the exact values from the image are used:\n\n"
        "1. 'Invoice Number' - Extract the invoice number or bill number. Note that the invoice number may be labeled as 'Invoice Number', 'Inv No', or similar variations.\n"
        "2. 'GST Number' - Extract the GST Number exactly as mentioned in the bill.\n"
        "3. 'Actual Total Price' - Extract the exact total amount excluding GST, but including freight and transportation charges.\n"
        "4. 'SGST Rate' - Extract the SGST rate (%) mentioned in the bill.\n"
        "5. 'CGST Rate' - Extract the CGST rate (%) mentioned in the bill.\n"
        "6. 'IGST Rate' - Extract the IGST rate (%) mentioned in the bill, if any, otherwise mark as '-'.\n"
        "7. 'Total GST Rate' - Calculate the total GST rate by summing SGST, CGST, and IGST rates.\n"
        "8. 'Total GST Amount' - Calculate the total GST amount for the bill based on the 'Actual Total Price' and 'Total GST Rate'.\n"
        "9. 'Invoice Date' - Extract and convert the invoice date to 'DD/MM/YYYY' format.\n"
        "10. 'Total Amount' - Calculate the total amount, which is the sum of 'Actual Total Price' and 'Total GST Amount'.\n\n"
        "Make sure that each of these fields is accurately extracted and populated for the respective bill, using only the exact values from the image."
        "The extracted data should be formatted in the following structure:\n\n"
        "Invoice Number: [Invoice Number]\n"
        "GST Number: [GST Number]\n"
        "Actual Total Price: [Actual Total Price]\n"
        "SGST Rate: [SGST Rate]\n"
        "CGST Rate: [CGST Rate]\n"
        "IGST Rate: [IGST Rate]\n"
        "Total GST Rate: [Total GST Rate]\n"
        "Total GST Amount: [Total GST Amount]\n"
        "Invoice Date: [Invoice Date]\n"
        "Total Amount: [Total Amount]\n\n"
        "If any data is missing, mark it as '-'. Ensure all values are correctly placed in the respective fields for each bill."
        "\n\nExtracted text:\n" + text
    )
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except google.api_core.exceptions.ResourceExhausted as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise e

# Function to clean the invoice number
def clean_invoice_number(invoice_number):
    invoice_number = invoice_number.strip()
    return re.sub(r'\s*GST Number', '', invoice_number)

# Function to clean the GST number
def clean_gst_number(gst_number):
    gst_number = gst_number.strip()
    return re.sub(r'\s*Actual Total Price', '', gst_number)

# Function to ensure GST rate has a '%' symbol
def clean_gst_rate(gst_rate):
    gst_rate = gst_rate.strip()
    if not gst_rate.endswith('%'):
        gst_rate += '%'
    return gst_rate

# Function to safely convert a string to float, handle invalid strings
def safe_float_conversion(value):
    try:
        return float(value)
    except ValueError:
        return 0.0

# Function to parse bill details into a DataFrame
def parse_bill_details(text, bill_number):
    # Initialize the dictionary with default values
    data = [{
        "Bill No": bill_number,
        "Invoice Number": "N/A",
        "GST Number": "N/A",
        "Actual Total Price": 0.0,
        "SGST Rate": "0.0%",
        "CGST Rate": "0.0%",
        "IGST Rate": "0.0%",
        "Total GST Rate": "0.0%",
        "Total GST Amount": 0.0,
        "Invoice Date": "N/A",
        "Total Amount": 0.0
    }]

    details = text.split("\n")
    print("Parsed text details:", details)  # Debugging output

    # Loop through the details to find and assign values
    for detail in details:
        if 'Invoice Number' in detail:
            data[0]['Invoice Number'] = clean_invoice_number(detail.split(':')[-1].strip())
        elif 'GST Number' in detail:
            data[0]['GST Number'] = clean_gst_number(detail.split(':')[-1].strip())
        elif 'Actual Total Price' in detail:
            data[0]['Actual Total Price'] = safe_float_conversion(clean_value(detail.split(':')[-1].strip()))
        elif 'SGST Rate' in detail:
            data[0]['SGST Rate'] = clean_gst_rate(detail.split(':')[-1].strip())
        elif 'CGST Rate' in detail:
            data[0]['CGST Rate'] = clean_gst_rate(detail.split(':')[-1].strip())
        elif 'IGST Rate' in detail:
            data[0]['IGST Rate'] = clean_gst_rate(detail.split(':')[-1].strip())
        elif 'Total GST Rate' in detail:
            data[0]['Total GST Rate'] = clean_gst_rate(detail.split(':')[-1].strip())
        elif 'Total GST Amount' in detail:
            data[0]['Total GST Amount'] = safe_float_conversion(clean_value(detail.split(':')[-1].strip()))
        elif 'Invoice Date' in detail:
            data[0]['Invoice Date'] = convert_date_format(detail.split(':')[-1].strip())
        elif 'Total Amount' in detail:
            data[0]['Total Amount'] = safe_float_conversion(clean_value(detail.split(':')[-1].strip()))

    # Ensure the rates are correctly handled if missing
    for rate_field in ['SGST Rate', 'CGST Rate', 'IGST Rate']:
        if data[0][rate_field] == '-' or not data[0][rate_field]:
            data[0][rate_field] = '0.0%'

    # Calculate the total GST rate safely
    try:
        sgst = float(data[0]['SGST Rate'].strip('%'))
    except ValueError:
        sgst = 0.0

    try:
        cgst = float(data[0]['CGST Rate'].strip('%'))
    except ValueError:
        cgst = 0.0

    try:
        igst = float(data[0]['IGST Rate'].strip('%'))
    except ValueError:
        igst = 0.0

    total_gst_rate = sgst + cgst + igst
    data[0]['Total GST Rate'] = f"{total_gst_rate}%"

    print(f"Parsed Bill Data: {data}")  # Debugging output

    return pd.DataFrame(data)


# Function to calculate the total GST amount
def calculate_total_gst_amount(df):
    return df['Total GST Amount'].sum()

# Function to generate a monthly summary DataFrame
def generate_monthly_summary(df):
    # Convert 'Invoice Date' to datetime format, handling errors by coerce (set invalid dates to NaT)
    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%d/%m/%Y', errors='coerce')

    # Check if there are any invalid dates
    if df['Invoice Date'].isnull().all():
        print("All 'Invoice Date' values are invalid or missing.")
        return pd.DataFrame(columns=['Month', 'Total Actual Price', 'Total GST Amount'])
    
    print("Valid 'Invoice Date' found. Proceeding with monthly summary generation.")
    
    # Group by month and aggregate 'Actual Total Price' and 'Total GST Amount'
    summary = df.groupby(df['Invoice Date'].dt.to_period('M')).agg({
        'Actual Total Price': 'sum',
        'Total GST Amount': 'sum'
    }).reset_index()

    # Rename the columns for clarity
    summary.columns = ['Month', 'Total Actual Price', 'Total GST Amount']

    print(f"Generated Monthly Summary: {summary}")

    return summary



# Function to save DataFrame to an Excel file
def save_to_excel(df, filepath):
    # Clean the DataFrame before saving
    df_cleaned = df.dropna(how='all')  # Ensure no empty rows
    
    # Generate monthly summary
    monthly_summary = generate_monthly_summary(df_cleaned)

    # Save DataFrame and summary to multiple sheets in one Excel file
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        # Write all bill details to the first sheet
        if not df_cleaned.empty:
            df_cleaned.to_excel(writer, sheet_name='Bill Details', index=False)
        else:
            print("Bill details DataFrame is empty. No data to write.")

        # Write monthly summary to the second sheet
        if not monthly_summary.empty:
            monthly_summary.to_excel(writer, sheet_name='Monthly Summary', index=False)
        else:
            print("Monthly summary is empty, not writing to Excel.")



