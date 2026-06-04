# DataLoad NFO Creator 

Ein moderner, schlanker und benutzerfreundlicher NFO- und Forenbeitrags-Generator auf Basis von Python und CustomTkinter. Das Tool analysiert technische Daten von Videodateien automatisiert via ffprobe und verbindet diese mit redaktionellen Informationen (Plot, Genres, Jahr) direkt aus der TMDb-Datenbank (The Movie Database).

---

## Features

- Automatische Videoanalyse: Liest Auflösung, Codecs, Bitraten, Laufzeit, Audio- und Untertitelspuren direkt aus .mkv, .mp4 oder .avi aus.
- TMDb-Integration: Intelligente Titelsuche inklusive automatischer Auflösung von Mehrfachtreffern (Inline-Auswahlliste) und Abruf von Postern, Plots und Genres.
- Drei-Tab-Interface:
  1. Hauptseite: Dateiauswahl, Filmtitel-Suche und NFO-Generierung.
  2. Einstellungen: API-Key Verwaltung, Live-NFO-Vorschau und flexible Anpassung der NFO-Labels.
  3. Beitrag Erstellen: Automatisierte Generierung von fertig formatiertem BBCode für Foren (inkl. Hoster-Auswahl, Download-Code-Block und NFO-Spoiler).
- Responsive Layout: Wechselt per Knopfdruck nahtlos zwischen einer Vollansicht (750 x 920 Pixel) und einem kompakten Mini-Modus (450 x 650 Pixel) für die platzsparende Nutzung nebenbei.
- Rechtsklick-Kontextmenü: Volle Unterstützung für Ausschneiden, Kopieren, Einfügen und Alles auswählen in allen Textfeldern.

---

## Voraussetzungen für Entwickler

Wenn du am Quellcode arbeiten oder das Skript selbst ausführen möchtest, müssen folgende Abhängigkeiten auf deinem System installiert sein.

### 1. Python
- Empfohlen: Python 3.10 oder höher

### 2. Benötigte Bibliotheken
Installiere die externen Abhängigkeiten ganz einfach über den Paketmanager pip:

[ BEFEHL ]
pip install customtkinter pillow requests
[ /BEFEHL ]

Hinweis: Die Standardbibliotheken tkinter, subprocess, json, os, sys, textwrap und re sind bereits in Python integriert.

### 3. Externe Binärdateien (Wichtig!)
Das Programm benötigt ffprobe.exe (Teil des FFmpeg-Projekts) für die Videoanalyse.
- Erstelle im Projektverzeichnis einen Ordner namens bin.
- Platziere die ffprobe.exe in diesem Ordner (/bin/ffprobe.exe).

---

## Projektstruktur

Für eine korrekte Funktion im Entwicklungsmodus und beim Kompilieren muss die Ordnerstruktur wie folgt aussehen:

[ STRUKTUR ]
+-- main.py              # Der Hauptquellcode des Programms
+-- app_icon.ico         # Das Icon der Anwendung
+-- logo.png             # Großes Branding-Logo für die Hauptansicht
+-- logo_small.png       # Kleines Logo für den Kompaktmodus
+-- settings.json        # Speichert API-Key und NFO-Feldkonfiguration
+-- bin/
    +-- ffprobe.exe      # Das Tool zur Videoanalyse
[ /STRUKTUR ]

---

## Kompilieren zu einer eigenständigen .exe

Um das Projekt in eine einzige, ausführbare Windows-Datei (.exe) zu verwandeln, wird PyInstaller verwendet. Dadurch werden alle Grafiken, Bibliotheken und sogar die ffprobe.exe direkt in die Datei integriert.

### Schritt 1: PyInstaller installieren
[ BEFEHL ]
pip install pyinstaller
[ /BEFEHL ]

### Schritt 2: Build-Befehl ausführen
Nutze exakt diesen Befehl in deiner Eingabeaufforderung (CMD) oder im Terminal deines Editors, um die Anwendung fehlerfrei zu verpacken:

[ BEFEHL ]
python -m PyInstaller --noconsole --onefile --add-data "logo.png;." --add-data "logo_small.png;." --add-data "app_icon.ico;." --add-data "bin;bin" --collect-all customtkinter --icon="app_icon.ico" main.py
[ /BEFEHL ]

### Erklärung der Parameter:
- --noconsole: Blendet das schwarze CMD-Hintergrundfenster beim Start der App aus.
- --onefile: Schnürt das gesamte Programm inklusive aller Abhängigkeiten in eine einzige .exe.
- --add-data ...: Bettet die Logos, das Icon und den kompletten bin-Ordner (inkl. ffprobe.exe) direkt in den internen Speicher der App ein.
- --collect-all customtkinter: Zwingt PyInstaller dazu, alle Assets (Themes, Schriften) von CustomTkinter mitzunehmen.
- --icon=...: Setzt das Anwendungs-Icon für die Windows-Ansicht.

Nach erfolgreichem Build findest du die fertige Datei im neu entstandenen Ordner dist/main.exe.

---

## Mitwirken (Contributing)

Beiträge, Fehlerberichte und Feature-Wünsche sind herzlich willkommen!

1. Forke das Projekt.
2. Erstelle einen Feature-Branch (git checkout -b feature/AmazingFeature).
3. Commit deine Änderungen (git commit -m 'Add some AmazingFeature'). Achte im Code bitte penibel auf saubere Formatierung und vermeide Trailing Semicolons am Zeilenende.
4. Pushe den Branch (git push origin feature/AmazingFeature).
5. Öffne einen Pull Request.

---

## Lizenz

Dieses Projekt ist für private Zwecke und die Community gedacht. Bitte geh respektvoll mit den genutzten APIs um.

Entwickelt von Dwarfpicker