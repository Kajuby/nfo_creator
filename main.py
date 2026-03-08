import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import json
import os
import sys
import textwrap
import requests
from cinemagoerng import web as imdb_web
from PIL import Image


# Hilfspfad-Funktion für PyInstaller Ressourcen
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class NFOCreator(ctk.CTk):
    # App-Initialisierung: Fenster-Setups, Themes und Konfiguration laden
    def __init__(self):
        super().__init__()
        self.title("DataLoad NFO Creator v1.3.1 - by Dwarfpicker")

        # Icon für Fenster und Taskleiste setzen
        try:
            self.iconbitmap(resource_path("app_icon.ico"))
        except Exception:
            pass

        # Definierte Fenster-Maße
        self.width_full, self.height_full = 750, 900
        self.width_mini, self.height_mini = 400, 600

        # Standard-Felder (Sprachlich optimiert)
        self.default_fields = [
            {"id": "title",   "name": "Titel",    "label": "Title............:", "enabled": True, "placeholder": "$Filmtitel"},
            {"id": "year",    "name": "Year",     "label": "Year.............:", "enabled": True, "placeholder": "$Jahr"},
            {"id": "imdb",    "name": "IMDB",     "label": "IMDb.............:", "enabled": True, "placeholder": "$IMDB_Link"},
            {"id": "genre",   "name": "Genre",    "label": "Genre............:", "enabled": True, "placeholder": "$Genre"},
            {"id": "plot",    "name": "Plot",     "label": "Plot.............:", "enabled": True, "placeholder": "$Plot"},
            {"id": "format",  "name": "Format",   "label": "Format...........:", "enabled": True, "placeholder": "$Video_Format"},
            {"id": "video",   "name": "Video",    "label": "Video............:", "enabled": True, "placeholder": "$Video_Auflösung"},
            {"id": "audio",   "name": "Audio",    "label": "Audio............:", "enabled": True, "placeholder": "$Audiospur"},
            {"id": "subs",    "name": "Subtitle", "label": "Subtitles........:", "enabled": True, "placeholder": "$Untertitel"},
            {"id": "runtime", "name": "Runtime",  "label": "Runtime..........:", "enabled": True, "placeholder": "$Laufzeit"}
        ]

        self.settings_file = "settings.json"
        self.settings      = self.load_settings()
        self.is_compact    = self.settings.get("compact_mode", False)

        # Farben und Styling
        self.bg_color           = "#1f2530"
        self.tab_color_active   = "#1f2530"
        self.tab_color_inactive = "#161b22"
        self.border_color       = "white"

        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=self.bg_color)

        self.selected_file = ""
        self.poster_url    = ""
        self.ffprobe_path  = resource_path(os.path.join("bin", "ffprobe.exe"))

        # --- UI STRUKTUR ---
        # Kopfleiste für Resize-Button
        self.top_header = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self.top_header.pack(fill="x", padx=10, pady=5)

        self.btn_resize = ctk.CTkButton(self.top_header, text="1/2", width=30, height=20,
                                        fg_color=self.tab_color_inactive, border_width=1, border_color="white",
                                        font=("Arial", 10, "bold"), text_color="white",
                                        command=self.toggle_window_size)
        self.btn_resize.pack(side="right")

        # Haupt-Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Logo-Bereich
        self.logo_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.logo_frame.pack(fill="x", pady=(0, 5))

        # Laden der Logo-Dateien (Groß & Klein)
        self.load_branding_assets()

        # Tabs (Folder-Stil)
        self.tab_frame = ctk.CTkFrame(self.main_container, fg_color="transparent", height=45)
        self.tab_frame.pack(fill="x", pady=(10, 0))
        self.tab_frame.pack_propagate(False)

        self.btn_tab_main = ctk.CTkButton(self.tab_frame, text="Hauptseite", command=lambda: self.switch_tab("main"),
                                          corner_radius=10, border_width=2, height=45, font=("Arial", 13, "bold"))
        self.btn_tab_main.pack(side="left", expand=True, fill="both")

        self.btn_tab_settings = ctk.CTkButton(self.tab_frame, text="Einstellungen",
                                              command=lambda: self.switch_tab("settings"),
                                              corner_radius=10, border_width=2, height=45, font=("Arial", 13, "bold"))
        self.btn_tab_settings.pack(side="left", expand=True, fill="both")

        # Inhaltsbereich
        self.folder_body = ctk.CTkFrame(self.main_container, fg_color=self.bg_color, corner_radius=15,
                                        border_width=2, border_color=self.border_color)
        self.folder_body.pack(fill="both", expand=True, pady=(0, 10))

        self.page_main = ctk.CTkFrame(self.folder_body, fg_color="transparent")
        self.page_settings = ctk.CTkFrame(self.folder_body, fg_color="transparent")

        self.field_widgets = {}
        self.setup_main_page()
        self.setup_settings_page()

        self.apply_stored_size()
        self.switch_tab("main")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Lädt die Logo-Dateien und erstellt die Labels für alle Modi
    def load_branding_assets(self):
        # Normales Logo
        try:
            img_big = Image.open(resource_path("logo.png"))
            self.ctk_logo_big = ctk.CTkImage(light_image=img_big, dark_image=img_big, size=(400, 185))
            self.logo_label_img = ctk.CTkLabel(self.logo_frame, image=self.ctk_logo_big, text="")
        except:
            self.logo_label_img = ctk.CTkLabel(self.logo_frame, text="DataLoad NFO Creator", font=("Arial", 22, "bold"))

        # Kompaktes Logo
        try:
            img_small = Image.open(resource_path("logo_small.png"))
            self.ctk_logo_small = ctk.CTkImage(light_image=img_small, dark_image=img_small, size=(225, 30))
            self.logo_label_small = ctk.CTkLabel(self.logo_frame, image=self.ctk_logo_small, text="")
        except:
            self.logo_label_small = None

        # Text-Ersatz IMMER erstellen
        self.logo_label_text = ctk.CTkLabel(self.logo_frame, text="DataLoad NFO Creator", font=("Arial", 16, "bold"),
                                            text_color="white")

    # Manuelle Clipboard-Verarbeitung für echtes Windows-Rechtsklick-Verhalten
    def add_context_menu(self, widget):
        menu = tk.Menu(widget, tearoff=0, bg="#161b22", fg="white", activebackground="#2ecc71")

        def do_cut():
            do_copy()
            try:
                widget.delete("sel.first", "sel.last")
            except:
                pass

        def do_copy():
            try:
                selected_text = widget._entry.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
            except:
                pass

        def do_paste():
            try:
                text = self.clipboard_get()
                if widget.select_present():
                    widget.delete("sel.first", "sel.last")
                widget.insert("insert", text)
            except:
                pass

        menu.add_command(label="Ausschneiden", command=do_cut)
        menu.add_command(label="Kopieren", command=do_copy)
        menu.add_command(label="Einfügen", command=do_paste)
        menu.add_separator()
        menu.add_command(label="Alles auswählen", command=lambda: widget.select_range(0, 'end'))

        def show_menu(event):
            widget.focus_set()
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)

    # Initialisiert die Fenstergröße basierend auf den gespeicherten Werten
    def apply_stored_size(self):
        if self.is_compact:
            self.is_compact = False
            self.toggle_window_size()
        else:
            self.geometry(f"{self.width_full}x{self.height_full}")
            self.minsize(650, 800)
            self.logo_label_img.pack()

    # Wechselt zwischen 1/1 (Full) und 1/2 (Kompakt) Layout
    def toggle_window_size(self):
        if not self.is_compact:
            # ZU KOMPAKT WECHSELN
            self.minsize(300, 400)
            self.geometry(f"{self.width_mini}x{self.height_mini}")
            self.btn_resize.configure(text="1/1")
            self.is_compact = True

            self.logo_label_img.pack_forget()
            if self.logo_label_small:
                self.logo_label_small.pack(pady=5)
            else:
                self.logo_label_text.pack(pady=10)

            self.log_box.configure(height=70)
            self.preview_label.pack_forget()
            self.preview_box.pack_forget()
        else:
            # ZU NORMAL WECHSELN
            self.geometry(f"{self.width_full}x{self.height_full}")
            self.minsize(650, 800)
            self.btn_resize.configure(text="1/2")
            self.is_compact = False

            if self.logo_label_small: self.logo_label_small.pack_forget()
            self.logo_label_text.pack_forget()
            self.logo_label_img.pack()

            self.log_box.configure(height=200)

            # FIX: Vorschau wieder korrekt einblenden mit allen Parametern
            self.preview_label.pack(pady=(15, 0))
            self.preview_box.pack(fill="both", expand=True, pady=10)

    # Steuert das Ein- und Ausblenden der Inhaltsseiten (Tabs)
    def switch_tab(self, tab_name):
        if tab_name == "main":
            self.page_settings.pack_forget()
            self.page_main.pack(fill="both", expand=True, padx=10, pady=10)
            self.btn_tab_main.configure(fg_color=self.tab_color_active, border_color=self.border_color,
                                        text_color="white")
            self.btn_tab_settings.configure(fg_color=self.tab_color_inactive, border_color=self.tab_color_inactive,
                                            text_color="gray")
        else:
            self.page_main.pack_forget()
            self.page_settings.pack(fill="both", expand=True, padx=10, pady=10)
            self.btn_tab_main.configure(fg_color=self.tab_color_inactive, border_color=self.tab_color_inactive,
                                        text_color="gray")
            self.btn_tab_settings.configure(fg_color=self.tab_color_active, border_color=self.border_color,
                                            text_color="white")
            self.update_preview()

    # Erstellt die Bedienelemente für die Hauptseite
    def setup_main_page(self):
        ctk.CTkButton(self.page_main, text="1. Video Datei auswählen", command=self.select_file, height=35).pack(
            pady=(10, 5))
        self.label_file_path = ctk.CTkLabel(self.page_main, text="Keine Datei ausgewählt", font=("Arial", 10, "italic"))
        self.label_file_path.pack()

        ctk.CTkLabel(self.page_main, text="Filmtitel für die Suche:", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        self.entry_title = ctk.CTkEntry(self.page_main, width=400)
        self.entry_title.pack(pady=5)
        self.add_context_menu(self.entry_title)

        ctk.CTkLabel(self.page_main, text="Bessere Ergebnisse wenn man das Jahr hinzufügt.\nBeispiel: Broken (2012)",
                     font=("Arial", 10), text_color="gray", justify="center").pack()

        self.imdb_frame = ctk.CTkFrame(self.page_main, fg_color="transparent")
        self.imdb_frame.pack(pady=10)
        self.entry_imdb = ctk.CTkEntry(self.imdb_frame, width=150, placeholder_text="tt0133093")
        self.entry_imdb.pack(side="left", padx=5)
        self.add_context_menu(self.entry_imdb)

        ctk.CTkButton(self.imdb_frame, text="2. ID Suchen", width=120, command=self.search_imdb_stable).pack(
            side="left")

        self.cover_var = ctk.BooleanVar(value=self.settings.get("cover", True))
        ctk.CTkCheckBox(self.page_main, text="Cover herunterladen", variable=self.cover_var).pack(pady=5)

        self.log_box = ctk.CTkTextbox(self.page_main, width=600, height=200, font=("Consolas", 11), fg_color="#161b22")
        self.log_box.pack(fill="both", expand=True, pady=10)

        ctk.CTkButton(self.page_main, text="3. NFO Erstellen", fg_color="#2ecc71", hover_color="#27ae60",
                      command=self.start_process, height=45, font=("Arial", 14, "bold")).pack(pady=(0, 10))

    # Erstellt die Bedienelemente für die Einstellungen
    def setup_settings_page(self):
        settings_container = ctk.CTkFrame(self.page_settings, fg_color="transparent")
        settings_container.pack(pady=10)

        for field in self.settings["fields"]:
            row = ctk.CTkFrame(settings_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            var = ctk.BooleanVar(value=field["enabled"])
            cb = ctk.CTkCheckBox(row, text="", variable=var, width=20, command=self.update_preview)
            cb.pack(side="left")

            ent = ctk.CTkEntry(row, width=220)
            ent.insert(0, field["label"])
            ent.pack(side="left", padx=10)
            ent.bind("<KeyRelease>", lambda e: self.update_preview())
            self.add_context_menu(ent)

            ctk.CTkLabel(row, text=field["placeholder"], text_color="gray", font=("Arial", 10)).pack(side="left")
            self.field_widgets[field["id"]] = {"check": var, "entry": ent}

        self.preview_label = ctk.CTkLabel(self.page_settings, text="Vorschau der NFO (Beispiel):",
                                          font=("Arial", 11, "bold"))
        self.preview_label.pack(pady=(15, 0))
        self.preview_box = ctk.CTkTextbox(self.page_settings, width=650, height=250, font=("Consolas", 11),
                                          fg_color="#161b22")
        self.preview_box.pack(fill="both", expand=True, pady=10)

    # Generiert dynamisch die Vorschau für den Einstellungs-Tab
    def update_preview(self):
        preview_text = []
        for field in self.settings["fields"]:
            f_id = field["id"]
            if f_id in self.field_widgets and self.field_widgets[f_id]["check"].get():
                if f_id == "format": preview_text.append("")
                label = self.field_widgets[f_id]["entry"].get()
                preview_text.append(f"{label}  {field['placeholder']}")
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("1.0", "\n".join(preview_text))

    # Lädt die settings.json Konfiguration
    def load_settings(self):
        base_data = {"cover": True, "fields": self.default_fields, "compact_mode": False}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    loaded = json.load(f)
                    if "fields" not in loaded: loaded["fields"] = self.default_fields
                    return loaded
            except:
                return base_data
        return base_data

    # Speichert Konfiguration und Fensterstatus beim Beenden
    def on_closing(self):
        try:
            if self.field_widgets:
                for item in self.settings["fields"]:
                    f_id = item["id"]
                    if f_id in self.field_widgets:
                        item["label"] = self.field_widgets[f_id]["entry"].get()
                        item["enabled"] = self.field_widgets[f_id]["check"].get()
                self.settings["cover"] = self.cover_var.get()
                self.settings["compact_mode"] = self.is_compact
                with open(self.settings_file, "w") as f:
                    json.dump(self.settings, f, indent=4)
        except:
            pass
        self.destroy()

    # Schreibt Statusmeldungen in die Logbox
    def log(self, text, is_error=False):
        prefix = "ℹ️ "
        if is_error: prefix = "❌ "
        self.log_box.insert("end", f"{prefix}{text}\n")
        self.log_box.see("end")
        self.update()

    # Führt eine Suggestion-Suche bei IMDb durch
    def search_imdb_stable(self):
        raw = self.entry_title.get().strip()
        if not raw: return
        term = raw.replace(" ", "_").lower()
        url = f"https://v3.sg.media-imdb.com/suggestion/{term[0]}/{term}.json"
        try:
            res = requests.get(url, timeout=5).json()
            if "d" in res:
                movie = res["d"][0]
                self.entry_imdb.delete(0, "end")
                self.entry_imdb.insert(0, movie["id"])
                self.poster_url = movie.get("i", {}).get("imageUrl", "")
                self.log(f"Gefunden: {movie['l']} ({movie.get('y')})")
        except:
            self.log("Suche fehlgeschlagen.", True)

    # Öffnet den Dateidialog zur Auswahl der Video-Datei
    def select_file(self):
        fn = filedialog.askopenfilename(filetypes=[("Video files", "*.mkv *.mp4 *.avi")])
        if fn:
            self.selected_file = fn
            self.label_file_path.configure(text=fn)
            self.entry_title.delete(0, "end")
            self.entry_title.insert(0, os.path.basename(fn).rsplit('.', 1)[0].replace(".", " "))

    # Holt Film-Metadaten in deutscher Sprache von IMDb
    def get_detailed_info(self, imdb_id):
        self.log(f"Abruf via NextGen Web für: {imdb_id}")
        try:
            custom_headers = {"Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8"}
            movie = imdb_web.get_title(imdb_id, headers=custom_headers)
            genres = movie.genres if movie.genres else []
            year = movie.year if hasattr(movie, 'year') else "N/A"
            plot_raw = movie.plot
            plot_text = "Kein Plot verfügbar."
            if isinstance(plot_raw, dict):
                plot_text = plot_raw.get('de-DE') or plot_raw.get('de') or plot_raw.get('en-US') or \
                            list(plot_raw.values())[0]
            else:
                plot_text = str(plot_raw)
            return {"plot": " ".join(plot_text.split()), "genres": ", ".join(genres), "year": str(year)}
        except Exception as e:
            self.log(f"Abruf-Fehler: {e}", True)
            return {"plot": "Fehler", "genres": "N/A", "year": "N/A"}

    # Analysiert technische Streams mit ffprobe
    def analyze_video(self, file_path):
        self.log("Analysiere Video...")
        try:
            cmd = [self.ffprobe_path, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams",
                   file_path]
            data = json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)
            v = next(s for s in data['streams'] if s['codec_type'] == 'video')
            dur = float(data['format'].get('duration', 1))
            bit = int((os.path.getsize(file_path) * 8) / dur / 1000)
            codec = v.get('codec_name', 'UNK').upper()
            if codec == "H264": codec = "AVC"
            if v.get("color_transfer") == "smpte2084": codec += " (HDR10)"
            return {
                "res": f"{v.get('width')}x{v.get('height')}", "codec": codec, "bitrate": f"{bit} kb/s",
                "runtime": f"{int(dur // 3600):02d}:{int((dur % 3600) // 60):02d}:{int(dur % 60):02d}",
                "audio": [s for s in data['streams'] if s['codec_type'] == 'audio'],
                "subs": [s for s in data['streams'] if s['codec_type'] == 'subtitle']
            }
        except:
            return None

    # Hauptfunktion zur NFO-Erstellung und Cover-Download
    def start_process(self):
        if not self.selected_file or not self.entry_imdb.get(): return
        tech = self.analyze_video(self.selected_file)
        if not tech: return
        info = self.get_detailed_info(self.entry_imdb.get())
        data_map = {
            "title": self.entry_title.get(), "year": info["year"],
            "imdb": f"imdb.com/title/{self.entry_imdb.get()}", "genre": info["genres"],
            "plot": info["plot"], "format": f"{tech['codec']} @ MKV",
            "video": f"{tech['res']} @ {tech['bitrate']}", "runtime": tech["runtime"]
        }
        nfo_final = []
        for field in self.settings["fields"]:
            f_id = field["id"]
            if f_id in self.field_widgets and self.field_widgets[f_id]["check"].get():
                if f_id == "format": nfo_final.append("")
                label = self.field_widgets[f_id]["entry"].get()
                if f_id == "plot":
                    plot_lines = textwrap.wrap(f"{label}  {data_map['plot']}", width=90, subsequent_indent=" " * 20)
                    nfo_final.extend(plot_lines)
                    nfo_final.append("")
                elif f_id == "audio":
                    for a in tech['audio']:
                        lang = a.get('tags', {}).get('language', '').upper()
                        lang = f"{lang} " if lang and lang != "UND" else ""
                        ch_m = {"6": "5.1", "2": "2.0", "8": "7.1"}
                        nfo_final.append(
                            f"{label}  {lang}{a.get('codec_name', '').upper()} {ch_m.get(str(a.get('channels')), '2.0')}")
                elif f_id == "subs":
                    for s in tech['subs']:
                        lang = s.get('tags', {}).get('language', '').upper()
                        if lang and lang != "UND": nfo_final.append(f"{label}  {lang} Full")
                else:
                    nfo_final.append(f"{label}  {str(data_map.get(f_id, 'N/A'))}")
        path = os.path.splitext(self.selected_file)[0] + ".nfo"
        try:
            with open(path, "w", encoding="cp437", errors="replace") as f:
                f.write("\n".join(nfo_final))
            self.log("NFO gespeichert.")
            messagebox.showinfo("Erfolg", "NFO wurde erfolgreich erstellt!")
        except Exception as e:
            self.log(f"Fehler: {e}", True)
        if self.cover_var.get() and self.poster_url:
            try:
                img_data = requests.get(self.poster_url).content
                with open(os.path.join(os.path.dirname(self.selected_file), "cover.jpg"), 'wb') as h:
                    h.write(img_data)
                self.log("Cover gespeichert.")
            except:
                pass


if __name__ == "__main__":
    app = NFOCreator()
    app.mainloop()