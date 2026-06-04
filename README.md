# DataLoad NFO Creator

Ein moderner, schlanker und benutzerfreundlicher NFO- und Forenbeitrags-Generator auf Basis von Python und CustomTkinter.

Das Tool analysiert technische Daten von Videodateien automatisiert via `ffprobe` und verbindet diese mit redaktionellen Informationen (Plot, Genres, Jahr) direkt aus der TMDb-Datenbank (The Movie Database).

---

## Features

###  Automatische Videoanalyse

* Liest Auflösung, Codecs, Bitraten, Laufzeit sowie Audio- und Untertitelspuren direkt aus `.mkv`, `.mp4` oder `.avi` Dateien aus.

###  TMDb-Integration

* Intelligente Titelsuche
* Automatische Auflösung von Mehrfachtreffern (Inline-Auswahlliste)
* Abruf von Postern, Plots und Genres

###  Drei-Tab-Interface

#### Hauptseite

* Dateiauswahl
* Filmtitel-Suche
* NFO-Generierung

#### Einstellungen

* API-Key-Verwaltung
* Live-NFO-Vorschau
* Flexible Anpassung der NFO-Labels

#### Beitrag erstellen

* Automatisierte Generierung von fertig formatiertem BBCode für Foren
* Hoster-Auswahl
* Download-Code-Block
* NFO-Spoiler

### 📐 Responsive Layout

* Wechsel per Knopfdruck zwischen:

  * **Vollansicht:** 750 × 920 Pixel
  * **Mini-Modus:** 450 × 650 Pixel

### 📝 Rechtsklick-Kontextmenü

* Ausschneiden
* Kopieren
* Einfügen
* Alles auswählen

---

# Voraussetzungen für Entwickler

Wenn du am Quellcode arbeiten oder das Skript selbst ausführen möchtest, müssen folgende Abhängigkeiten auf deinem System installiert sein.

## 1. Python

**Empfohlen:** Python 3.10 oder höher

## 2. Benötigte Bibliotheken

Installiere die externen Abhängigkeiten über `pip`:

```bash
pip install customtkinter pillow requests
```

> Hinweis: Die Standardbibliotheken `tkinter`, `subprocess`, `json`, `os`, `sys`, `textwrap` und `re` sind bereits Bestandteil von Python.

## 3. Externe Binärdateien (Wichtig)

Das Programm benötigt `ffprobe.exe` (Teil des FFmpeg-Projekts) für die Videoanalyse.

1. Erstelle im Projektverzeichnis einen Ordner namens `bin`
2. Platziere die Datei `ffprobe.exe` in diesem Ordner:

```text
/bin/ffprobe.exe
```

---

# Projektstruktur

Für eine korrekte Funktion im Entwicklungsmodus und beim Kompilieren sollte die Ordnerstruktur wie folgt aussehen:

```text
project/
│
├── main.py              # Hauptquellcode des Programms
├── app_icon.ico         # Anwendungs-Icon
├── logo.png             # Großes Branding-Logo
├── logo_small.png       # Kleines Logo für den Kompaktmodus
├── settings.json        # API-Key & NFO-Konfiguration
│
└── bin/
    └── ffprobe.exe      # Tool zur Videoanalyse
```

---

# Kompilieren zu einer eigenständigen EXE

Um das Projekt in eine einzelne ausführbare Windows-Datei (`.exe`) zu verwandeln, wird PyInstaller verwendet.

Dadurch werden alle Grafiken, Bibliotheken und auch `ffprobe.exe` direkt in die Anwendung integriert.

## Schritt 1: PyInstaller installieren

```bash
pip install pyinstaller
```

## Schritt 2: Build-Befehl ausführen

Führe folgenden Befehl im Terminal oder in der Eingabeaufforderung aus:

```bash
python -m PyInstaller ^
--noconsole ^
--onefile ^
--add-data "logo.png;." ^
--add-data "logo_small.png;." ^
--add-data "app_icon.ico;." ^
--add-data "bin;bin" ^
--collect-all customtkinter ^
--icon="app_icon.ico" ^
main.py
```

### Erklärung der Parameter

| Parameter                     | Beschreibung                                            |
| ----------------------------- | ------------------------------------------------------- |
| `--noconsole`                 | Blendet das CMD-Fenster beim Start der Anwendung aus    |
| `--onefile`                   | Erstellt eine einzelne ausführbare Datei                |
| `--add-data`                  | Bindet Logos, Icons und den kompletten `bin`-Ordner ein |
| `--collect-all customtkinter` | Fügt alle Assets und Themes von CustomTkinter hinzu     |
| `--icon`                      | Setzt das Windows-Anwendungsicon                        |

Nach erfolgreichem Build befindet sich die fertige Datei unter:

```text
dist/main.exe
```

---

# Mitwirken (Contributing)

Beiträge, Fehlerberichte und Feature-Wünsche sind herzlich willkommen.

1. Forke das Projekt.
2. Erstelle einen Feature-Branch:

```bash
git checkout -b feature/AmazingFeature
```

3. Committe deine Änderungen:

```bash
git commit -m "Add some AmazingFeature"
```

> Bitte achte auf saubere Formatierung und vermeide unnötige Trailing Semicolons am Zeilenende.

4. Pushe den Branch:

```bash
git push origin feature/AmazingFeature
```

5. Öffne einen Pull Request.

---

# Lizenz

Dieses Projekt ist für private Zwecke und die Community gedacht.

Bitte gehe respektvoll mit den genutzten APIs um.

---

## Entwickler

**Entwickelt von Dwarfpicker**
