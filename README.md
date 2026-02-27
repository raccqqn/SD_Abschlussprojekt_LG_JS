# SD_Abschlussprojekt_LG_JS
![](resources/logo_1.png)
## Projektübersicht

...

## Minimalanforderung

Die definierten Minimalanforderungen wurden zur Gänze erfüllt und befinden sich nachfolgend aufgelistet:

- Programmiert mit Python und User Interface umgesetzt mit streamlit.
- Die Geometrie eines beliebigen 2D Balkens und 3D Körpers wird durch das Eingabefeld definiert. Alle nachfolgenden Funktionen werden automatisch an die gewählte Dimension angepasst. 
- Randbedingungen und Kräfte können an jedem Massepunkt der Ausgangsstruktur platziert werden.
- Die Struktur wird bereits beim Definieren der Maße, beim Wählen der Lager und beim Ansetzen der Kräfte dargestellt. Bei der Optimierung erscheint ein Plot nach jeder Iteration und die resultierende Verschiebung wird anschließend dargestellt. 
- Zu jedem Zeitpunkt kann die Struktur in einem Hybrid-System aus einer JSON-Datei und dem Numpy Binär-Format NPZ gespeichert werden. Durch das Speichern der Randbedingungen und des Optimierungszustandes ist ein späteres Laden und Anpassen der Konfiguration problemlos möglich. 
- Die Struktur besteht aus einem Knoten-Federn System, wodurch das FEM Prinzip angewendet ist. 
- Verschiedene Überprüfungen und Fehlermeldungen während der Optimierung vermeiden statisch instabile Systeme. 
- Die Verwendung von Plotly als Visualisierungs-Lösung erlaubt ein einfache Exportieren der Ergebnisse als png-Datei. 

## Anwendung anhand des Messerschmitt–Bölkow–Blohm (MBB)
Um die Nutzung zu verstehen, wird die Anwendung anhand des Messerschmitt-Bölkow-Blohm Balken durchgeführt. 

1) Neue Struktur erstellen. 
![](resources/1_Startseite.png)

2) Die gewünschten Maße der Geometrie eingeben und bestätigen. 
![](resources/2_Geometrie.png)

3) Lager und Kräfte ansetzen.
![](resources/3_Kraft_bestimmen.png) 

4) Einstellungen am Optimierer treffen. 
![](resources/4_Eso_Optimierung_Einstellungen.png) 

## Erweiterungen

...