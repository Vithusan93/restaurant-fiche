package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"time"

	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
	"github.com/signintech/gopdf"
)

func getAvailableFont() string {
	// Font path for Windows compatibility (use Arial as fallback on Windows)
	if runtime.GOOS == "windows" {
		return "C:\\Windows\\Fonts\\Arial.ttf"
	}

	// Fallback for macOS
	possibleFonts := []string{
		"/System/Library/Fonts/Supplemental/Arial.ttf",
		"/System/Library/Fonts/Arial.ttf",
		"/Library/Fonts/Arial.ttf",
	}

	for _, font := range possibleFonts {
		if _, err := os.Stat(font); err == nil {
			return font
		}
	}

	fmt.Println("Aucune police trouvée, utilisation de Helvetica.")
	return "/System/Library/Fonts/Helvetica.ttc"
}

func generateTicketNumber() string {
	date := time.Now().Format("20060102") // Format: YYYYMMDD

	// Fichier pour stocker le dernier numéro utilisé par jour
	counterFile := "ticket_counter_" + date + ".txt"

	var count int

	if data, err := os.ReadFile(counterFile); err == nil {
		count, _ = strconv.Atoi(string(data))
	}
	count++

	// Sauvegarde le nouveau numéro
	_ = os.WriteFile(counterFile, []byte(strconv.Itoa(count)), 0644)

	// Format final
	return fmt.Sprintf("%s-%04d", date, count)
}

func generatePDF(nombrePersonnes, prixTotal, tvaRate string) {
	prixTotalFloat := strToFloat(prixTotal)
	tvaRateFloat := strToFloat(tvaRate) / 100
	tva := prixTotalFloat * tvaRateFloat
	totalHT := prixTotalFloat - tva

	ticketRef := generateTicketNumber()

	pdf := gopdf.GoPdf{}
	pdf.Start(gopdf.Config{PageSize: gopdf.Rect{W: 175, H: 283}})
	pdf.AddPage()

	pageWidth := 175.0
	marginLeft := 10.0
	marginRight := 10.0

	// Ajout du logo
	logoWidth := 200.0
	logoHeight := 130.0
	logoX := (pageWidth - logoWidth) / 2

	logoPath := "./assets/Massala-Magic-logo.png"
	err := pdf.Image(logoPath, logoX, -20, &gopdf.Rect{W: logoWidth, H: logoHeight})
	if err != nil {
		fmt.Println("Erreur d'ajout de l'image:", err)
	}

	// Police
	fontPath := getAvailableFont()
	if fontPath != "" {
		err := pdf.AddTTFFont("font", fontPath)
		if err != nil {
			fmt.Println("Erreur de chargement de la police:", err)
		} else {
			pdf.SetFont("font", "", 8)
		}
	}

	// Centrer du texte
	centerText := func(text string) {
		width, err := pdf.MeasureTextWidth(text)
		if err != nil {
			fmt.Println("Erreur de calcul de la largeur du texte:", err)
			return
		}
		x := (pageWidth - width) / 2
		pdf.SetX(x)
		pdf.Cell(nil, text)
		pdf.Br(13)
	}

	pdf.SetY(70)
	centerText("MASALA MAGIC")
	centerText("7 RUE DE L'ARBALETE")
	centerText("75005 PARIS")
	centerText("Téléphone: 0140560943")
	centerText("SIRET: 84847312000022")
	centerText("TVA: FR80848473120")
	centerText("TICKET : " + ticketRef)

	pdf.Br(10)

	pdf.SetFont("font", "", 10)
	pdf.SetY(170)

	// Fonction pour aligner un texte à gauche et un autre à droite sur la même ligne
	drawLine := func(leftText, rightText string) {
		pdf.SetX(marginLeft)
		pdf.Cell(nil, leftText)

		textWidth, err := pdf.MeasureTextWidth(rightText)
		if err != nil {
			fmt.Println("Erreur de mesure du texte:", err)
			return
		}

		pdf.SetX(pageWidth - textWidth - marginRight)
		pdf.Cell(nil, rightText)

		pdf.Br(10)
	}

	// Ajout du texte formaté
	drawLine(fmt.Sprintf("%s Repas Complet", nombrePersonnes), "")
	drawLine("Prix :", fmt.Sprintf("%0.2f €", prixTotalFloat))
	drawLine(fmt.Sprintf("TVA (%0.1f%%):", tvaRateFloat*100), fmt.Sprintf("%0.2f €", tva))
	drawLine("Total HT:", fmt.Sprintf("%0.2f €", totalHT))
	drawLine("Total TTC:", fmt.Sprintf("%0.2f €", prixTotalFloat))
	pdf.Br(10) // Ajoute un saut de ligne après "Total TTC"
	centerText(time.Now().Format("02/01/2006"))

	// Générer le fichier PDF
	err = pdf.WritePdf("bloc_repas.pdf")
	if err != nil {
		fmt.Println("Erreur d'écriture PDF:", err)
		return
	}

	// Sauvegarde dans CSV
	saveToCSV(ticketRef, nombrePersonnes, prixTotalFloat, totalHT, prixTotalFloat, tva, tvaRate)

	// Imprimer automatiquement après la génération
	printPDF("bloc_repas.pdf")
}

func saveToCSV(ticketRef, nombrePersonnes string, prixTotal, totalHT, totalTTC, tva float64, tvaRate string) {
	file, err := os.OpenFile("commandes.csv", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("Erreur d'ouverture du fichier CSV:", err)
		return
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	stat, _ := file.Stat()
	if stat.Size() == 0 {
		err := writer.Write([]string{"TICKET", "Nombre de personnes", "Prix Total (TTC)", "Total HT", "Total TTC", "TVA", "TVA (%)"})
		if err != nil {
			fmt.Println("Erreur d'écriture de l'entête CSV:", err)
			return
		}
	}

	err = writer.Write([]string{
		ticketRef,
		nombrePersonnes,
		fmt.Sprintf("%0.2f", prixTotal),
		fmt.Sprintf("%0.2f", totalHT),
		fmt.Sprintf("%0.2f", totalTTC),
		fmt.Sprintf("%0.2f", tva),
		tvaRate,
	})
	if err != nil {
		fmt.Println("Erreur d'écriture dans le fichier CSV:", err)
		return
	}
}

func strToFloat(str string) float64 {
	f, err := strconv.ParseFloat(str, 64)
	if err != nil {
		fmt.Println("Erreur de conversion:", err)
		return 0.0
	}
	return f
}

func findSumatraPDFPath() (string, error) {
	// Vérifier dans le registre Windows
	manualPath := "C:\\Users\\Masala Magic\\AppData\\Local\\SumatraPDF\\SumatraPDF.exe"

	// Vérifier si le fichier existe
	if _, err := os.Stat(manualPath); err == nil {
		return manualPath, nil
	}

	return "", fmt.Errorf("SumatraPDF non trouvé à l'emplacement : %s", manualPath)

}

func printPDF(pdfPath string) {
	// Vérifier si le fichier PDF existe avant d'imprimer
	if _, err := os.Stat(pdfPath); os.IsNotExist(err) {
		fmt.Println("Erreur : Le fichier PDF n'existe pas.")
		return
	}

	// Trouver SumatraPDF
	sumatraPath, err := findSumatraPDFPath()
	if err != nil {
		fmt.Println("Erreur :", err)
		return
	}

	// Commande pour imprimer automatiquement le fichier PDF avec SumatraPDF
	cmd := exec.Command(sumatraPath, "-print-to-default", pdfPath)

	// Exécution de la commande pour imprimer
	err = cmd.Run()
	if err != nil {
		fmt.Println("Erreur d'impression :", err)
	} else {
		fmt.Println("Impression lancée avec succès !")
	}
}

func main() {
	a := app.New()
	w := a.NewWindow("Bloc de Repas - MASSALA MAGIC")

	labelPersonnes := widget.NewLabel("Nombre de personnes")
	entryPersonnes := widget.NewEntry()

	labelPrix := widget.NewLabel("Prix total TTC (€) (TVA incluse)")
	entryPrix := widget.NewEntry()

	varSurPlace := widget.NewRadioGroup([]string{"Sur place (10% TVA)", "Emporter (5.5% TVA)"}, nil)

	var tvaRate string

	varSurPlace.OnChanged = func(value string) {
		if value == "Sur place (10% TVA)" {
			tvaRate = "10"
		} else if value == "Emporter (5.5% TVA)" {
			tvaRate = "5.5"
		}
	}

	generateButton := widget.NewButton("Générer le PDF", func() {
		nombrePersonnes := entryPersonnes.Text
		prixTotal := entryPrix.Text

		if nombrePersonnes == "" || prixTotal == "" || tvaRate == "" {
			fmt.Println("Veuillez remplir tous les champs !")
			return
		}

		generatePDF(nombrePersonnes, prixTotal, tvaRate)

		fmt.Println("PDF et CSV générés avec succès !")
	})

	w.SetContent(container.NewVBox(
		labelPersonnes,
		entryPersonnes,
		labelPrix,
		entryPrix,
		varSurPlace,
		generateButton,
	))

	w.ShowAndRun()
}
