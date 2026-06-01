import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import json
import os
import sys
import textwrap
import requests
import re
from PIL import Image


def resource_path(relative_path):
    """
    Sorgt dafür, dass Pfade zu Dateien (Icons, ffprobe) sowohl im
    Skript-Modus als auch in der fertigen .exe (PyInstaller) funktionieren.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class NFOCreator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. INITIALISIERUNG DER ATTRIBUTE ---
        # Alle Variablen werden hier vorab deklariert (wichtig für PyCharm & Stabilität).
        self.settings_file = "settings.json"
        self.settings = {}
        self.is_compact = False
        self.selected_file = ""
        self.poster_url = ""
        self.ffprobe_path = resource_path(os.path.join("bin", "ffprobe.exe"))

        # UI-Platzhalter für die Hauptseite
        self.label_file_path = None
        self.entry_title = None
        self.entry_imdb = None
        self.imdb_frame = None
        self.cover_var = None
        self.selection_container = None
        self.log_box = None

        # UI-Platzhalter für Einstellungen
        self.entry_api_key = None
        self.settings_center_frame = None
        self.settings_scroll_container = None
        self.preview_label = None
        self.preview_box = None
        self.field_widgets = {}

        # UI-Platzhalter für Beitrags-Tab
        self.entry_img_link = None
        self.entry_dl_links = None
        self.post_preview_label = None
        self.post_preview_box = None
        self.hoster_vars = {}

        # Branding / Logos
        self.ctk_logo_big = None
        self.logo_label_img = None
        self.ctk_logo_small = None
        self.logo_label_small = None
        self.logo_label_text = None

        # --- 2. GRUNDKONFIGURATION ---
        self.title("DataLoad NFO Creator v2.0 - by Dwarfpicker")
        self.settings = self.load_settings()

        # Check: Falls kein TMDb Key in den Settings steht, sofort fragen
        if not self.settings.get("tmdb_api_key"):
            self.ask_for_api_key()

        # Fenstergrößen für Normal- und Mini-Modus
        self.width_full = 750
        self.height_full = 920
        self.width_mini = 450
        self.height_mini = 650
        self.is_compact = bool(self.settings.get("compact_mode", False))

        # TMDb Genre-ID Übersetzungstabelle
        self.g_map = {
            28: "Action", 12: "Abenteuer", 16: "Animation", 35: "Komödie", 80: "Krimi",
            99: "Doku", 18: "Drama", 10751: "Familie", 14: "Fantasy", 36: "Historie",
            27: "Horror", 10402: "Musik", 9648: "Mystery", 10749: "Liebesfilm",
            878: "Science Fiction", 10770: "TV-Film", 53: "Thriller", 10752: "Kriegsfilm",
            37: "Western", 10759: "Action & Adventure", 10762: "Kids", 10763: "News",
            10764: "Reality", 10765: "Sci-Fi & Fantasy", 10766: "Soap", 10767: "Talk", 10768: "War & Politics"
        }

        # App-Icon setzen
        try:
            self.iconbitmap(resource_path("app_icon.ico"))
        except Exception:
            pass

        # Daten für die BBCode-Generierung
        self.post_data = {
            "title": "",
            "year": "",
            "plot": "",
            "file_size": "",
            "nfo_content_no_plot": ""
        }

        # Farben und Styling
        self.bg_color = "#1f2530"
        self.tab_color_active = "#1f2530"
        self.tab_color_inactive = "#161b22"
        self.border_color = "white"
        self.default_border = ["#979da2", "#565b5e"]

        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=self.bg_color)

        # --- 3. UI-AUFBAU ---
        # Oberer Header mit dem Größen-Umschalter
        self.top_header = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self.top_header.pack(fill="x", padx=10, pady=5)

        self.btn_resize = ctk.CTkButton(
            self.top_header, text="1/2", width=30, height=20,
            fg_color=self.tab_color_inactive, border_width=1, border_color="white",
            font=("Arial", 10, "bold"), text_color="white", command=self.toggle_window_size
        )
        self.btn_resize.pack(side="right")

        # Haupt-Inhaltsbereich
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Logo-Frame
        self.logo_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.logo_frame.pack(fill="x", pady=(0, 5))
        self.load_branding_assets()

        # Tab-Navigations-Leiste
        self.tab_frame = ctk.CTkFrame(self.main_container, fg_color="transparent", height=45)
        self.tab_frame.pack(fill="x", pady=(10, 0))
        self.tab_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="group1")

        self.btn_tab_main = ctk.CTkButton(
            self.tab_frame, text="Hauptseite", command=lambda: self.switch_tab("main"),
            corner_radius=10, border_width=2, height=45, font=("Arial", 12, "bold")
        )
        self.btn_tab_main.grid(row=0, column=0, sticky="nsew", padx=(0, 2))

        self.btn_tab_settings = ctk.CTkButton(
            self.tab_frame, text="Einstellungen", command=lambda: self.switch_tab("settings"),
            corner_radius=10, border_width=2, height=45, font=("Arial", 12, "bold")
        )
        self.btn_tab_settings.grid(row=0, column=1, sticky="nsew", padx=2)

        self.btn_tab_post = ctk.CTkButton(
            self.tab_frame, text="Beitrag Erstellen", command=lambda: self.switch_tab("post"),
            corner_radius=10, border_width=2, height=45, font=("Arial", 12, "bold"), state="disabled"
        )
        self.btn_tab_post.grid(row=0, column=2, sticky="nsew", padx=(2, 0))

        # Rahmen um den eigentlichen Inhalt
        self.folder_body = ctk.CTkFrame(
            self.main_container, fg_color=self.bg_color, corner_radius=15,
            border_width=2, border_color=self.border_color
        )
        self.folder_body.pack(fill="both", expand=True, pady=(0, 10))

        # Frames für die verschiedenen Seiten
        self.page_main = ctk.CTkFrame(self.folder_body, fg_color="transparent")
        self.page_settings = ctk.CTkFrame(self.folder_body, fg_color="transparent")
        self.page_post = ctk.CTkFrame(self.folder_body, fg_color="transparent")

        # UI-Inhalte initialisieren
        self.setup_main_page()
        self.setup_settings_page()
        self.setup_post_page()
        self.apply_stored_size()
        self.switch_tab("main")

        # Beim Schließen-Button (X) speichern
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # =========================================================================
    # KONFIGURATION & PERSISTENZ
    # =========================================================================

    def ask_for_api_key(self):
        """ Öffnet einen Dialog zur Eingabe des TMDb API-Keys. """
        key = simpledialog.askstring("TMDb API Key", "Bitte gib deinen TMDb API Key ein:", parent=self)
        if key:
            self.settings["tmdb_api_key"] = key.strip()

    def load_settings(self):
        """ Lädt die settings.json oder erstellt sie mit Standardwerten. """
        df = [
            {"id": "title", "name": "Titel", "label": "Title............:", "enabled": True,
             "placeholder": "$Filmtitel"},
            {"id": "year", "name": "Year", "label": "Year.............:", "enabled": True, "placeholder": "$Jahr"},
            {"id": "imdb", "name": "IMDB", "label": "IMDb.............:", "enabled": True, "placeholder": "$IMDB_Link"},
            {"id": "genre", "name": "Genre", "label": "Genre............:", "enabled": True, "placeholder": "$Genre"},
            {"id": "plot", "name": "Plot", "label": "Plot.............:", "enabled": True, "placeholder": "$Plot"},
            {"id": "format", "name": "Format", "label": "Format...........:", "enabled": True,
             "placeholder": "$Video_Format"},
            {"id": "video", "name": "Video", "label": "Video............:", "enabled": True,
             "placeholder": "$Video_Auflösung"},
            {"id": "audio", "name": "Audio", "label": "Audio............:", "enabled": True,
             "placeholder": "$Audiospur"},
            {"id": "subs", "name": "Subtitle", "label": "Subtitles........:", "enabled": True,
             "placeholder": "$Untertitel"},
            {"id": "runtime", "name": "Runtime", "label": "Runtime..........:", "enabled": True,
             "placeholder": "$Laufzeit"}
        ]
        s = {"fields": df, "tmdb_api_key": "", "compact_mode": False, "cover": True}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    ld = json.load(f)
                    if not ld.get("fields"):
                        ld["fields"] = df
                    return ld
            except Exception:
                pass
        return s

    def on_closing(self):
        """ Speichert alle aktuellen UI-Zustände in die JSON-Datei. """
        self.settings["tmdb_api_key"] = self.entry_api_key.get().strip()
        self.settings["compact_mode"] = self.is_compact
        self.settings["cover"] = self.cover_var.get()
        # NFO Felder erfassen
        for item in self.settings.get("fields", []):
            f_id = item["id"]
            if f_id in self.field_widgets:
                item["label"] = self.field_widgets[f_id]["entry"].get()
                item["enabled"] = self.field_widgets[f_id]["check"].get()

        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f, indent=4)
        self.destroy()

    # =========================================================================
    # UI: BRANDING & KONTEXTMENÜ
    # =========================================================================

    def load_branding_assets(self):
        """ Lädt die Logo-Grafiken für die Kopfzeile. """
        try:
            img_b = Image.open(resource_path("logo.png"))
            self.ctk_logo_big = ctk.CTkImage(light_image=img_b, dark_image=img_b, size=(400, 185))
            self.logo_label_img = ctk.CTkLabel(self.logo_frame, image=self.ctk_logo_big, text="")
        except Exception:
            self.logo_label_img = ctk.CTkLabel(self.logo_frame, text="DataLoad NFO Creator", font=("Arial", 22, "bold"))

        try:
            img_s = Image.open(resource_path("logo_small.png"))
            self.ctk_logo_small = ctk.CTkImage(light_image=img_s, dark_image=img_s, size=(225, 30))
            self.logo_label_small = ctk.CTkLabel(self.logo_frame, image=self.ctk_logo_small, text="")
        except Exception:
            self.logo_label_small = None

        self.logo_label_text = ctk.CTkLabel(self.logo_frame, text="DataLoad NFO Creator", font=("Arial", 16, "bold"),
                                            text_color="white")

    def add_context_menu(self, widget):
        """ Fügt Kopieren/Einfügen per Rechtsklick zu Eingabefeldern hinzu. """
        menu = tk.Menu(widget, tearoff=0, bg="#161b22", fg="white", activebackground="#2ecc71")

        def do_cut():
            do_copy()
            try:
                widget.delete("sel.first", "sel.last")
            except Exception:
                pass

        def do_copy():
            try:
                if isinstance(widget, ctk.CTkTextbox):
                    sel = widget.get("sel.first", "sel.last")
                else:
                    sel = widget.get_selection()
                self.clipboard_clear()
                self.clipboard_append(sel)
            except Exception:
                pass

        def do_paste():
            try:
                txt = self.clipboard_get()
                widget.insert("insert", txt)
            except Exception:
                pass

        menu.add_command(label="Ausschneiden", command=do_cut)
        menu.add_command(label="Kopieren", command=do_copy)
        menu.add_command(label="Einfügen", command=do_paste)
        menu.add_separator()
        menu.add_command(label="Alles auswählen",
                         command=lambda: widget.select_range(0, 'end') if not isinstance(widget,
                                                                                         ctk.CTkTextbox) else widget.tag_add(
                             "sel", "1.0", "end"))

        def show_menu(event):
            widget.focus_set()
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)

    # =========================================================================
    # TAB 1: HAUPTSEITE
    # =========================================================================

    def setup_main_page(self):
        """ Aufbau der ersten Seite: Datei wählen und TMDb-Suche. """
        ctk.CTkButton(self.page_main, text="1. Video Datei auswählen", command=self.select_file, height=35).pack(
            pady=(10, 5))

        self.label_file_path = ctk.CTkLabel(self.page_main, text="Keine Datei ausgewählt", font=("Arial", 10, "italic"))
        self.label_file_path.pack()

        ctk.CTkLabel(self.page_main, text="Filmtitel für die Suche:", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        self.entry_title = ctk.CTkEntry(self.page_main, width=400)
        self.entry_title.pack(pady=5)
        self.add_context_menu(self.entry_title)

        self.imdb_frame = ctk.CTkFrame(self.page_main, fg_color="transparent")
        self.imdb_frame.pack(pady=10)

        self.entry_imdb = ctk.CTkEntry(self.imdb_frame, width=150, placeholder_text="IMDb ID (tt...)")
        self.entry_imdb.pack(side="left", padx=5)
        self.add_context_menu(self.entry_imdb)

        ctk.CTkButton(self.imdb_frame, text="2. Suchen", width=120, command=self.search_tmdb).pack(side="left")

        self.cover_var = ctk.BooleanVar(value=self.settings.get("cover", True))
        ctk.CTkCheckBox(self.page_main, text="Cover herunterladen", variable=self.cover_var).pack(pady=5)

        # Auswahlbereich für Mehrfachtreffer
        self.selection_container = ctk.CTkScrollableFrame(self.page_main, width=500, height=150, fg_color="#161b22",
                                                          border_width=1, border_color="white")

        # Logfenster für Meldungen
        self.log_box = ctk.CTkTextbox(self.page_main, width=600, height=200, font=("Consolas", 11), fg_color="#161b22")
        self.log_box.pack(fill="both", expand=True, pady=10)

        ctk.CTkButton(self.page_main, text="3. NFO Erstellen", fg_color="#2ecc71", hover_color="#27ae60",
                      command=self.start_process, height=45, font=("Arial", 14, "bold")).pack(pady=(0, 10))

    # =========================================================================
    # TAB 2: EINSTELLUNGEN
    # =========================================================================

    def setup_settings_page(self):
        """ Aufbau der Einstellungsseite mit zentriertem Feld-Block. """
        self.settings_center_frame = ctk.CTkFrame(self.page_settings, fg_color="transparent")
        self.settings_center_frame.pack(expand=True)

        api_row = ctk.CTkFrame(self.settings_center_frame, fg_color="transparent")
        api_row.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(api_row, text="TMDb API Key:", font=("Arial", 12, "bold")).pack(side="left", padx=10)

        self.entry_api_key = ctk.CTkEntry(api_row, width=400, show="*")
        self.entry_api_key.insert(0, str(self.settings.get("tmdb_api_key", "")))
        self.entry_api_key.pack(side="left", padx=10)
        self.add_context_menu(self.entry_api_key)

        # Container für die NFO-Felder (Ohne Scrollen für sauberen Look)
        self.settings_scroll_container = ctk.CTkFrame(self.settings_center_frame, fg_color="transparent", width=600,
                                                      height=320)
        self.settings_scroll_container.pack(pady=5)

        for field in self.settings.get("fields", []):
            row = ctk.CTkFrame(self.settings_scroll_container, fg_color="transparent")
            row.pack(fill="x", pady=2)

            var = ctk.BooleanVar(value=field.get("enabled", True))
            cb = ctk.CTkCheckBox(row, text="", variable=var, width=20, command=self.update_preview)
            cb.pack(side="left")

            ent = ctk.CTkEntry(row, width=220)
            ent.insert(0, field.get("label", ""))
            ent.pack(side="left", padx=10)
            ent.bind("<KeyRelease>", lambda e: self.update_preview())
            self.add_context_menu(ent)

            ctk.CTkLabel(row, text=field.get("placeholder", ""), text_color="gray", font=("Arial", 10)).pack(
                side="left")

            self.field_widgets[field["id"]] = {"check": var, "entry": ent}

        # NFO Live-Vorschau
        self.preview_label = ctk.CTkLabel(self.page_settings, text="Vorschau der NFO (Beispiel):",
                                          font=("Arial", 11, "bold"))
        self.preview_label.pack(pady=(10, 0))

        self.preview_box = ctk.CTkTextbox(self.page_settings, width=650, height=250, font=("Consolas", 11),
                                          fg_color="#161b22")
        self.preview_box.pack(fill="both", expand=True, pady=5)

    # =========================================================================
    # TAB 3: POST GENERATOR
    # =========================================================================

    def setup_post_page(self):
        """ Interface zur Erstellung von Foren-Posts (BBCode). """
        cont = ctk.CTkFrame(self.page_post, fg_color="transparent")
        cont.pack(pady=5, fill="x")

        ctk.CTkLabel(cont, text="Bild-Link:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
        self.entry_img_link = ctk.CTkEntry(cont, width=600)
        self.entry_img_link.pack(pady=(0, 5), padx=20)
        self.add_context_menu(self.entry_img_link)

        ctk.CTkLabel(cont, text="Download-Links:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
        self.entry_dl_links = ctk.CTkTextbox(cont, width=600, height=80, fg_color="#161b22", border_width=1,
                                             border_color="#565b5e")
        self.entry_dl_links.pack(pady=(0, 5), padx=20)
        self.add_context_menu(self.entry_dl_links)

        ctk.CTkLabel(cont, text="Hoster:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
        h_f = ctk.CTkFrame(cont, fg_color="transparent")
        h_f.pack(pady=5)

        h_list = ["Rapidgator", "DDownload", "1Fichier", "Turbobit.net", "KatFile.com", "Nitroflare.com"]
        for i, hn in enumerate(h_list):
            self.hoster_vars[hn] = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(h_f, text=hn, variable=self.hoster_vars[hn], font=("Arial", 10))
            cb.grid(row=i // 3, column=i % 3, padx=10, pady=5, sticky="w")

        ctk.CTkButton(self.page_post, text="Post erstellen & kopieren", fg_color="#3498db", hover_color="#2980b9",
                      command=self.generate_bbcode, height=40, font=("Arial", 13, "bold")).pack(pady=5)

        self.post_preview_label = ctk.CTkLabel(self.page_post, text="Fertiger BBCode:", font=("Arial", 11, "bold"))
        self.post_preview_label.pack(pady=(5, 0))

        self.post_preview_box = ctk.CTkTextbox(self.page_post, width=650, font=("Consolas", 11), fg_color="#161b22")
        self.post_preview_box.pack(fill="both", expand=True, pady=10)
        self.add_context_menu(self.post_preview_box)

    def generate_bbcode(self):
        """ Baut den BBCode-String zusammen und kopiert ihn. """
        t_f = f"{self.post_data['title']} ({self.post_data['year']})"
        hl = [n for n, v in self.hoster_vars.items() if v.get()]
        code = (
            f"[CENTER]\n{t_f}\n\n[img]{self.entry_img_link.get()}[/img]\n\nPlot:\n{self.post_data['plot']}\n\nSize:\n{self.post_data['file_size']}\n\n[SPOILER=\"NFO\"]\n{self.post_data['nfo_content_no_plot']}\n[/SPOILER]\n\nHoster:\n{', '.join(hl)}\n\nDownload:\n[CODE]\n{self.entry_dl_links.get('1.0', 'end-1c').strip()}\n[/CODE]\n[/CENTER]")
        self.post_preview_box.delete("1.0", "end")
        self.post_preview_box.insert("1.0", code)
        self.clipboard_clear()
        self.clipboard_append(code)
        messagebox.showinfo("Erfolg", "BBCode kopiert!")

    # =========================================================================
    # LOGIK: SUCHE & VIDEOANALYSE
    # =========================================================================

    def search_tmdb(self):
        """ Sucht via TMDb API nach dem Titel. """
        q = self.entry_title.get().strip()
        k = self.entry_api_key.get().strip()
        if not q or not k:
            self.log("Titel oder API Key fehlt.", True)
            return
        try:
            url = f"https://api.themoviedb.org/3/search/multi?api_key={k}&query={q}&language=de-DE"
            res = requests.get(url, timeout=5).json()
            its = [r for r in res.get("results", []) if r.get("media_type") in ["movie", "tv"]]
            if its:
                if len(its) > 1:
                    self.show_inline_selection(its)
                else:
                    self.finalize_tmdb_selection(its[0])
            else:
                self.log("Nichts gefunden.", True)
                self.entry_imdb.configure(border_color="#e74c3c")
        except Exception as e:
            self.log(f"Fehler: {e}", True)

    def show_inline_selection(self, results):
        """ Zeigt Knöpfe zur Auswahl an, wenn TMDb mehrere Treffer liefert. """
        for w in self.selection_container.winfo_children():
            w.destroy()
        self.log("Mehrere Treffer gefunden. Bitte auswählen...")
        for m in results[:10]:
            ti = m.get("title") or m.get("name")
            da = m.get("release_date") or m.get("first_air_date")
            yr = str(da)[:4] if da else "...."
            ic = "🎬" if m["media_type"] == "movie" else "📺"
            btn = ctk.CTkButton(self.selection_container, text=f"{ic} | {ti} ({yr})", anchor="w", fg_color="#1f2530",
                                hover_color="#2ecc71", command=lambda r=m: self.finalize_tmdb_selection(r))
            btn.pack(fill="x", pady=2, padx=5)
        self.selection_container.pack(after=self.imdb_frame, pady=5)

    def finalize_tmdb_selection(self, movie_data):
        """ Übernimmt die IMDb-ID eines ausgewählten Films/Serie. """
        self.selection_container.pack_forget()
        k = self.entry_api_key.get().strip()
        try:
            u = f"https://api.themoviedb.org/3/{movie_data['media_type']}/{movie_data['id']}/external_ids?api_key={k}"
            ex = requests.get(u, timeout=5).json()
            self.entry_imdb.delete(0, "end")
            self.entry_imdb.insert(0, ex.get("imdb_id", ""))
            self.entry_imdb.configure(border_color="#2ecc71")
            p = movie_data.get("poster_path")
            if p:
                self.poster_url = f"https://image.tmdb.org/t/p/original{p}"
            self.log(f"Ausgewählt: {movie_data.get('title') or movie_data.get('name')}")
        except Exception as e:
            self.log(f"ID-Fehler: {e}", True)

    def analyze_video(self, fp):
        """ Nutzt ffprobe, um technische Daten (Auflösung, Codec, Streams) zu laden. """
        try:
            c = [self.ffprobe_path, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", fp]
            raw = subprocess.run(c, capture_output=True, text=True).stdout
            d = json.loads(raw)
            v = next(s for s in d['streams'] if s['codec_type'] == 'video')
            dur = float(d['format'].get('duration', 1))
            res = f"{v.get('width')}x{v.get('height')}"
            br = f"{int((os.path.getsize(fp) * 8) / dur / 1000)} kb/s"
            rt = f"{int(dur // 3600):02d}:{int((dur % 3600) // 60):02d}:{int(dur % 60):02d}"
            return {
                "res": res,
                "codec": v.get('codec_name', '').upper(),
                "bitrate": br,
                "runtime": rt,
                "audio": [s for s in d['streams'] if s['codec_type'] == 'audio'],
                "subs": [s for s in d['streams'] if s['codec_type'] == 'subtitle']
            }
        except Exception:
            return None

    def start_process(self):
        """ Fließt alle Daten zusammen, erstellt die NFO-Datei und lädt das Cover. """
        if not self.selected_file or not self.entry_imdb.get():
            return
        tech = self.analyze_video(self.selected_file)
        if not tech:
            return
        k = self.entry_api_key.get().strip()
        u = f"https://api.themoviedb.org/3/find/{self.entry_imdb.get()}?api_key={k}&external_source=imdb_id&language=de-DE"
        res = requests.get(u).json()
        its = res.get("movie_results") or res.get("tv_results")
        if not its:
            return
        m = its[0]
        gs = [self.g_map.get(gid, "Unbekannt") for gid in m.get("genre_ids", [])]
        dt = m.get("release_date") or m.get("first_air_date") or "N/A"
        inf = {"plot": m.get("overview", ""), "genres": ", ".join(gs), "year": str(dt)[:4]}
        f_sz = f"{round(os.path.getsize(self.selected_file) / (1024 * 1024))} MB"

        # Daten für BBCode Generator speichern
        self.post_data.update(
            {"title": self.entry_title.get(), "year": inf["year"], "plot": inf["plot"], "file_size": f_sz})

        # FIX: Hier wurde fälschlicherweise "info" statt "inf" aufgerufen
        dm = {
            "title": self.entry_title.get(),
            "year": inf["year"],
            "imdb": f"imdb.com/title/{self.entry_imdb.get()}",
            "genre": inf["genres"],
            "plot": inf["plot"],
            "format": f"{tech['codec']} @ MKV",
            "video": f"{tech['res']} @ {tech['bitrate']}",
            "runtime": tech["runtime"]
        }

        n_f, n_np = [], []
        for f_c in self.settings.get("fields", []):
            f_id = f_c["id"]
            if f_id not in self.field_widgets or not self.field_widgets[f_id]["check"].get():
                continue
            lbl = self.field_widgets[f_id]["entry"].get()

            # Leerzeile vor dem technischen Block einfügen
            if f_id == "format":
                n_f.append("")
                n_np.append("")

            if f_id == "plot":
                wr = textwrap.wrap(f"{lbl}  {dm['plot']}", width=90, subsequent_indent=" " * 20)
                n_f.extend(wr)
                n_f.append("")
            elif f_id in ["audio", "subs"]:
                str_list = tech['audio'] if f_id == "audio" else tech['subs']
                for s in str_list:
                    lang = s.get('tags', {}).get('language', '').upper()
                    l_s = f"{lang} " if lang and lang != "UND" else ""
                    ln = f"{lbl}  {l_s}{s.get('codec_name', '').upper()} {s.get('channels', '2.0') if f_id == 'audio' else 'Full'}"
                    n_f.append(ln)
                    n_np.append(ln)
            else:
                ln = f"{lbl}  {str(dm.get(f_id, 'N/A'))}"
                n_f.append(ln)
                n_np.append(ln)

        self.post_data["nfo_content_no_plot"] = "\n".join(n_np)
        p_nfo = os.path.splitext(self.selected_file)[0] + ".nfo"
        with open(p_nfo, "w", encoding="cp437", errors="replace") as f:
            f.write("\n".join(n_f))

        if self.cover_var.get() and self.poster_url:
            try:
                img = requests.get(self.poster_url).content
                p_cov = os.path.join(os.path.dirname(self.selected_file), "cover.jpg")
                with open(p_cov, 'wb') as f:
                    f.write(img)
            except Exception:
                pass

        self.btn_tab_post.configure(state="normal")
        messagebox.showinfo("Erfolg", "NFO erstellt!")

    # =========================================================================
    # HILFSFUNKTIONEN
    # =========================================================================

    def select_file(self):
        """ Öffnet den Dateidialog und bereinigt den Titel für die Suche. """
        fn = filedialog.askopenfilename(filetypes=[("Video files", "*.mkv *.mp4 *.avi")])
        if fn:
            self.selected_file = fn
            self.label_file_path.configure(text=fn)
            bn = os.path.basename(fn).rsplit('.', 1)[0].replace(".", " ")
            tgs = ["2160p", "1080p", "720p", "480p", "576p", "UHD", "BluRay", "BDRip", "WebDL", "Webrip", "4K", "HEVC",
                   "x265", "x264", "German", "English", "DL"]
            for t in tgs:
                bn = re.sub(rf"\b{t}\b", "", bn, flags=re.IGNORECASE)
            self.entry_title.delete(0, "end")
            self.entry_title.insert(0, " ".join(bn.split()).strip())
            self.btn_tab_post.configure(state="disabled")
            self.switch_tab("main")

    def update_preview(self):
        """ Aktualisiert die NFO-Vorschau im Einstellungs-Tab. """
        ls = []
        for f in self.settings.get("fields", []):
            f_id = f["id"]
            if f_id in self.field_widgets and self.field_widgets[f_id]["check"].get():
                if f_id == "format":
                    ls.append("")
                ls.append(f"{self.field_widgets[f_id]['entry'].get()}  {f['placeholder']}")
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("1.0", "\n".join(ls))

    def apply_stored_size(self):
        """ Setzt die Fenstergröße beim Starten. """
        if self.is_compact:
            self.is_compact = False
            self.toggle_window_size()
        else:
            self.geometry(f"{self.width_full}x{self.height_full}")
            self.minsize(650, 800)
            self.logo_label_img.pack()

    def toggle_window_size(self):
        """ Schaltet zwischen Normal- und Kompaktmodus um. """
        if not self.is_compact:
            self.minsize(300, 400)
            self.geometry(f"{self.width_mini}x{self.height_mini}")
            self.btn_resize.configure(text="1/1")
            self.is_compact = True
            self.btn_tab_main.configure(text="🏠")
            self.btn_tab_settings.configure(text="⚙️")
            self.btn_tab_post.configure(text="📝")
            self.logo_label_img.pack_forget()
            if self.logo_label_small:
                self.logo_label_small.pack(pady=5)
            self.log_box.configure(height=70)
            self.preview_label.pack_forget()
            self.preview_box.pack_forget()
        else:
            self.geometry(f"{self.width_full}x{self.height_full}")
            self.minsize(650, 800)
            self.btn_resize.configure(text="1/2")
            self.is_compact = False
            self.btn_tab_main.configure(text="Hauptseite")
            self.btn_tab_settings.configure(text="Einstellungen")
            self.btn_tab_post.configure(text="Beitrag Erstellen")
            self.logo_label_img.pack()
            self.log_box.configure(height=200)
            self.preview_label.pack(pady=(10, 0))
            self.preview_box.pack(fill="both", expand=True, pady=5)

    def switch_tab(self, tab_name):
        """ Schaltet zwischen den drei Funktions-Tabs um. """
        pm = {"main": (self.page_main, self.btn_tab_main), "settings": (self.page_settings, self.btn_tab_settings),
              "post": (self.page_post, self.btn_tab_post)}
        for n, (p, b) in pm.items():
            if n == tab_name:
                p.pack(fill="both", expand=True, padx=10, pady=10)
                b.configure(fg_color=self.tab_color_active, border_color="white", text_color="white")
            else:
                p.pack_forget()
                b.configure(fg_color=self.tab_color_inactive, border_color=self.tab_color_inactive, text_color="gray")
        if tab_name == "settings":
            self.update_preview()

    def log(self, text, is_error=False):
        """ Gibt Nachrichten im Log-Fenster aus. """
        px = '❌ ' if is_error else 'ℹ️ '
        self.log_box.insert("end", f"{px}{text}\n")
        self.log_box.see("end")
        self.update()


if __name__ == "__main__":
    NFOCreator().mainloop()