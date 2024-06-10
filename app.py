from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import firebase_admin
from firebase_admin import credentials, firestore
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import csv
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Firebase
cred = credentials.Certificate(r"C:\Users\akhla\test-crud\test-crud-b8f2b-firebase-adminsdk-63uw2-cce78329f3.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_contact', methods=['POST'])
def add_contact():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']

    if not name or not phone or not email:
        flash('Please enter name, phone number, and email.', 'danger')
        return redirect(url_for('index'))

    try:
        doc_ref = db.collection('contacts').document()
        doc_ref.set({
            'name': name,
            'phone': phone,
            'email': email,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        flash('Contact added successfully!', 'success')
    except Exception as e:
        flash(f'Failed to add contact: {e}', 'danger')

    return redirect(url_for('index'))

@app.route('/phone_book')
def phone_book():
    try:
        contacts_ref = db.collection('contacts').order_by('created_at').get()
        contacts = [{**contact.to_dict(), 'id': contact.id} for contact in contacts_ref]
    except Exception as e:
        flash(f'Failed to retrieve contacts: {e}', 'danger')
        contacts = []
    return render_template('phone_book.html', contacts=contacts)

@app.route('/delete_contacts', methods=['POST'])
def delete_contacts():
    # Get the IDs of selected contacts from the request
    selected_ids = request.json.get('ids', [])

    # Delete each selected contact from Firebase Firestore
    for contact_id in selected_ids:
        db.collection("contacts").document(contact_id).delete()

    # Return a success response
    return jsonify({'message': 'Selected contacts deleted successfully'}), 200


@app.route('/export/pdf')
def export_pdf():
    try:
        contacts_ref = db.collection('contacts').order_by('created_at').get()
        contacts = [[contact.id, contact.to_dict()['name'], contact.to_dict()['phone'], contact.to_dict()['email']] for contact in contacts_ref]
    except Exception as e:
        flash(f'Failed to retrieve contacts: {e}', 'danger')
        return redirect(url_for('phone_book'))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    table_data = [['ID', 'Name', 'Phone', 'Email']] + contacts

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements = [table]
    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='contacts.pdf', mimetype='application/pdf')

@app.route('/export/csv')
def export_csv():
    try:
        contacts_ref = db.collection('contacts').order_by('created_at').get()
        contacts = [[contact.id, contact.to_dict()['name'], contact.to_dict()['phone'], contact.to_dict()['email']] for contact in contacts_ref]
    except Exception as e:
        flash(f'Failed to retrieve contacts: {e}', 'danger')
        return redirect(url_for('phone_book'))

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['ID', 'Name', 'Phone', 'Email'])
    writer.writerows(contacts)
    buffer.seek(0)

    return send_file(io.BytesIO(buffer.getvalue().encode()), as_attachment=True, download_name='contacts.csv', mimetype='text/csv')


@app.route('/update_contact/<contact_id>', methods=['POST'])
def update_contact(contact_id):
    try:
        # Get the updated contact data from the request body
        updated_contact = request.json
        
        # Update the contact in Firestore using the provided contact_id
        db.collection('contacts').document(contact_id).update(updated_contact)

        return jsonify({'message': 'Contact updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
