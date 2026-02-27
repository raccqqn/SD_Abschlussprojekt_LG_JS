# SD_Abschlussprojekt_LG_JS
### Joachim Spitaler und Leonie Graf

Für das Abschlussprojekt im 3. Semester Mechatronik in Softwaredesign wurde eine Anwendung erstellt, die die Materialverteilung eines Balkens optimiert. Die Geometrien, Randbedingungen und Lasten werden in der Applikation gesetzt und die Optimierung geschieht in Anlehnung an die FEM-Methode. 



## Minimalanforderung

Die Streamlit Seite kann durch das Ausführen von ```streamlit run .\Startseite.py``` im Terminal geladen werden. Die definierten Minimalanforderungen wurden zur Gänze erfüllt und befinden sich nachfolgend aufgelistet.

- Programmiert mit Python und User Interface umgesetzt mit streamlit.
- Die Geometrie eines beliebigen 2D Balkens und 3D Körpers wird durch das Eingabefeld definiert. Alle nachfolgenden Funktionen werden automatisch an die gewählte Dimension angepasst. 
- Randbedingungen und Kräfte können an jedem Massepunkt der Ausgangsstruktur platziert werden.
- Die Struktur wird bereits beim Definieren der Maße, beim Wählen der Lager und beim Ansetzen der Kräfte dargestellt. Bei der Optimierung erscheint ein Plot nach jeder Iteration und die resultierende Verschiebung wird anschließend dargestellt. 
- Struktur kann zu jedem Zeitpunkt gespeichert werden. Durch das Speichern der Randbedingungen und des Optimierungszustandes ist ein späteres Laden und Anpassen der Konfiguration problemlos möglich. 
- Die Struktur besteht aus einem Knoten-Federn System, wodurch das FEM Prinzip angewendet ist. 
- Verschiedene Überprüfungen und Fehlermeldungen während der Optimierung vermeiden statisch instabile Systeme. 
- Die Verwendung von Plotly als Visualisierungs-Lösung erlaubt ein einfache Exportieren der Ergebnisse als png-Datei. 

Die Benutzeroberfläche hat viele Implementierungen und ist sehr intuitiv für den Nutzer, wodurch auf eine detaillierte Erklärung verzichtet wird.
## Optimierung des Messerschmitt–Bölkow–Blohm Balkens (MBB)



### 2D SIMP Optimierung

Mit den Einstellungen ```Zielvolumen = 35%, Iterationen = 30, Filter = 1.5, Cleanup = mittel```  ergibt sich folgende Optimierung:
<table width="100%" style="border-collapse: collapse;">

<tr>
<td width="50%" valign="top" align="center"
    style="border-right: 1px solid #444; border-bottom: 1px solid #444;">

<h4>Optimierte Struktur</h4>
<img src="resources/SIMP_2D.png" width="90%">

</td>

<td width="50%" valign="top" align="center"
    style="border-bottom: 1px solid #444;">

<h4>Verformung</h4>
<img src="resources/SIMP_2D_verformung.png" width="90%">

</td>
</tr>

<tr>
<td width="50%" valign="top" align="center"
    style="border-right: 1px solid #444;">

<h4>Normalkraft-Analyse</h4>
<img src="resources/SIMP_2D_kraefte.png" width="90%">

</td>

<td width="50%" valign="top" align="center">

<h4>Federenergien-Analyse</h4>
<img src="resources/SIMP_2D_energies.png" width="90%">

</td>
</tr>

</table>

### 2D ESO Optimierung
Mit den Einstellungen ```Zielvolumen = 35%, Aggressivität = 0.3```  ergibt der nachfolgend optimierte Balken:
<div align="center">
    <img src="resources/ESO_2D.png" width="70%">
</div>

## Optimierung von 3D Körpern

### 3D SIMP Optimierung

Bei der Optimierung von 3D Objekten ist auf eine korrekte Lagerung zu achten. Bei mangelhafter Befesetigung funktioniert eine Optimierung mit der SIMP Methode nicht. Falls dies jedoch der Fall sein sollte, wird man von einer Fehlermeldung darauf aufmerksam gemacht. Mit den Einstellungen ```Zielvolumen = 35%, Iterationen = 30, Filter = 1.5, Cleanup = mittel``` ergibt sich der nachfolgend optimierte Körper:

<div align="center">
    <img src="resources/ESO_2D.png" width="70%">
</div>

### 3D ESO Optimierung

Die Eso Optimierung liefert für dreidimensionale Körper keine realistisch umsetzbaren Strukturen. Beispielsweise liefern die Optimierungsparameter ```Zielvolumen = 35%, Aggressivität = 0.3```  die folgende Struktur:

<div align="center">
    <img src="resources/ESO_2D.png" width="70%">
</div>

## Erweiterungen

...







# Methodik und Fokus der Implementierung

Im Rahmen des Projekts wurde besonderer Wert auf eine nachvollziehbare und klare Strukturierung gelegt. Dies erreichten wir durch eine logische Verknüpfung der Klassen und eine konsequente Trennung der Funktionalitäten.

## Herausforderungen der ESO-Optimierung

Obwohl der Fokus anfangs auf der vorgeschlagenen **ESO-Optimierung (Evolutionary Structural Optimization)** lag, traten hierbei signifikante Herausforderungen auf. Da das Entfernen von Knoten oft die Integrität des mechanischen Systems gefährdet, haben wir verschiedene Prüfroutinen implementiert, die das System bereits vor dem Löschen auf seine zukünftige Stabilität untersuchen. Da eine lückenlose Prüfung insbesondere bei komplexen Strukturen jedoch zu extrem langen Rechenzeiten führt, lag die größte Schwierigkeit darin, einen effizienten Kompromiss zwischen Rechengeschwindigkeit und Vorhersagegenauigkeit zu finden.

Das Endergebnis der ESO-Implementierung ist somit primär auf eine vertretbare Rechenzeit ausgelegt. Da der Fokus im weiteren Projektverlauf auf das SIMP-Verfahren verlagert wurde, ist dieser Teil nicht voll ausgereift; insbesondere 3D-Strukturen können aufgrund der aktuell noch zu primitiven Prüflogik nur bedingt optimiert werden.

## Implementierung des SIMP-Verfahrens

Aufgrund dieser Limitationen haben wir ein zweites Optimierungsverfahren auf Basis eines **SIMP-Modells (Solid Isotropic Material with Penalization)** integriert. Hierbei wird über eine Empfindlichkeitsanalyse der Federelemente die Gesamtnachgiebigkeit minimiert, während ein Lagrange-Verfahren sicherstellt, dass das Zielvolumen als Nebenbedingung eingehalten wird.

Viel Zeit floss dabei in die Performance-Optimierung:

* **Laufzeitanalyse:** Mithilfe von `cProfile` wurden ineffiziente Methoden identifiziert und gezielt eliminiert.
* **Effizienz:** Das Ergebnis ist ein zuverlässiges Verfahren, das selbst große Strukturen schnell und fehlerfrei berechnet.
* **Benutzerkontrolle:** Durch variabel einstellbare Filter (Anpassung der Sensitivität an benachbarte Elemente) und eine steuerbare Struktur-Bereinigung behält der Anwender die volle Kontrolle über das Endergebnis.

## Qualität vor Quantität

Ein weiterer Schwerpunkt war die saubere Einbettung aller Erweiterungen in die Benutzeroberfläche (UI). Um eine möglichst hohe Benutzerfreundlichkeit zu gewährleisten, haben wir das Tool durch externe Testpersonen prüfen lassen. Verschiedene Hilfsfunktionen erleichtern nun die Eingabe der Randbedingungen. Zudem verhindern implementierte Safeguards sowie ein durchdachtes Speichermanagement via `Session States` Bedienfehler und ermöglichen einen flüssigen Workflow. Endergebnisse werden visuell Ansprechend und interaktiv dargestellt.


# Quellen und Ressourcennutzung

Während des Projekts wurde großer Wert darauf gelegt, sämtliche Konzepte eigenständig umzusetzen und zu verstehen. Die gesamte Programmstruktur sowie das User Interface wurden eigenständig konzipiert und ausgearbeitet. Obwohl eine exzessive Kommentierung im professionellen Software-Engineering unüblich ist, wurde sie hier bewusst eingesetzt, um den eigenen Lernprozess zu dokumentieren und die Nachvollziehbarkeit zu erhöhen.

Als Hilfestellung dienten Internet-Recherchen in Fachforen, wissenschaftlichen Papern und Dokumentationen (Reddit, YouTube, Stack Overflow sowie verschiedene Library-Websites).

## Nutzung von Large Language Models (LLMs)

LLMs wurden als Hilfsmittel verwendet, um programmiertechnische Konzepte effizienter aufnehmen zu können. Dabei wurde strikt darauf geachtet, keine fertigen Code-Blöcke blind zu übernehmen. Vielmehr dienten LLMs als Wissensdatenbank, um spezifische Probleme zu diskutieren und Lösungswege zu überprüfen, anstatt die Programmierarbeit auszulagern.

Die KI lieferte bei den folgenden Konzepten die initialen Lösungsansätze:
* **Hybrid-Speichersystem:** Kombination aus JSON- und npz-Dateien für Datenspeicherung.
* **Lagrange-Verfahren:** Einsatz bei der SIMP-Optimierung zur Einhaltung der Nebenbedingungen.
* **Performance-Steigerung:** Vorberechnung benachbarter Knoten bei der SIMP-Optimierung.
* **Rendering:** Nutzung von WebGL für eine effizientere Darstellung der Plots.

### Ausnahme: Enddarstellung der Strukturen
Die einzige Ausnahme bildet die Datei `plots.py`. In der Klasse "Plotter" wurde Code stellenweise direkt von Google Gemini generiert übernommen. Da das Plotten stark von spezifischen Bibliotheks-Optionen abhängt und die optische Anpassung der Darstellung einen hohen zeitlichen Aufwand für "Kleinarbeit" bedeutet, haben wir uns aufgrund von Zeitmangel für diesen Weg entschieden. Der übernommene Code wurde jedoch vollständig überprüft, im Detail nachvollzogen und an unsere Anforderungen angepasst.