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
        self.title("DataLoad NFO Creator v1.5 - by Dwarfpicker")

        # Icon für Fenster und Taskleiste setzen
        try:
            self.iconbitmap(resource_path("app_icon.ico"))
        except Exception:
            pass

        # Definierte Fenster-Maße
        self.width_full, self.height_full = 750, 920
        self.width_mini, self.height_mini = 400, 600

        # Standard-Felder
        self.default_fields = [
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

        self.settings_file = "settings.json"
        self.settings = self.load_settings()
        self.is_compact = self.settings.get("compact_mode", False)

        # Zwischenspeicher für die Post-Generierung
        self.post_data = {
            "title": "", "year": "", "plot": "", "file_size": "", "nfo_content_no_plot": ""
        }

        # Farben und Styling
        self.bg_color = "#1f2530"
        self.tab_color_active = "#1f2530"
        self.tab_color_inactive = "#161b22"
        self.border_color = "white"
        self.default_border = ["#979da2", "#565b5e"]  # Standard CTK Farben

        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=self.bg_color)

        self.selected_file = ""
        self.poster_url = ""
        self.ffprobe_path = resource_path(os.path.join("bin", "ffprobe.exe"))

        # --- UI STRUKTUR ---
        self.top_header = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self.top_header.pack(fill="x", padx=10, pady=5)

        self.btn_resize = ctk.CTkButton(self.top_header, text="1/2", width=30, height=20,
                                        fg_color=self.tab_color_inactive, border_width=1, border_color="white",
                                        font=("Arial", 10, "bold"), text_color="white",
                                        command=self.toggle_window_size)
        self.btn_resize.pack(side="right")

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Logo-Bereich
        self.logo_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.logo_frame.pack(fill="x", pady=(0, 5))
        self.load_branding_assets()

        # Tabs (Grid für absolute Symmetrie)
        self.tab_frame = ctk.CTkFrame(self.main_container, fg_color="transparent", height=45)
        self.tab_frame.pack(fill="x", pady=(10, 0))
        self.tab_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="group1")

        self.btn_tab_main = ctk.CTkButton(self.tab_frame, text="Hauptseite", command=lambda: self.switch_tab("main"),
                                          corner_radius=10, border_width=2, height=45, font=("Arial", 12, "bold"))
        self.btn_tab_main.grid(row=0, column=0, sticky="nsew", padx=(0, 2))

        self.btn_tab_settings = ctk.CTkButton(self.tab_frame, text="Einstellungen",
                                              command=lambda: self.switch_tab("settings"),
                                              corner_radius=10, border_width=2, height=45, font=("Arial", 12, "bold"))
        self.btn_tab_settings.grid(row=0, column=1, sticky="nsew", padx=2)

        self.btn_tab_post = ctk.CTkButton(self.tab_frame, text="Beitrag Erstellen",
                                          command=lambda: self.switch_tab("post"),
                                          corner_radius=10, border_width=2, height=45, font=("Arial", 12, "bold"),
                                          state="disabled")
        self.btn_tab_post.grid(row=0, column=2, sticky="nsew", padx=(2, 0))

        # Inhaltsbereich
        self.folder_body = ctk.CTkFrame(self.main_container, fg_color=self.bg_color, corner_radius=15,
                                        border_width=2, border_color=self.border_color)
        self.folder_body.pack(fill="both", expand=True, pady=(0, 10))

        self.page_main = ctk.CTkFrame(self.folder_body, fg_color="transparent")
        self.page_settings = ctk.CTkFrame(self.folder_body, fg_color="transparent")
        self.page_post = ctk.CTkFrame(self.folder_body, fg_color="transparent")

        self.field_widgets = {}
        self.setup_main_page()
        self.setup_settings_page()
        self.setup_post_page()

        self.apply_stored_size()
        self.switch_tab("main")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Lädt die Logo-Dateien
    def load_branding_assets(self):
        try:
            img_big = Image.open(resource_path("logo.png"))
            self.ctk_logo_big = ctk.CTkImage(light_image=img_big, dark_image=img_big, size=(400, 185))
            self.logo_label_img = ctk.CTkLabel(self.logo_frame, image=self.ctk_logo_big, text="")
        except Exception:
            self.logo_label_img = ctk.CTkLabel(self.logo_frame, text="DataLoad NFO Creator", font=("Arial", 22, "bold"))

        try:
            img_small = Image.open(resource_path("logo_small.png"))
            self.ctk_logo_small = ctk.CTkImage(light_image=img_small, dark_image=img_small, size=(225, 30))
            self.logo_label_small = ctk.CTkLabel(self.logo_frame, image=self.ctk_logo_small, text="")
        except Exception:
            self.logo_label_small = None

        self.logo_label_text = ctk.CTkLabel(self.logo_frame, text="DataLoad NFO Creator", font=("Arial", 16, "bold"),
                                            text_color="white")

    # Manuelle Clipboard-Verarbeitung
    def add_context_menu(self, widget):
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
                    selected_text = widget.get("sel.first", "sel.last")
                else:
                    selected_text = widget._entry.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
            except Exception:
                pass

        def do_paste():
            try:
                text = self.clipboard_get()
                if isinstance(widget, ctk.CTkTextbox):
                    try:
                        widget.delete("sel.first", "sel.last")
                    except:
                        pass
                    widget.insert("insert", text)
                else:
                    if widget.select_present(): widget.delete("sel.first", "sel.last")
                    widget.insert("insert", text)
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

    # Initialisiert die Fenstergröße
    def apply_stored_size(self):
        if self.is_compact:
            self.is_compact = False
            self.toggle_window_size()
        else:
            self.geometry(f"{self.width_full}x{self.height_full}")
            self.minsize(650, 800)
            self.logo_label_img.pack()

    # Layout-Wechsel (1/1 zu 1/2)
    def toggle_window_size(self):
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
            else:
                self.logo_label_text.pack(pady=10)
            self.log_box.configure(height=70)
            self.preview_label.pack_forget()
            self.preview_box.pack_forget()
            self.post_preview_label.pack_forget()
            self.post_preview_box.pack_forget()
        else:
            self.geometry(f"{self.width_full}x{self.height_full}")
            self.minsize(650, 800)
            self.btn_resize.configure(text="1/2")
            self.is_compact = False
            self.btn_tab_main.configure(text="Hauptseite")
            self.btn_tab_settings.configure(text="Einstellungen")
            self.btn_tab_post.configure(text="Beitrag Erstellen")
            if self.logo_label_small: self.logo_label_small.pack_forget()
            self.logo_label_text.pack_forget()
            self.logo_label_img.pack()
            self.log_box.configure(height=200)
            self.preview_label.pack(pady=(15, 0))
            self.preview_box.pack(fill="both", expand=True, pady=10)
            self.post_preview_label.pack(pady=(15, 0))
            self.post_preview_box.pack(fill="both", expand=True, pady=10)

    # Tab-Steuerung
    def switch_tab(self, tab_name):
        pages = {"main": (self.page_main, self.btn_tab_main),
                 "settings": (self.page_settings, self.btn_tab_settings),
                 "post": (self.page_post, self.btn_tab_post)}
        for name, (page, btn) in pages.items():
            if name == tab_name:
                page.pack(fill="both", expand=True, padx=10, pady=10)
                btn.configure(fg_color=self.tab_color_active, border_color=self.border_color, text_color="white")
            else:
                page.pack_forget()
                btn.configure(fg_color=self.tab_color_inactive, border_color=self.tab_color_inactive, text_color="gray")
        if tab_name == "settings": self.update_preview()

    # Aufbau Hauptseite
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

    # Aufbau Einstellungen
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

    # Aufbau Post-Generator
    def setup_post_page(self):
        input_container = ctk.CTkFrame(self.page_post, fg_color="transparent")
        input_container.pack(pady=10, fill="x")
        ctk.CTkLabel(input_container, text="Bild-Link:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
        self.entry_img_link = ctk.CTkEntry(input_container, width=600)
        self.entry_img_link.pack(pady=(0, 10), padx=20)
        self.add_context_menu(self.entry_img_link)
        ctk.CTkLabel(input_container, text="Download-Links (Einer pro Zeile):", font=("Arial", 11, "bold")).pack(
            anchor="w", padx=20)
        self.entry_dl_links = ctk.CTkTextbox(input_container, width=600, height=80, fg_color="#161b22", border_width=1,
                                             border_color="#565b5e")
        self.entry_dl_links.pack(pady=(0, 10), padx=20)
        self.add_context_menu(self.entry_dl_links)
        ctk.CTkLabel(input_container, text="Hoster:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20)
        hoster_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        hoster_frame.pack(pady=5)
        self.hoster_vars = {
            "Rapidgator": ctk.BooleanVar(), "DDownload": ctk.BooleanVar(), "1Fichier": ctk.BooleanVar(),
            "Turbobit.net": ctk.BooleanVar(), "KatFile.com": ctk.BooleanVar(), "Nitroflare.com": ctk.BooleanVar()
        }
        for i, (name, var) in enumerate(self.hoster_vars.items()):
            cb = ctk.CTkCheckBox(hoster_frame, text=name, variable=var, font=("Arial", 10))
            cb.grid(row=i // 3, column=i % 3, padx=15, pady=5, sticky="w")
        ctk.CTkButton(self.page_post, text="Post erstellen & kopieren", fg_color="#3498db", hover_color="#2980b9",
                      command=self.generate_bbcode, height=40, font=("Arial", 13, "bold")).pack(pady=10)
        self.post_preview_label = ctk.CTkLabel(self.page_post, text="Fertiger BBCode:", font=("Arial", 11, "bold"))
        self.post_preview_label.pack(pady=(5, 0))
        self.post_preview_box = ctk.CTkTextbox(self.page_post, width=650, font=("Consolas", 11), fg_color="#161b22")
        self.post_preview_box.pack(fill="both", expand=True, pady=10)
        self.add_context_menu(self.post_preview_box)

    # Generiert BBCode
    def generate_bbcode(self):
        titel_full = f"{self.post_data['title']} ({self.post_data['year']})"
        img_bb = f"[img]{self.entry_img_link.get()}[/img]"
        raw_links = self.entry_dl_links.get("1.0", "end-1c").strip()
        dl_code_block = f"[CODE]\n{raw_links}\n[/CODE]" if raw_links else "N/A"
        hoster_list = [name for name, var in self.hoster_vars.items() if var.get()]
        hoster_str = ", ".join(hoster_list) if hoster_list else "N/A"
        bbcode = f"[CENTER]\n{titel_full}\n\n{img_bb}\n\nPlot:\n{self.post_data['plot']}\n\n\nSize:\n{self.post_data['file_size']}\n\n[SPOILER=\"NFO\"]\n{self.post_data['nfo_content_no_plot']}\n[/SPOILER]\n\n\n\nHoster:\n{hoster_str}\n\nDownload:\n{dl_code_block}\n[/CENTER]"
        self.post_preview_box.delete("1.0", "end")
        self.post_preview_box.insert("1.0", bbcode)
        self.clipboard_clear()
        self.clipboard_append(bbcode)
        messagebox.showinfo("BBCode Kopiert", "Der fertige BBCode wurde automatisch in deine Zwischenablage kopiert!")

    # Hauptprozess
    def start_process(self):
        if not self.selected_file or not self.entry_imdb.get(): return
        tech = self.analyze_video(self.selected_file)
        if not tech: return
        info = self.get_detailed_info(self.entry_imdb.get())
        self.post_data["title"] = self.entry_title.get()
        self.post_data["year"] = info["year"]
        self.post_data["plot"] = info["plot"]
        mb_size = round(os.path.getsize(self.selected_file) / (1024 * 1024))
        self.post_data["file_size"] = f"{mb_size} MB"
        data_map = {"title": self.entry_title.get(), "year": info["year"],
                    "imdb": f"imdb.com/title/{self.entry_imdb.get()}",
                    "genre": info["genres"], "plot": info["plot"], "format": f"{tech['codec']} @ MKV",
                    "video": f"{tech['res']} @ {tech['bitrate']}", "runtime": tech["runtime"]}
        nfo_final, nfo_no_plot = [], []
        for field in self.settings["fields"]:
            f_id = field["id"]
            if f_id in self.field_widgets and self.field_widgets[f_id]["check"].get():
                if f_id == "format": nfo_final.append(""); nfo_no_plot.append("")
                label = self.field_widgets[f_id]["entry"].get()
                if f_id == "plot":
                    lines = textwrap.wrap(f"{label}  {data_map['plot']}", width=90, subsequent_indent=" " * 20)
                    nfo_final.extend(lines)
                    nfo_final.append("")
                elif f_id in ["audio", "subs"]:
                    streams = tech['audio'] if f_id == "audio" else tech['subs']
                    for s in streams:
                        lang = s.get('tags', {}).get('language', '').upper()
                        lang = f"{lang} " if lang and lang != "UND" else ""
                        if f_id == "audio":
                            ch_m = {"6": "5.1", "2": "2.0", "8": "7.1"}
                            line = f"{label}  {lang}{s.get('codec_name', '').upper()} {ch_m.get(str(s.get('channels')), '2.0')}"
                        else:
                            line = f"{label}  {lang} Full"
                        nfo_final.append(line)
                        nfo_no_plot.append(line)
                else:
                    line = f"{label}  {str(data_map.get(f_id, 'N/A'))}"
                    nfo_final.append(line)
                    nfo_no_plot.append(line)
        self.post_data["nfo_content_no_plot"] = "\n".join(nfo_no_plot)
        path = os.path.splitext(self.selected_file)[0] + ".nfo"
        try:
            with open(path, "w", encoding="cp437", errors="replace") as f:
                f.write("\n".join(nfo_final))
            self.log("NFO gespeichert.")
            self.btn_tab_post.configure(state="normal")
            messagebox.showinfo("Erfolg", "NFO erstellt! Der Post-Generator ist nun bereit.")
        except Exception as e:
            self.log(f"Fehler: {e}", True)

    # Standard Funktionen
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

    def load_settings(self):
        base_data = {"cover": True, "fields": self.default_fields, "compact_mode": False}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    loaded = json.load(f)
                    return loaded if "fields" in loaded else base_data
            except Exception:
                return base_data
        return base_data

    def on_closing(self):
        try:
            if self.field_widgets:
                for item in self.settings["fields"]:
                    f_id = item["id"]
                    if f_id in self.field_widgets:
                        item["label"] = self.field_widgets[f_id]["entry"].get()
                        item["enabled"] = self.field_widgets[f_id]["check"].get()
                self.settings["cover"], self.settings["compact_mode"] = self.cover_var.get(), self.is_compact
                with open(self.settings_file, "w") as f:
                    json.dump(self.settings, f, indent=4)
        except Exception:
            pass
        self.destroy()

    def log(self, text, is_error=False):
        prefix = "ℹ️ " if not is_error else "❌ "
        self.log_box.insert("end", f"{prefix}{text}\n")
        self.log_box.see("end")
        self.update()

    # IMDb Suche mit Farbindikator
    def search_imdb_stable(self):
        raw = self.entry_title.get().strip()
        if not raw: return
        try:
            res = requests.get(
                f"https://v3.sg.media-imdb.com/suggestion/{raw[0].lower()}/{raw.replace(' ', '_').lower()}.json",
                timeout=5).json()
            if "d" in res:
                movie = res["d"][0]
                self.entry_imdb.delete(0, "end")
                self.entry_imdb.insert(0, movie["id"])
                self.poster_url = movie.get("i", {}).get("imageUrl", "")
                self.log(f"Gefunden: {movie['l']} ({movie.get('y')})")
                # VISUAL FEEDBACK: GRÜN
                self.entry_imdb.configure(border_color="#2ecc71")
            else:
                raise Exception()
        except Exception:
            self.log("Suche fehlgeschlagen.", True)
            # VISUAL FEEDBACK: ROT
            self.entry_imdb.configure(border_color="#e74c3c")

    # Datei auswählen (Inklusive Reset der Indikatoren)
    def select_file(self):
        fn = filedialog.askopenfilename(filetypes=[("Video files", "*.mkv *.mp4 *.avi")])
        if fn:
            self.selected_file = fn
            self.label_file_path.configure(text=fn)
            self.entry_title.delete(0, "end")
            self.entry_title.insert(0, os.path.basename(fn).rsplit('.', 1)[0].replace(".", " "))
            self.btn_tab_post.configure(state="disabled")
            self.entry_img_link.delete(0, "end")
            self.entry_dl_links.delete("1.0", "end")
            # FARBE RESETTEN
            self.entry_imdb.configure(border_color=self.default_border)
            self.switch_tab("main")

    def get_detailed_info(self, imdb_id):
        self.log(f"Abruf via IMDb für: {imdb_id}")
        try:
            movie = imdb_web.get_title(imdb_id, headers={"Accept-Language": "de-DE"})
            plot = movie.plot
            if isinstance(plot, dict): plot = plot.get('de-DE') or plot.get('de') or list(plot.values())[0]
            return {"plot": " ".join(str(plot).split()), "genres": ", ".join(movie.genres or []),
                    "year": str(getattr(movie, 'year', 'N/A'))}
        except Exception as e:
            self.log(f"Abruf-Fehler: {e}", True); return {"plot": "Fehler", "genres": "N/A", "year": "N/A"}

    def analyze_video(self, file_path):
        self.log("Analysiere Video...")
        try:
            data = json.loads(subprocess.run(
                [self.ffprobe_path, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path],
                capture_output=True, text=True).stdout)
            v = next(s for s in data['streams'] if s['codec_type'] == 'video')
            dur = float(data['format'].get('duration', 1))
            codec = v.get('codec_name', 'UNK').upper()
            if codec == "H264": codec = "AVC"
            if v.get("color_transfer") == "smpte2084": codec += " (HDR10)"
            return {"res": f"{v.get('width')}x{v.get('height')}", "codec": codec,
                    "bitrate": f"{int((os.path.getsize(file_path) * 8) / dur / 1000)} kb/s",
                    "runtime": f"{int(dur // 3600):02d}:{int((dur % 3600) // 60):02d}:{int(dur % 60):02d}",
                    "audio": [s for s in data['streams'] if s['codec_type'] == 'audio'],
                    "subs": [s for s in data['streams'] if s['codec_type'] == 'subtitle']}
        except Exception:
            return None


if __name__ == "__main__":
    app = NFOCreator();
    app.mainloop()