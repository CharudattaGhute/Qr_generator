from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from fpdf import FPDF
from qrcode import QRCode
import csv
import os
import math
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

class CustomPDF(FPDF):
    def add_whatsapp_icon(self, x, y, icon_path, width, height):
        """Adds the WhatsApp icon next to the helpline text."""
        self.image(icon_path, x=x, y=y, w=width, h=height)

    def rounded_rect(self, x, y, w, h, r):
        """Draws a rounded rectangle with less curvature."""
        r = min(r, w / 2, h / 2)

        self.arc(x + r, y + r, 180, 270, r)  # top left corner
        self.arc(x + w - r, y + r, 270, 360, r)  # top right corner
        self.arc(x + w - r, y + h - r, 0, 90, r)  # bottom right corner
        self.arc(x + r, y + h - r, 90, 180, r)  # bottom left corner
        self.line(x + r, y, x + w - r, y)  # top side
        self.line(x + w, y + r, x + w, y + h - r)  # right side
        self.line(x + r, y + h, x + w - r, y + h)  # bottom side
        self.line(x, y + r, x, y + h - r)  # left side

    def arc(self, x, y, start_angle, end_angle, radius):
        """Draw an arc from a point with specified angles."""
        self._arc(x, y, start_angle, end_angle, radius)

    def _arc(self, x, y, start_angle, end_angle, radius):
        """Internal method to draw arc using fpdf's path management."""
        angle_diff = end_angle - start_angle
        angle_step = angle_diff / 20

        for angle in range(start_angle, end_angle + 1, int(angle_step)):
            angle_rad = angle * (math.pi / 180)
            x_arc = x + radius * math.cos(angle_rad)
            y_arc = y + radius * math.sin(angle_rad)
            if angle == start_angle:
                self.move_to(x_arc, y_arc)
            else:
                self.line_to(x_arc, y_arc)

    def move_to(self, x, y):
        """Move to a point in the drawing."""
        self.set_xy(x, y)

    def line_to(self, x, y):
        """Draw a line to a point."""
        self.line(self.get_x(), self.get_y(), x, y)
        self.set_xy(x, y)

def add_qr_code_to_pdf(pdf, qr_img, code_text, helpline_text, icon_path):
    temp_file = 'temp_qr_code.png'
    qr_img.save(temp_file, format='PNG')

    div_width = 50
    div_height = 70
    page_width = 210
    page_height = 297
    x = (page_width - div_width) / 2
    y = (page_height - div_height) / 2

    pdf.set_line_width(0.1)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(x, y, div_width, div_height)

    qr_size = 45
    qr_x = x + (div_width - qr_size) / 2
    qr_y = y + 1
    pdf.image(temp_file, x=qr_x, y=qr_y, w=qr_size, h=qr_size)

    pdf.set_font('Arial', '', 21)
    pdf.set_xy(x, qr_y + qr_size - 2.5)
    pdf.cell(w=div_width, h=8, txt=code_text, border=0, ln=1, align='C')

    instruction_text_1 = "Scan the QR code or visit"
    instruction_text_2 = "bit.ly/oasiscb24"
    instruction_text_3 = "coupon code to avail cashback."

    instruction_border_padding = 2
    instruction_width = div_width - instruction_border_padding * 2
    instruction_height = 5
    instruction_x = x + instruction_border_padding
    instruction_y = pdf.get_y()

    pdf.set_line_width(0.1)
    pdf.set_draw_color(0, 0, 0)
    pdf.rounded_rect(instruction_x, instruction_y, instruction_width, instruction_height + 8, 2)

    pdf.set_font('Arial', '', 8)
    pdf.set_xy(instruction_x + 1, instruction_y + 1)
    pdf.cell(w=instruction_width - 2, h=4, txt=instruction_text_1, border=0, align='C')

    pdf.set_font('Arial', 'B', 8)
    pdf.set_xy(instruction_x + 1, instruction_y + 5)
    pdf.cell(w=instruction_width - 20, h=4, txt=instruction_text_2, border=0, align='C')

    pdf.set_font('Arial', '', 8)
    pdf.set_xy(instruction_x + 2, instruction_y + 5)
    pdf.cell(w=instruction_width + 17, h=4, txt=" and enter the", border=0, align='C')

    pdf.set_font('Arial', '', 8)
    pdf.set_xy(instruction_x + 1, instruction_y + 9)
    pdf.cell(w=instruction_width - 2, h=4, txt=instruction_text_3, border=0, align='C')

    pdf.set_xy(x + 2, instruction_y + instruction_height + 13)
    pdf.set_font('Arial', '', 7)

    helpline_y = pdf.get_y()
    whatsapp_icon_height = 3
    whatsapp_icon_width = 3
    pdf.add_whatsapp_icon(x + 4, helpline_y - 3.5, icon_path, whatsapp_icon_width, whatsapp_icon_height)

    pdf.set_xy(x + whatsapp_icon_width + 0, helpline_y)
    pdf.cell(w=div_width - 4, h=-4, txt=helpline_text, border=0, ln=1, align='C')

    if os.path.exists(temp_file):
        os.remove(temp_file)

def generate_pdf_from_csv(csv_filename, original_filename, icon_path):
    pdf = CustomPDF(orientation='P', unit='mm', format='A4')

    # Construct the output PDF filename from the original CSV filename
    base_filename = os.path.splitext(original_filename)[0]
    output_pdf_filename = base_filename + ".pdf"

    try:
        with open(csv_filename, newline='', encoding='ISO-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                code = row['Code']
                helpline = row.get('Helpline', "WhatsApp Helpline: 8766070705")

                qr = QRCode(box_size=10, border=2)
                qr.add_data("bit.ly/oasiscb24")
                qr.make(fit=False)

                qr_img = qr.make_image(fill='black', back_color='white').convert('RGB')
                pdf.add_page()
                add_qr_code_to_pdf(pdf, qr_img, code, helpline, icon_path)

    except FileNotFoundError:
        logging.error(f"Error: The file {csv_filename} does not exist.")
        return None
    except KeyError as e:
        logging.error(f"Error: Missing expected column in CSV: {e}")
        return None
    except UnicodeDecodeError as e:
        logging.error(f"Error decoding file: {e}")
        return None

    # Save the PDF with the constructed filename
    pdf.output(output_pdf_filename)
    logging.info(f"PDF generated successfully: {output_pdf_filename}")
    return output_pdf_filename

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csv' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['csv']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Debugging: Check the content of the uploaded file
        csv_contents = file.read().decode('ISO-8859-1')  # Read the contents for debugging
        logging.info(f"Contents of uploaded CSV: {csv_contents}")
        file.seek(0)  # Reset file pointer to the beginning after reading

        # Save the uploaded CSV file temporarily
        csv_path = os.path.join('/tmp', file.filename)
        file.save(csv_path)

        # Debugging: Check if the file is saved
        if not os.path.exists(csv_path):
            logging.error(f"File not saved correctly at: {csv_path}")
            return jsonify({"error": "File not saved correctly"}), 500

        # Path to WhatsApp icon (modify this as needed)
        icon_path = '/Users/charudattaghute/Desktop/qrcode/backend/WhatsApp_icon.png'  # Ensure this path is correct

        # Generate the PDF with the same name as the CSV file
        output_pdf_filename = generate_pdf_from_csv(csv_path, file.filename, icon_path)
        if output_pdf_filename:
            response = send_file(output_pdf_filename, as_attachment=True)
            # Set the filename in the response headers for download
            response.headers["Content-Disposition"] = f'attachment; filename="{file.filename.rsplit(".", 1)[0]}.pdf"'
            return response
        else:
            return jsonify({"error": "Error generating PDF"}), 500

    return jsonify({"error": "Unknown error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)
