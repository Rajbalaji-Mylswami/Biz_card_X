# Biz_card_X

## Business Card Information Extractor

The **Business Card Information Extractor** is a Streamlit app that allows users to upload images of business cards in JPG or PNG format and automatically extracts relevant information from the business cards. The app uses the `easyocr` library for optical character recognition (OCR) to extract text from the images and applies regular expressions and predefined patterns to identify specific information like company names, card holder names, designations, mobile numbers, email addresses, website URLs, and addresses.

## Requirements

- Python 3.x
- Streamlit
- easyocr
- mysql-connector-python
- pandas
- PIL (Python Imaging Library)


## Setup

1. Make sure you have a MySQL database set up. You can install MySQL locally or use a cloud-based MySQL service.

2. Clone this repository to your local machine.

3. Create a virtual environment (optional but recommended):

4. Install the required packages (see "Requirements" section).

5. Open the `app.py` file and update the MySQL database connection details in the `conn` variable:

conn = mysql.connector.connect(
    host='localhost',
    user='your_username',
    password='your_password',
    database='your_database'
)

## How to Use
1. Run the app.
2. The Streamlit app will open in your web browser.
3. Upload an image of a business card in JPG or PNG format.
4. The app will display the uploaded image and extract information like company name, card holder name, designation, mobile number, email address, website URL, and address from the image.
5. If the extracted information is correct, you can click on the "Save to Database" button to store the data in the MySQL database.
6. The app will also display the data stored in the database in a tabular format.
7. Optionally, you can choose to display the "Delete Option" by checking the checkbox and provide the ID of the row you want to delete. Click on the "Delete" button to delete the selected row from the database.

## Notes
- This app uses the easyocr library for OCR, which may not be perfect in all cases. The accuracy of text extraction depends on the quality of the uploaded images.
- The app uses regular expressions and predefined patterns to identify specific information. You can modify the regex_patterns, company_names_list, and card_holder_names_list as needed to suit your specific use case.
- Make sure to handle the security of the MySQL database connection carefully, especially when deploying the app to production.
- The app allows users to delete data from the database. Ensure that only authorized users have access to this functionality in a production environment.
