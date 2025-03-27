import sys
import os
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QRadioButton, QPushButton, QMessageBox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import date

# Vérifier le système d'exploitation
if sys.platform == "win32":
    import win32print
    import win32ui
elif sys.platform == "darwin":  # macOS
    import cups

def generate_pdf():
    nombre_personnes = entry_personnes.text()
    prix_total = entry_prix.text()

    if not nombre_personnes or not prix_total:
        QMessageBox.critical(window, "Erreur", "Veuillez remplir tous les champs!")
        return

    # Remplacement de la virgule par un point
    nombre_personnes = nombre_personnes.replace(",", ".")
    prix_total = prix_total.replace(",", ".")

    # Date actuelle
    today = date.today()
    date_actuelle = today.strftime("%d/%m/%Y")

    # Calcul de la TVA
    tva_rate = 0.10 if var_sur_place.isChecked() else 0.055
    total_ht = float(prix_total) / (1 + tva_rate)
    tva = float(prix_total) - total_ht

    # Génération du PDF
    pdf_filename = "bloc_repas.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 750, "MASSALA MAGIC")
    c.drawString(100, 735, "7 RUE DE L'ARBALETE, 75005 PARIS, France")
    c.drawString(100, 720, "Email: massalamagic2023@gmail.com")
    c.drawString(100, 705, "SIRET: 84847312000022 | TVA: FR80848473120")
    c.drawString(100, 690, "Téléphone: 0140560943")
    c.setFont("Helvetica", 10)
    c.drawString(100, 680, f"Date: {date_actuelle}")
    c.drawString(100, 665, f"Nombre de personnes: {nombre_personnes}")
    c.drawString(100, 650, f"Prix total (TVA incluse): {prix_total} €")
    c.drawString(100, 635, f"TVA: {tva_rate*100}%")
    c.drawString(100, 620, f"Total HT: {total_ht:.2f} €")
    c.drawString(100, 605, f"TVA: {tva:.2f} €")
    c.drawString(100, 590, f"Total TTC: {prix_total} €")
    c.save()

    # Sauvegarde CSV
    save_to_csv(date_actuelle, nombre_personnes, prix_total, tva_rate, total_ht, tva)
    
    # Impression du ticket
    print_ticket(nombre_personnes, prix_total, tva, total_ht)

    QMessageBox.information(window, "Succès", "PDF généré et ticket imprimé avec succès!")

def save_to_csv(date_actuelle, nombre_personnes, prix_total_ttc, tva_rate, total_ht, tva):
    file_exists = os.path.isfile('bloc_repas.csv')
    with open('bloc_repas.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Date', 'Nombre de personnes', 'Prix total TTC (€)', 'TVA', 'Total HT (€)', 'TVA (€)', 'Total TTC (€)'])
        writer.writerow([date_actuelle, nombre_personnes, prix_total_ttc, f"{tva_rate*100}%", total_ht, tva, prix_total_ttc])

def print_ticket(nombre_personnes, prix_total, tva, total_ht):
    ticket_text = f"""
    MASSALA MAGIC
    -----------------------
    Nombre de personnes: {nombre_personnes}
    Prix total TTC: {prix_total} €
    -----------------------
    Total HT: {total_ht:.2f} €
    TVA: {tva:.2f} €
    -----------------------
    Merci pour votre visite!
    """
    
    if sys.platform == "win32":  # Impression Windows
        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(hprinter, 2)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)
        pdc.StartDoc('Ticket')
        pdc.StartPage()
        pdc.TextOut(100, 100, ticket_text)
        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()
    elif sys.platform == "darwin":  # Impression macOS
        conn = cups.Connection()
        printer_name = conn.getDefault()
        file_path = "/tmp/ticket.txt"
        with open(file_path, "w") as f:
            f.write(ticket_text)
        conn.printFile(printer_name, file_path, "Ticket", {})

# Création de l'interface PyQt5
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Bloc de Repas - MASSALA MAGIC")
window.setGeometry(100, 100, 400, 300)
layout = QVBoxLayout()

label_personnes = QLabel("Nombre de personnes")
layout.addWidget(label_personnes)
entry_personnes = QLineEdit()
layout.addWidget(entry_personnes)

label_prix = QLabel("Prix total TTC (€) (TVA incluse)")
layout.addWidget(label_prix)
entry_prix = QLineEdit()
layout.addWidget(entry_prix)

var_sur_place = QRadioButton('Sur place (10% TVA)')
var_emporter = QRadioButton('Emporter (5.5% TVA)')
layout.addWidget(var_sur_place)
layout.addWidget(var_emporter)

generate_button = QPushButton("Générer le PDF et Imprimer")
generate_button.clicked.connect(generate_pdf)
layout.addWidget(generate_button)

window.setLayout(layout)
window.show()
sys.exit(app.exec_())