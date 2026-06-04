# DataLoad NFO Creator v1.9.7

Ein moderner, schlanker und benutzerfreundlicher NFO- und Forenbeitrags-Generator auf Basis von Python und CustomTkinter. Das Tool analysiert technische Daten von Videodateien automatisiert via `ffprobe` und verbindet diese mit redaktionellen Informationen (Plot, Genres, Jahr) direkt aus der TMDb-Datenbank (The Movie Database).

---

## 🚀 Features

- **Automatische Videoanalyse:** Liest Auflösung, Codecs, Bitraten, Laufzeit, Audio- und Untertitelspuren direkt aus `.mkv`, `.mp4` oder `.avi` aus.
- **TMDb-Integration:** Intelligente Titelsuche inklusive automatischer Auflösung von Mehrfachtreffern (Inline-Auswahlliste) und Abruf von Postern, Plots und Genres.
- **Drei-Tab-Interface:**
  1. *Hauptseite:* Dateiauswahl, Filmtitel-Suche und NFO-Generierung.
  2. *Einstellungen:* API-Key Verwaltung, Live-NFO-Vorschau und flexible Anpassung der NFO-Labels.
  3. *Beitrag Erstellen:* Automatisierte Generierung von fertig formatiertem BBCode für Foren (inkl. Hoster-Auswahl, Download-Code-Block und NFO-Spoiler).
- **Responsive Layout:** Wechselt per Knopfdruck nahtlos zwischen einer Vollansicht ($750 \times 920$ Pixel) und einem kompakten Mini-Modus ($450 \times 650$ Pixel) für die platzsparende Nutzung nebenbei.
- **Rechtsklick-Kontextmenü:** Volle Unterstützung für Ausschneiden, Kopieren, Einfügen und Alles auswählen in allen Textfeldern.

---

## 🛠️ Voraussetzungen für Entwickler

Wenn du am Quellcode arbeiten oder das Skript selbst ausführen möchtest, müssen folgende Abhängigkeiten auf deinem System installiert sein.

### 1. Python
- Empfohlen: **Python 3.10 oder höher**

### 2. Benötigte Bibliotheken
Installiere die externen Abhängigkeiten ganz einfach über den Paketmanager `pip`:

```bash
pip install customtkinter pillow requests