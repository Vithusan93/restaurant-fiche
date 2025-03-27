import tkinter as tk
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import date
import csv
import os

# Fonction pour générer le PDF et enregistrer dans le fichier CSV
def generate_pdf():
    # Récupérer les données
    repas = entry_repas.get()
    prix_par_repas = entry_prix.get()
    
    if not repas or not prix_par_repas:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs!")
        return

    # Calcul de la date actuelle
    today = date.today()
    date_actuelle = today.strftime("%d/%m/%Y")

    # Calcul de la TVA en fonction de l'option choisie
    tva_rate = 0.10 if var_sur_place.get() == "Sur place" else 0.05
    total_ht = float(repas) * float(prix_par_repas)
    tva = total_ht * tva_rate
    total_ttc = total_ht + tva

    # Créer le fichier PDF
    c = canvas.Canvas("bloc_repas.pdf", pagesize=letter)

    # Informations de l'entreprise
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 750, "MASSALA MAGIC")
    c.drawString(100, 735, "7 RUE DE L'ARBALETE, 118 BIS RUE MOUFFETARD, 75005 PARIS, France")
    c.drawString(100, 720, "Email: massalamagic2023@gmail.com")
    c.drawString(100, 705, "SIRET: 84847312000022 | TVA: FR80848473120")
    c.drawString(100, 690, "Téléphone: 0140560943")
    
    # Infos de la fiche de bloc de repas
    c.setFont("Helvetica", 10)
    c.drawString(100, 680, f"Date: {date_actuelle}")
    c.drawString(100, 665, f"Repas: {repas} repas")
    c.drawString(100, 650, f"Prix par repas: {prix_par_repas} €")
    
    # TVA et calcul détaillé
    c.drawString(100, 635, f"TVA ({'Sur place' if var_sur_place.get() == 'Sur place' else 'Emporter'}): {tva_rate*100}%")
    c.drawString(100, 620, f"Total HT: {total_ht:.2f} €")
    c.drawString(100, 605, f"TVA: {tva:.2f} €")
    c.drawString(100, 590, f"Total TTC: {total_ttc:.2f} €")

    # Sauvegarder le fichier PDF
    c.save()
    
    # Enregistrer les données dans un fichier CSV
    save_to_csv(date_actuelle, repas, prix_par_repas, tva_rate, total_ht, tva, total_ttc)

    messagebox.showinfo("Succès", "Fiche de bloc de repas générée avec succès et enregistrée dans le CSV!")

# Fonction pour sauvegarder les données dans le fichier CSV
def save_to_csv(date_actuelle, repas, prix_par_repas, tva_rate, total_ht, tva, total_ttc):
    # Si le fichier CSV n'existe pas, on le crée avec les en-têtes
    file_exists = os.path.isfile('bloc_repas.csv')
    
    with open('bloc_repas.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Ajouter les en-têtes si le fichier est vide
        if not file_exists:
            writer.writerow(['Date', 'Nombre de repas', 'Prix par repas (€)', 'TVA', 'Total HT (€)', 'TVA (€)', 'Total TTC (€)'])
        
        # Ajouter les données de la fiche générée
        writer.writerow([date_actuelle, repas, prix_par_repas, f"{tva_rate*100}%", total_ht, tva, total_ttc])

# Créer la fenêtre Tkinter
root = tk.Tk()
root.title("Bloc de Repas - MASSALA MAGIC")

# Champ pour entrer le nombre de repas et le prix par repas
label_repas = tk.Label(root, text="Nombre de repas")
label_repas.pack()
entry_repas = tk.Entry(root)
entry_repas.pack()

label_prix = tk.Label(root, text="Prix par repas (€)")
label_prix.pack()
entry_prix = tk.Entry(root)
entry_prix.pack()

# Options de TVA : Sur place (10%) ou Emporter (5%)
var_sur_place = tk.StringVar()

# Radiobutton pour "Sur place"
radio_sur_place = tk.Radiobutton(root, text="Sur place (10% TVA)", variable=var_sur_place, value="Sur place")
radio_sur_place.pack()

# Radiobutton pour "Emporter"
radio_emporter = tk.Radiobutton(root, text="Emporter (5% TVA)", variable=var_sur_place, value="Emporter")
radio_emporter.pack()

# Bouton pour générer le PDF
generate_button = tk.Button(root, text="Générer le PDF", command=generate_pdf)
generate_button.pack()

# Lancer l'interface
root.mainloop()
