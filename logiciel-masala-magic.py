import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QRadioButton, QPushButton, QMessageBox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import date
import csv
import os

# Fonction pour générer le PDF et enregistrer dans le fichier CSV
def generate_pdf():
    nombre_personnes = entry_personnes.text()
    prix_total = entry_prix.text()

    if not nombre_personnes or not prix_total:
        QMessageBox.critical(window, "Erreur", "Veuillez remplir tous les champs!")
        return

    # Remplacer la virgule par un point pour le format numérique
    nombre_personnes = nombre_personnes.replace(",", ".")
    prix_total = prix_total.replace(",", ".")

    # Calcul de la date actuelle
    today = date.today()
    date_actuelle = today.strftime("%d/%m/%Y")

    # Calcul du prix total TTC
    prix_total_ttc = float(prix_total)

    # Calcul de la TVA en fonction de l'option choisie
    tva_rate = 0.10 if var_sur_place.isChecked() else 0.055
    
    # Si la TVA est incluse, on calcule le montant HT
    total_ht = prix_total_ttc / (1 + tva_rate)
    tva = prix_total_ttc - total_ht

    # Créer le fichier PDF
    c = canvas.Canvas("bloc_repas.pdf", pagesize=letter)

    # Informations de l'entreprise
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 750, "MASSALA MAGIC")
    c.drawString(100, 735, "7 RUE DE L'ARBALETE, 75005 PARIS, France")
    c.drawString(100, 720, "Email: massalamagic2023@gmail.com")
    c.drawString(100, 705, "SIRET: 84847312000022 | TVA: FR80848473120")
    c.drawString(100, 690, "Téléphone: 0140560943")
    
    # Infos de la fiche de bloc de repas
    c.setFont("Helvetica", 10)
    c.drawString(100, 680, f"Date: {date_actuelle}")
    c.drawString(100, 665, f"Nombre de personnes: {nombre_personnes}")
    c.drawString(100, 650, f"Prix total (TVA incluse): {prix_total_ttc} €")
    
    # TVA et calcul détaillé
    c.drawString(100, 635, f"TVA ({'Sur place' if var_sur_place.isChecked() else 'Emporter'}): {tva_rate*100}%")
    c.drawString(100, 620, f"Total HT: {total_ht:.2f} €")
    c.drawString(100, 605, f"TVA: {tva:.2f} €")
    c.drawString(100, 590, f"Total TTC: {prix_total_ttc:.2f} €")

    # Sauvegarder le fichier PDF
    c.save()
    
    # Enregistrer les données dans un fichier CSV
    save_to_csv(date_actuelle, nombre_personnes, prix_total_ttc, tva_rate, total_ht, tva)

    QMessageBox.information(window, "Succès", "Fiche de bloc de repas générée avec succès et enregistrée dans le CSV!")

# Fonction pour sauvegarder les données dans le fichier CSV
def save_to_csv(date_actuelle, nombre_personnes, prix_total_ttc, tva_rate, total_ht, tva):
    file_exists = os.path.isfile('bloc_repas.csv')
    
    with open('bloc_repas.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Date', 'Nombre de personnes', 'Prix total TTC (€)', 'TVA', 'Total HT (€)', 'TVA (€)', 'Total TTC (€)'])
        
        writer.writerow([date_actuelle, nombre_personnes, prix_total_ttc, f"{tva_rate*100}%", total_ht, tva, prix_total_ttc])

# Créer la fenêtre PyQt5
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Bloc de Repas - MASSALA MAGIC")
window.setGeometry(100, 100, 400, 300)

layout = QVBoxLayout()

# Champ pour entrer le nombre de personnes et le prix total TTC
label_personnes = QLabel("Nombre de personnes")
layout.addWidget(label_personnes)
entry_personnes = QLineEdit()
layout.addWidget(entry_personnes)

label_prix = QLabel("Prix total TTC (€) (TVA incluse)")
layout.addWidget(label_prix)
entry_prix = QLineEdit()
layout.addWidget(entry_prix)

# Options de TVA : Sur place (10%) ou Emporter (5,5%)
var_sur_place = QRadioButton('Sur place (10% TVA)')
var_emporter = QRadioButton('Emporter (5,5% TVA)')

layout.addWidget(var_sur_place)
layout.addWidget(var_emporter)

# Bouton pour générer le PDF
generate_button = QPushButton("Générer le PDF")
generate_button.clicked.connect(generate_pdf)
layout.addWidget(generate_button)

window.setLayout(layout)

# Lancer l'interface
window.show()
sys.exit(app.exec_())
