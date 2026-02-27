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
Zu den Minimalanforderungen wurden zusätzliche Erweiterungen implementiert:

-	Erweiterung auf 3D-Strukturen: User Interface passt sich automatisch der geänderten Dimension an. 
-	Implementierung der SIMP basierten Topologie Optimierung, die die Nachgiebigkeit als Optimierungskriterium besitzt. Dabei liegt der Fokus auf ein effizientes Lösen und die Laufzeit wird über Profiling minimiert. 
-	Durchdachtes User Interface: 
    -	Position der Lager durch eingebaute Streamlit Widgets schneller setzen (in 2D und 3D)
    -	Ausgrauen/Inaktivieren von Buttons, je nach Bedingungen
    -	Kraftangriff zusätzlich durch Slider-Funktionen bestimmen (in 2D und 3D)
    -	Verschiedene Wanungen verhindern ungewollte User-Errors (fehlender Input, nicht ausreichende Lagerung, zusätzliche Bestätigung zum Löschen/Schließen) 
    -   Optisch ansprechendes Design (Hintergrundbild auf Startseite, selbstentwickeltes Logo in Sidebar) - Rechte für Bild und Schriftarten sind vorhanden.
-	Sinnvolles Speichermanagement: Hybrides System aus einer JSON Datei und dem Numpy Binär-Format NPZ.
-	Ausführliche Struktur-Analyse: Nach der Optimierung werden neben der optimierten Struktur inklusive Lager und Kräften auch die Verformung, Feder-Energien und Feder-Kräft ansprechend dargestellt.