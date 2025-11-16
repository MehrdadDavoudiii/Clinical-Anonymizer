import os
import sys
import json
import threading
import webbrowser

import fitz 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import sv_ttk 


# ----------------------------------------------------------------------
#PATHS
# ----------------------------------------------------------------------
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()

HELP_FILES = [
    os.path.join(BASE_DIR, "HELP.txt"),
]

ACK_FILES = [
    os.path.join(BASE_DIR, "ACKNOWLEDGEMENT.txt"),
]

LICENSE_FILES = [
    os.path.join(BASE_DIR, "LICENSE.txt"),
]

USER_PHOTO_FILES = [
    os.path.join(BASE_DIR, "user_photo.png"),
]

# ----------------------------------------------------------------------
# BUILT-IN REDACTION TERMS
# ----------------------------------------------------------------------
KEY_VALUE_PAIRS = [
    # English
    "Name", "Last Name", "Family Name","First Name", "Middle Name", "Address", "Street Address",
    "City", "State", "Zip", "County", "Date of Birth", "birthdate", "DOB",
    "Age", "Date of Admission", "Admission Date", "Date of Discharge",
    "Discharge Date", "Date of Death", "Date Measured", "Telephone Number", "Phone",
    "Fax Number", "Fax", "Email Address", "Email", "Social Security Number", "SSN",
    "Medical Record Number", "MRN", "Patient ID", "Patient Number",
    "Health Plan Beneficiary Number", "Member ID", "Insurance ID", "Insurance Number", "Health Insurance", "Account Number",
    "Certificate/License Number", "Vehicle Identifier", "License Plate",
    "Device Identifier", "Serial Number", "Sex", "Gender", "Attending Physician",
    "Referring Physician",
    # Deutsch
    "Nachname", "Vorname", "Adresse", "Straße", "Stadt", "Ort", "Land",
    "PLZ", "Postleitzahl", "Geburtsdatum", "Geburtstag", "Geb.", "Alter",
    "Aufnahmedatum", "Entlassungsdatum", "Todesdatum", "Messdatum",
    "Telefonnummer", "Tel", "Faxnummer", "E-Mail", "Sozialversicherungsnummer",
    "SV-Nummer", "Patienten-ID", "Patientennummer", "Krankenversicherungsnummer",
    "Versichertennummer", "Kontonummer", "Lizenznummer", "Fahrzeug-ID",
    "Kennzeichen", "Geräte-ID", "Seriennummer", "Geschlecht",
    "Behandelnder Arzt", "Überweisender Arzt", "Arzt", "Klinik", "Krankenhaus",
    # Français
    "Nom", "Nom de naissance", "Nom de famille", "Prénom", "Adresse", "Rue",
    "Ville", "Code Postal", "Date de naissance", "Né(e) le", "Âge",
    "Date d'admission", "Date d'entrée", "Date de sortie", "Date de décès",
    "Date de la mesure", "Numéro de téléphone", "Tél", "Numéro de fax",
    "Adresse e-mail", "Courriel", "Numéro de Sécurité Sociale", "N° SS",
    "Numéro de dossier patient", "N° Dossier", "ID Patient",
    "Numéro d'assurance maladie", "Numéro de compte", "Numéro de licence",
    "Plaque d'immatriculation", "Numéro de série", "Identifiant de l'appareil",
    "Sexe", "Genre", "Médecin traitant", "Médecin référent",
]


# ----------------------------------------------------------------------
# FILE LOADERS
# ----------------------------------------------------------------------

def load_first_existing(paths, fallback_text):
    for p in paths:
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception:
            continue 
    return fallback_text


HELP_TEXT = load_first_existing(
    HELP_FILES,
    "Help.txt not found.\n",
)


ACK_TEXT = load_first_existing(
    ACK_FILES,
    "Acknowledgment file (Acknowledgment.txt) not found.\n",
)

LICENSE_TEXT = load_first_existing(
    LICENSE_FILES,
    "LICENSE.txt not found.",
)

# ----------------------------------------------------------------------
# STYLED UI HELPER – STANDARD HEADER WITH PHOTO
# ----------------------------------------------------------------------


def add_photo_header(window, title, subtitle=None):
    header = ttk.Frame(window, padding="20 10 20 20")
    header.pack(fill=tk.X, side=tk.TOP)

    root = window.master
    user_photo = getattr(root, "user_photo_small", None)

    header.columnconfigure(1, weight=1)

    if user_photo is not None:
        img_label = ttk.Label(header, image=user_photo)
        img_label.image = user_photo
        img_label.grid(row=0, column=0, rowspan=2, sticky=tk.NW, padx=(0, 15))

    
    title_label = ttk.Label(header, text=title, font=("Segoe UI", 14, "bold"))
    title_label.grid(row=0, column=1, sticky=tk.W)

    if subtitle:
        subtitle_label = ttk.Label(
            header, text=subtitle, font=("Segoe UI", 10)
        )
        subtitle_label.grid(row=1, column=1, sticky=tk.W, pady=(2, 0))

# ----------------------------------------------------------------------
# REDACTION TERMS MANAGER
# ----------------------------------------------------------------------

class RedactionTermsManager:
    def __init__(self, parent):
        self.parent = parent
        self.terms_file = os.path.join(BASE_DIR, "redaction_terms.json")
        self.terms = self.load_terms()

    def load_terms(self):
        try:
            if os.path.exists(self.terms_file):
                with open(self.terms_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return KEY_VALUE_PAIRS.copy()

    def save_terms(self):
        try:
            with open(self.terms_file, "w", encoding="utf-8") as f:
                json.dump(self.terms, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save terms: {e}")

    def show_manager(self):
        window = tk.Toplevel(self.parent)
        window.title("Clinical Anonymizer – Redaction Terms")
        window.geometry("750x550")
        window.minsize(700, 500)
        window.transient(self.parent)
        window.grab_set()
        if hasattr(self.parent, "user_photo_small"):
            window.iconphoto(False, self.parent.user_photo_small)

        add_photo_header(
            window,
            "Redaction Terms",
            "Built-in and user-defined labels used for anonymization.",
        )

        main = ttk.Frame(window, padding="20")
        main.pack(fill=tk.BOTH, expand=True)

        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)  

        top_frame = ttk.Frame(main)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        
    
        add_group = ttk.Frame(top_frame)
        add_group.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        add_group.columnconfigure(0, weight=1)
        ttk.Label(add_group, text="Add New Term:", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        self.new_term_var = tk.StringVar()
        entry = ttk.Entry(add_group, textvariable=self.new_term_var)
        entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(add_group, text="Add Term", command=self.add_term).grid(
            row=1, column=1
        )

        search_group = ttk.Frame(top_frame)
        search_group.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        search_group.columnconfigure(0, weight=1)
        ttk.Label(search_group, text="Search Term:", font=("Segoe UI",10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_group, textvariable=self.search_var)
        search_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(search_group, text="Find", command=self.search_term).grid(
            row=1, column=1
        )
        
        ttk.Label(
            main, text="Current Redaction Terms:", font=("Segoe UI",10, "bold")
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        list_frame = ttk.Frame(main)
        list_frame.grid(
            row=2,
            column=0,
            sticky=(tk.N, tk.S, tk.E, tk.W),
            pady=(0, 10),
        )
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(
            list_frame, selectmode=tk.SINGLE, font=("Segoe UI",10)
        )
        self.listbox.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.listbox.yview
        )
        scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.listbox.configure(yscrollcommand=scroll.set)

        action = ttk.Frame(main)
        action.grid(row=3, column=0, sticky=tk.W, pady=(5, 0))

        ttk.Button(action, text="Edit Selected", command=self.edit_term).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(action, text="Delete Selected", command=self.delete_term).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(action, text="Reset to Defaults", command=self.reset_terms).pack(
            side=tk.LEFT, padx=(5, 0)
        )

        bottom = ttk.Frame(main)
        bottom.grid(row=4, column=0, sticky=tk.E, pady=(20, 0))

        def on_save_and_close():
            self.save_terms()
            window.destroy()

        ttk.Button(
            bottom,
            text="Save and Close",
            command=on_save_and_close,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom, text="Cancel", command=window.destroy).pack(
            side=tk.LEFT
        )

        self.refresh_listbox()
        self.listbox.bind("<Double-Button-1>", lambda e: self.edit_term())
        self.listbox.bind("<Key>", self.on_listbox_key)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for t in sorted(self.terms):
            self.listbox.insert(tk.END, t)

    def add_term(self):
        term = self.new_term_var.get().strip()
        if not term:
            messagebox.showwarning("Warning", "Please enter a term.")
            return
        if term in self.terms:
            messagebox.showwarning("Warning", "Term already exists.")
            return
        self.terms.append(term)
        self.new_term_var.set("")
        self.refresh_listbox()

    def search_term(self):
        query = (self.search_var.get() or "").strip().lower()
        if not query:
            return
        size = self.listbox.size()
        if size == 0:
            return
        start = 0
        cur = self.listbox.curselection()
        if cur:
            start = (cur[0] + 1) % size
        for offset in range(size):
            idx = (start + offset) % size
            text = self.listbox.get(idx).lower()
            if query in text:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(idx)
                self.listbox.see(idx)
                break
        else:
            messagebox.showinfo("Not found", f"'{self.search_var.get()}' not found in term list.")

    def on_listbox_key(self, event):
        ch = (event.char or "").lower()
        if not ch.isalpha():
            return
        size = self.listbox.size()
        if size == 0:
            return
        start = 0
        cur = self.listbox.curselection()
        if cur:
            start = (cur[0] + 1) % size
        for offset in range(size):
            idx = (start + offset) % size
            text = self.listbox.get(idx).lower()
            if text.startswith(ch):
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(idx)
                self.listbox.see(idx)
                break
        return "break"

    def edit_term(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a term to edit.")
            return
        index = sel[0]
        old = self.listbox.get(index)

        win = tk.Toplevel(self.parent)
        win.title("Edit Redaction Term")
        win.geometry("350x180")
        win.transient(self.parent)
        win.grab_set()
        if hasattr(self.parent, "user_photo_small"):
            win.iconphoto(False, self.parent.user_photo_small)
        
        main_frame = ttk.Frame(win, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Edit term:", font=("Segoe UI",10, "bold")).pack(pady=5, anchor=tk.W)
        var = tk.StringVar(value=old)
        ent = ttk.Entry(main_frame, textvariable=var, width=30)
        ent.pack(pady=5, fill=tk.X, expand=True)
        ent.select_range(0, tk.END)
        ent.focus()

        def save():
            new = var.get().strip()
            if new and new != old:
                if new not in self.terms:
                    self.terms[self.terms.index(old)] = new
                    self.refresh_listbox()
                else:
                    messagebox.showwarning(
                        "Warning", "A term with this name already exists."
                    )
            win.destroy()

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(15, 0), anchor=tk.E)
        ttk.Button(btn_frame, text="Save", command=save, style="Accent.TButton").pack(
            side=tk.LEFT, padx=10
        )
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(
            side=tk.LEFT
        )

    def delete_term(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a term to delete.")
            return
        term = self.listbox.get(sel[0])
        if messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete '{term}'?"
        ):
            self.terms.remove(term)
            self.refresh_listbox()

    def reset_terms(self):
        if messagebox.askyesno(
            "Confirm Reset",
            "This will restore the default list and remove your custom changes. Continue?",
        ):
            self.terms = KEY_VALUE_PAIRS.copy()
            self.refresh_listbox()

    def save_and_close(self, window):
        self.save_terms()
        window.destroy()

# ----------------------------------------------------------------------
# POP-UP WINDOWS
# ----------------------------------------------------------------------


class HelpWindow:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        w = tk.Toplevel(self.parent)
        w.title("Usage Help – Clinical Anonymizer")
        w.geometry("700x520")
        w.transient(self.parent)
        w.grab_set()
        if hasattr(self.parent, "user_photo_small"):
            w.iconphoto(False, self.parent.user_photo_small)

        add_photo_header(
            w,
            "Usage Help",
            "How to prepare PDF reports for safe use with AI tools.",
        )

        main = ttk.Frame(w, padding="0 20 20 20")
        main.pack(fill=tk.BOTH, expand=True)
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        txt = ScrolledText(main, wrap=tk.WORD, width=80, height=20)
        txt.grid(row=0, column=0, sticky="nsew")
        txt.insert(tk.END, HELP_TEXT)
        txt.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=1, column=0, sticky=tk.E, pady=(15, 0))
        ttk.Button(btn_frame, text="Close", command=w.destroy).pack()


class AcknowledgmentWindow:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        w = tk.Toplevel(self.parent)
        w.title("Acknowledgments – Clinical Anonymizer")
        w.geometry("700x520")
        w.transient(self.parent)
        w.grab_set()
        if hasattr(self.parent, "user_photo_small"):
            w.iconphoto(False, self.parent.user_photo_small)

        add_photo_header(
            w,
            "Acknowledgments / Danksagung",
            "Support for the development of Clinical Anonymizer.",
        )

        main = ttk.Frame(w, padding="0 20 20 20")
        main.pack(fill=tk.BOTH, expand=True)
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        txt = ScrolledText(main, wrap=tk.WORD, width=80, height=20)
        txt.grid(row=0, column=0, sticky="nsew")
        txt.insert(tk.END, ACK_TEXT)
        txt.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=1, column=0, sticky=tk.E, pady=(15, 0))
        ttk.Button(btn_frame, text="Close", command=w.destroy).pack()


class LicenseWindow:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        w = tk.Toplevel(self.parent)
        w.title("View License – Clinical Anonymizer")
        w.geometry("700x520")
        w.transient(self.parent)
        w.grab_set()
        if hasattr(self.parent, "user_photo_small"):
            w.iconphoto(False, self.parent.user_photo_small)

        add_photo_header(
            w,
            "License",
            "GPL license and conditions of use.",
        )

        main = ttk.Frame(w, padding="0 20 20 20")
        main.pack(fill=tk.BOTH, expand=True)
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        txt = ScrolledText(main, wrap=tk.WORD, width=80, height=20)
        txt.grid(row=0, column=0, sticky="nsew")
        txt.insert(tk.END, LICENSE_TEXT)
        txt.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=1, column=0, sticky=tk.E, pady=(15, 0))
        ttk.Button(btn_frame, text="Close", command=w.destroy).pack()


# ----------------------------------------------------------------------
# MAIN APP
# ----------------------------------------------------------------------


class PDFAnonymizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clinical Anonymizer")
        self.root.geometry("850x720")
        self.root.minsize(800, 650)
       
        self.title_font = ("Segoe UI", 18, "bold")
        self.subtitle_font = ("Segoe UI", 11, "bold")
        self.label_font = ("Segoe UI", 10, "bold")
        self.base_font = ("Segoe UI", 10, "bold")

        self.input_file = tk.StringVar()
        self.output_folder = tk.StringVar(value=os.getcwd())
        self.output_filename = tk.StringVar(value="anonymized_document.pdf")
        self.progress = tk.DoubleVar()
        self.status_text = tk.StringVar(
            value="Ready to anonymize clinical PDF documents."
        )
        self.redaction_mode = tk.StringVar(value="standard")

        self.terms_manager = RedactionTermsManager(root)
        self.help_window = HelpWindow(root)
        self.ack_window = AcknowledgmentWindow(root)
        self.license_window = LicenseWindow(root)

        self.interactive_widgets = []

        self.load_user_photo()

        self.build_menubar()
        self.create_widgets()

    # PHOTO -------------------------------------------------------------
    def load_user_photo(self):
        img = None
        for p in USER_PHOTO_FILES:
            if os.path.exists(p):
                try:
                    img = Image.open(p)
                    break
                except Exception:
                    continue
        if img is None:
            img = Image.new("RGB", (100, 100), color="#cccccc")

        img_large = img.resize((90, 90), Image.LANCZOS)
        self.user_photo_large = ImageTk.PhotoImage(img_large)
        self.root.user_photo_large = self.user_photo_large
        
        img_small = img.resize((50, 50), Image.LANCZOS)
        self.user_photo_small = ImageTk.PhotoImage(img_small)
        self.root.user_photo_small = self.user_photo_small
        
        self.root.iconphoto(True, self.user_photo_large)

    # MENU --------------------------------------------------------------
    def build_menubar(self):
        menubar = tk.Menu(self.root)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Usage Help", command=self.help_window.show)
        menubar.add_cascade(label="Help", menu=help_menu)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(
            label="View License", command=self.license_window.show
        )
        about_menu.add_command(
            label="Acknowledgments", command=self.ack_window.show
        )
        menubar.add_cascade(label="About", menu=about_menu)

        self.root.config(menu=menubar)

    # UI ---------------------------------------------------------------
    def create_widgets(self):
        main = ttk.Frame(self.root, padding="20")
        main.pack(fill=tk.BOTH, expand=True)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        main.columnconfigure(0, weight=1)
        main.rowconfigure(4, weight=1) 

        # HEADER -------------------------------------------------------
        header = ttk.Frame(main)
        header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 25))
        header.columnconfigure(1, weight=1)

        self.photo_label = ttk.Label(header, image=self.user_photo_large)
        self.photo_label.grid(row=0, column=0, rowspan=4, sticky=tk.NW, padx=(0, 20))
        self.photo_label.image = self.user_photo_large

        title_label = ttk.Label(
            header, text="Clinical Anonymizer", font=self.title_font
        )
        title_label.grid(row=0, column=1, sticky=tk.W)

        desc1 = ttk.Label(
            header,
            text="Mehrdad Davoudi",
            font=self.subtitle_font,
        )
        desc1.grid(row=1, column=1, sticky=tk.W, pady=(5,0))

        desc2 = ttk.Label(
            header,
            text=(
                "PhD student, Clinic for Orthopaedics, "
                "Heidelberg University Hospital, Heidelberg, Germany."
            ),
            font=self.base_font
        )
        desc2.grid(row=2, column=1, sticky=tk.W)

        desc3 = ttk.Label(
            header,
            text="Email: Mehrdad.Davoudi@med.uni-heidelberg.de",
            font=self.base_font
        )
        desc3.grid(row=3, column=1, sticky=tk.W, pady=(2, 0))

        io = ttk.LabelFrame(main, text="1. Document Configuration", padding="15")
        io.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        io.columnconfigure(1, weight=1)

        ttk.Label(io, text="Source PDF Document:", font=self.label_font).grid(
            row=0, column=0, sticky=tk.W, pady=4, padx=5
        )
        self.input_entry = ttk.Entry(io, textvariable=self.input_file, state="readonly")
        self.input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.browse_input_btn = ttk.Button(
            io, text="Browse", command=self.browse_input_file
        )
        self.browse_input_btn.grid(row=0, column=2, pady=5, padx=5)

        ttk.Label(io, text="Destination Folder:", font=self.label_font).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.output_entry = ttk.Entry(
            io, textvariable=self.output_folder, state="readonly"
        )
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.browse_output_btn = ttk.Button(
            io, text="Browse", command=self.browse_output_folder
        )
        self.browse_output_btn.grid(row=1, column=2, pady=5, padx=5)

        ttk.Label(io, text="Output Filename:", font=self.label_font).grid(
            row=2, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.output_filename_entry = ttk.Entry(
            io, textvariable=self.output_filename
        )
        self.output_filename_entry.grid(
            row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5
        )

        cfg_frame = ttk.LabelFrame(main, text="2. Redaction Configuration", padding="15")
        cfg_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        cfg_frame.columnconfigure(0, weight=1)
        cfg_frame.columnconfigure(1, weight=1)

        mode = ttk.Frame(cfg_frame)
        mode.grid(row=0, column=0, sticky="nwe", padx=(0, 10))
        ttk.Label(mode, text="Methodology", font=self.label_font).pack(anchor=tk.W, pady=(0, 5))

        self.radio_standard = ttk.Radiobutton(
            mode,
            text="Standard Protection (redacts identified words)",
            variable=self.redaction_mode,
            value="standard",
        )
        self.radio_standard.pack(anchor=tk.W, pady=3)

        self.radio_aggressive = ttk.Radiobutton(
            mode,
            text="Enhanced Protection (redacts contextual area)",
            variable=self.redaction_mode,
            value="aggressive",
        )
        self.radio_aggressive.pack(anchor=tk.W, pady=3)

        cfg = ttk.Frame(cfg_frame)
        cfg.grid(row=0, column=1, sticky="nwe", padx=(10, 0))
        ttk.Label(cfg, text="Sensitive Terms", font=self.label_font).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(
            cfg,
            text="Manage the terms used for detecting sensitive info:",
            wraplength=300
        ).pack(anchor=tk.W, pady=(0, 10))
        
        self.manage_terms_btn = ttk.Button(
            cfg,
            text="Manage Redaction Terms",
            command=self.terms_manager.show_manager,
            style="Accent.TButton",
        )
        self.manage_terms_btn.pack(anchor=tk.W, pady=(0, 4))

        buttons = ttk.LabelFrame(main, text="3. Execute", padding="15")
        buttons.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        buttons.columnconfigure(0, weight=1) 
        
        buttons_inner = ttk.Frame(buttons)
        buttons_inner.grid(row=0, column=0) 
        
        self.anonymize_btn = ttk.Button(
            buttons_inner,
            text="Execute Anonymization",
            command=self.start_anonymization,
            style="Accent.TButton",
        )
        self.anonymize_btn.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)

        self.reset_btn = ttk.Button(
            buttons_inner, text="Reset Configuration", command=self.reset,
            style="Accent.TButton"
        )
        self.reset_btn.pack(side=tk.LEFT, padx=10, ipady=5)

        status = ttk.Frame(main, padding="10 0 0 0")
        status.grid(
            row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0)
        )
        status.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(
            status,
            textvariable=self.status_text,
            anchor=tk.W,
        )
        self.status_label.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(4, 5)
        )
        
        self.progress_bar = ttk.Progressbar(
            status, variable=self.progress, mode="determinate"
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))


        
        self.interactive_widgets = [
            self.input_entry,
            self.browse_input_btn,
            self.output_entry,
            self.browse_output_btn,
            self.output_filename_entry,
            self.radio_standard,
            self.radio_aggressive,
            self.manage_terms_btn,
            self.anonymize_btn,
            self.reset_btn,
        ]

    # ------------------------------------------------------------------
    # CORE LOGIC
    # ------------------------------------------------------------------

    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select PDF Document for Anonymization",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if filename:
            self.input_file.set(filename)
            base = os.path.splitext(os.path.basename(filename))[0]
            self.output_filename.set(f"{base}_anonymized.pdf")
            self.output_folder.set(os.path.dirname(filename))

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Destination Folder")
        if folder:
            self.output_folder.set(folder)

    def toggle_ui_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        for w in self.interactive_widgets:
            try:
                if w in (self.input_entry, self.output_entry):
                    if enabled:
                        w.config(state="readonly")
                    else:
                        w.config(state=tk.DISABLED)
                else:
                    w.config(state=state)
            except tk.TclError:
                pass

    def safe_update_status(self, text):
        self.root.after(0, lambda: self.status_text.set(text))

    def safe_update_progress(self, value):
        self.root.after(0, lambda: self.progress.set(value))

    def safe_show_error(self, title, message):
        self.root.after(0, lambda: messagebox.showerror(title, message))

    def safe_ask_yes_no(self, title, message):
        selfind = threading.Condition()
        result = [None] 

        def ask():
            with selfind:
                result[0] = messagebox.askyesno(title, message)
                selfind.notify()

        self.root.after(0, ask)
        
        with selfind:
            selfind.wait()
            return result[0]

    def start_anonymization(self):
        if not self.input_file.get() or not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "Please select a valid PDF document.")
            return
        if not self.output_folder.get():
            messagebox.showerror("Error", "Please specify an output folder.")
            return

        self.toggle_ui_state(False)
        self.progress.set(0)
        th = threading.Thread(target=self.anonymize_pdf, daemon=True)
        th.start()

    def anonymize_pdf(self):
        try:
            input_path = self.input_file.get()
            output_path = os.path.join(self.output_folder.get(), self.output_filename.get())

            self.safe_update_status("Opening PDF document…")
            self.safe_update_progress(10)

            # --- This is the fix for the re-run bug ---
            with open(input_path, "rb") as f:
                file_data = f.read()
            
            doc = fitz.open(stream=file_data, filetype="pdf")
            # --- End of fix ---

            total_pages = len(doc)

         
            all_terms = [t.strip() for t in self.terms_manager.terms if t.strip()]
            single_terms = [t for t in all_terms if " " not in t]
            phrase_terms = [t for t in all_terms if " " in t]
            single_terms_set = {t.lower() for t in single_terms}

            for page_index, page in enumerate(doc):
                self.safe_update_status(
                    f"Processing page {page_index + 1} of {total_pages}…"
                )
                progress = 10 + (page_index / max(total_pages, 1)) * 80
                self.safe_update_progress(progress)

                
                words = page.get_text("words") or []
                for (x0, y0, x1, y1, text, *_rest) in words:
                    norm = text.strip(",:;").lower()
                    if norm in single_terms_set:
                        rect = fitz.Rect(x0, y0, x1, y1)
                        margin = 0.5
                        rect = fitz.Rect(
                            rect.x0 - margin,
                            rect.y0 - margin,
                            rect.x1 + margin,
                            rect.y1 + margin,
                        )
                        page.add_redact_annot(rect, text="[REDACTED]", fill=(0, 0, 0))

                        if self.redaction_mode.get() == "aggressive":
                            right = fitz.Rect(rect.x1, rect.y0 - 2,
                                              rect.x1 + 150, rect.y1 + 2)
                            page.add_redact_annot(right, text=" ", fill=(0, 0, 0))
                            below = fitz.Rect(rect.x0 - 10, rect.y1,
                                              rect.x1 + 150, rect.y1 + 20)
                            page.add_redact_annot(below, text=" ", fill=(0, 0, 0))

                
                for phrase in phrase_terms:
                    
                    # --- THIS IS THE CORRECTED LINE ---
                    # Using the integer 1 directly to force case-insensitivity
                    for rect in page.search_for(phrase, flags=1):
                    
                        page.add_redact_annot(rect, text="[REDACTED]", fill=(0, 0, 0))
                        if self.redaction_mode.get() == "aggressive":
                            right = fitz.Rect(rect.x1, rect.y0 - 2,
                                              rect.x1 + 150, rect.y1 + 2)
                            page.add_redact_annot(right, text=" ", fill=(0, 0, 0))
                            below = fitz.Rect(rect.x0 - 10, rect.y1,
                                              rect.x1 + 150, rect.y1 + 20)
                            page.add_redact_annot(below, text=" ", fill=(0, 0, 0))

                page.apply_redactions()

            self.safe_update_status("Saving anonymized document…")
            self.safe_update_progress(95)
            doc.save(output_path)
            doc.close()

            self.safe_update_progress(100)
            self.safe_update_status("Document anonymization completed successfully.")

            if self.safe_ask_yes_no(
                "Process Completed",
                f"Document successfully anonymized and saved to:\n{output_path}\n\n"
                "Do you want to open the output folder?",
            ):
                try:
                    webbrowser.open(os.path.realpath(self.output_folder.get()))
                except Exception as e:
                    self.safe_show_error("Error", f"Could not open folder: {e}")

        except Exception as e:
            self.safe_update_status(f"Processing error: {e}")
            self.safe_show_error(
                "Processing Error",
                f"An error occurred during anonymization:\n{e}",
            )
        finally:
            self.root.after(0, lambda: self.toggle_ui_state(True))
            self.root.after(0, lambda: self.progress.set(0))
            self.root.after(100, lambda: self.safe_update_status("Ready."))

    def reset(self):
        self.input_file.set("")
        self.output_folder.set(os.getcwd())
        self.output_filename.set("anonymized_document.pdf")
        self.progress.set(0)
        self.status_text.set("Ready to anonymize clinical PDF documents.")
        self.redaction_mode.set("standard")


def main():
    root = tk.Tk()
    sv_ttk.set_theme("light")
    app = PDFAnonymizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()