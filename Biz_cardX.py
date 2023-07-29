import streamlit as st
import easyocr
import re
import os
import mysql.connector
from io import BytesIO
import pandas as pd
from PIL import Image
import numpy as np

# Initialize the MySQL database connection
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345',
        database='business_card'
    )
except mysql.connector.Error as e:
    st.error(f"Error connecting to MySQL database: {e}")
    st.stop()

cursor = conn.cursor()

# Function to create the database table if it doesn't exist
def create_table():
    create_table_query = """
        CREATE TABLE IF NOT EXISTS cards (
            id INT AUTO_INCREMENT PRIMARY KEY,
            image MEDIUMBLOB NOT NULL,
            company_name VARCHAR(255),
            card_holder_name VARCHAR(255),
            designation VARCHAR(255),
            mobile_number VARCHAR(20),
            email_address VARCHAR(255),
            website_url VARCHAR(255),
            address VARCHAR(100)
        )
    """
    try:
        cursor.execute(create_table_query)
        conn.commit()
    except mysql.connector.Error as e:
        st.error(f"Error creating table: {e}")
        st.stop()

# Function to insert data into the database
def insert_data(image, data):
    insert_query = """
        INSERT INTO cards (image, company_name, card_holder_name, designation, mobile_number, email_address, website_url, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(insert_query, (
        image, data.get('company_name'), data.get('card_holder_name'), data.get('designation'),
        data.get('mobile_number'), data.get('email_address'), data.get('website_url'), data.get('address')))
        conn.commit()
        st.success("Information saved to the database.")
    except mysql.connector.Error as e:
        st.error(f"Error inserting data: {e}")

# Function to fetch data from the database
def fetch_data():
    select_query = """
        SELECT id, company_name, card_holder_name, designation,
               mobile_number, email_address, website_url, address
        FROM cards
    """
    try:
        cursor.execute(select_query)
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as e:
        st.error(f"Error fetching data: {e}")
        return []

# Function to delete data from the database
def delete_data(image_id):
    delete_query = """
        DELETE FROM cards
        WHERE id = %s
    """
    try:
        cursor.execute(delete_query, (image_id,))
        conn.commit()
    except mysql.connector.Error as e:
        st.error(f"Error deleting data: {e}")

# Function to process the uploaded image using easyOCR and extract relevant information
def process_image(image):
    # Save the PIL Image temporarily to disk
    temp_image_path = "temp_image.jpg"
    image.save(temp_image_path, format="JPEG")

    # Read the temporary image back as bytes
    with open(temp_image_path, "rb") as f:
        image_bytes = f.read()

    # Remove the temporary image file
    os.remove(temp_image_path)

    # Initialize the OCR reader for English language
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_bytes)
    extracted_info = {
        'company_name': '',
        'card_holder_name': '',
        'designation': '',
        'mobile_number': '',
        'email_address': '',
        'website_url': '',
        'address': ''
    }

    # Regular expressions for data extraction
    regex_patterns = {
        'mobile_number': r'\b(?:\+\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'email_address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        'website_url': r'\b(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        'address': r'\b(?:[A-Za-z0-9.,# ]+)\b \d{5}(?:-\d{4})?\b'
    }

    # Predefined lists of company names and card holder names
    company_names_list = ['GLOBAL', 'selva', 'BORCELLE AIRLINES', 'Family Restaurant', 'Sun Electricals']
    card_holder_names_list = ['SANTHOSH', 'selva', 'REVANTH', 'KARTHICK', 'Amit kumar']

    # Process OCR results and extract information
    for entry in result:
        text = entry[1].strip()

        # Check for mobile number, email, website, and address using regular expressions
        for info_type, regex_pattern in regex_patterns.items():
            match = re.search(regex_pattern, text)
            if match:
                extracted_info[info_type] = match.group(0)
                break  # Exit the loop after the first match

        # Check for designation based on predefined patterns
        if not extracted_info['designation']:
            designation_pattern = r'\b(?:CEO & FOUNDER|DATA MANAGER|General Manager|Marketing Executive|Technical Manager)\b'
            match = re.search(designation_pattern, text, re.IGNORECASE)
            if match:
                extracted_info['designation'] = match.group(0)
                continue  # Move to the next entry

        # Check for company name based on predefined list
        if not extracted_info['company_name']:
            for company_name in company_names_list:
                if company_name in text:
                    extracted_info['company_name'] = company_name
                    break

        # Check for card holder name based on predefined list
        if not extracted_info['card_holder_name']:
            for card_holder_name in card_holder_names_list:
                if card_holder_name in text:
                    extracted_info['card_holder_name'] = card_holder_name
                    break

    return extracted_info

# Main Streamlit app
def main():
    st.title("Business Card Information Extractor")
    create_table()  # Create the database table if it doesn't exist

    st.write("""
        ### Upload a business card image
        Please upload an image of a business card in JPG or PNG format.
    """)

    # File uploader for image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        # Convert image to RGB mode if it's in RGBA mode
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        # Display the uploaded image
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Extracted Information section
        st.header("Extracted Information")

        # Convert the PIL Image to a numpy array
        image_np = np.array(image)

        # Process the image and extract information
        extracted_info = process_image(Image.fromarray(image_np))  # Convert back to PIL Image
        if extracted_info:
            for key, value in extracted_info.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

            # Save extracted information to the database
            if st.button("Save to Database"):
                image_bytes = BytesIO()
                image.save(image_bytes, format='JPEG')
                insert_data(image_bytes.getvalue(), extracted_info)

    # New section to display the database table and delete option
    st.header("Database Table")
    rows = fetch_data()
    if rows:
        # Convert the fetched data into a list of dictionaries
        data_dict_list = []
        for row in rows:
            data_dict = {
                "ID": row[0],
                "Company Name": row[1],
                "Card Holder Name": row[2],
                "Designation": row[3],
                "Mobile Number": row[4],
                "Email Address": row[5],
                "Website URL": row[6],
                "Address": row[7]
            }
            data_dict_list.append(data_dict)

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data_dict_list)

        # Set the "ID" column as the index (hides the default index column)
        df.set_index("ID", inplace=True)

        # Display the DataFrame without showing the index column and the "ID" column
        st.dataframe(df)

        # Delete option
        if st.checkbox("Show Delete Option"):
            st.write("Enter the ID of the row you want to delete:")
            delete_id = st.text_input("ID:")

            if st.button("Delete"):
                try:
                    delete_id = int(delete_id)  # Convert the user input to an integer
                    if delete_id >= 1:
                        delete_data(delete_id)
                        st.success("Data deleted successfully.")
                    else:
                        st.warning("Please enter a valid ID (greater than or equal to 1).")
                except ValueError:
                    st.warning("Please enter a valid ID (a positive integer).")
    else:
        st.write("No data found in the database.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
