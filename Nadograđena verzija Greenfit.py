import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import xml.etree.ElementTree as ET
import os
import re
import sys
from functools import partial
from copy import deepcopy


try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except Exception:
    TKCALENDAR_AVAILABLE = False


def add_months(dt: datetime, months: int) -> datetime:

    y = dt.year + (dt.month - 1 + months) // 12
    m = (dt.month - 1 + months) % 12 + 1
    d = dt.day
    for day in (31, 30, 29, 28):
        try:
            new = datetime(y, m, min(d, day), dt.hour, dt.minute, dt.second)
            return new
        except ValueError:
            continue
    return datetime(y, m, 1, dt.hour, dt.minute, dt.second)

def format_date(d: datetime):
    if d is None:
        return ""
    return d.strftime("%d.%m.%Y")

def parse_date_str(s: str):
    """Parse date dd.mm.yyyy -> datetime. Raises ValueError if invalid."""
    return datetime.strptime(s.strip(), "%d.%m.%Y")


EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_RE = re.compile(r"^\+?\d[\d\s\-]{5,}$")  

def valid_name(s: str):
    return bool(re.fullmatch(r"[A-Za-zČčĆćĐđŠšŽž\s\-]+", s.strip()))

def valid_contact(s: str):
    s = (s or "").strip()
    if not s:
        return True  
    return bool(EMAIL_RE.match(s) or PHONE_RE.match(s))


class Clanarina:
    def __init__(self, datum_uplate: datetime, trajanje_mjeseci: int, cijena: float):
        self.datum_uplate = datum_uplate
        self.trajanje_mjeseci = trajanje_mjeseci
        self.cijena = cijena

    def datum_isteka(self) -> datetime:
        return add_months(self.datum_uplate, self.trajanje_mjeseci)

    def aktivna(self) -> bool:
        return date.today() <= self.datum_isteka().date()

class RedovnaClanarina(Clanarina):
    pass

class StudentskaClanarina(Clanarina):
    def __init__(self, datum_uplate, trajanje_mjeseci, cijena):
        super().__init__(datum_uplate, trajanje_mjeseci, cijena * 0.8)

class Clan:
    def __init__(self, ime: str, prezime: str, kontakt: str):
        self.ime = ime
        self.prezime = prezime
        self.kontakt = kontakt
        self.clanarina = None

    def status_str(self):
        if self.clanarina and self.clanarina.aktivna():
            return "AKTIVNA"
        return "ISTEKLA"

    def __str__(self):
        return f"{self.ime} {self.prezime} - {self.status_str()}"


class EvidencijaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GreenFit Evidencija 2.0")
        self.root.configure(bg="#d8f3dc")
        self.clanovi = []

        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Spremi (XML)", command=self.spremi_xml)
        file_menu.add_command(label="Učitaj (XML)", command=self.ucitaj_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Izlaz", command=self.izlaz)
        menubar.add_cascade(label="Datoteka", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="O aplikaciji", command=self.o_aplikaciji)
        menubar.add_cascade(label="Pomoć", menu=help_menu)

        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="Izvještaji", command=self.prikazi_izvjestaje)
        menubar.add_cascade(label="Analitika", menu=reports_menu)

        root.config(menu=menubar)

        frame_clan = tk.LabelFrame(root, text="Unos člana", bg="#b7e4c7")
        frame_clan.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        tk.Label(frame_clan, text="Ime:", bg="#b7e4c7").grid(row=0, column=0, sticky="w")
        tk.Label(frame_clan, text="Prezime:", bg="#b7e4c7").grid(row=1, column=0, sticky="w")
        tk.Label(frame_clan, text="Kontakt (email/telefon):", bg="#b7e4c7").grid(row=2, column=0, sticky="w")

        self.e_ime = tk.Entry(frame_clan)
        self.e_prezime = tk.Entry(frame_clan)
        self.e_kontakt = tk.Entry(frame_clan)

        self.e_ime.grid(row=0, column=1, padx=4, pady=2)
        self.e_prezime.grid(row=1, column=1, padx=4, pady=2)
        self.e_kontakt.grid(row=2, column=1, padx=4, pady=2)

        tk.Button(frame_clan, text="Dodaj člana", command=self.dodaj_clana, bg="#95d5b2").grid(row=3, column=0, columnspan=2, pady=6, sticky="we")

        frame_clanarina = tk.LabelFrame(root, text="Unos članarine", bg="#b7e4c7")
        frame_clanarina.grid(row=1, column=0, padx=10, pady=10, sticky="n")

        tk.Label(frame_clanarina, text="Datum uplate:", bg="#b7e4c7").grid(row=0, column=0, sticky="w")
        tk.Label(frame_clanarina, text="Trajanje (mj):", bg="#b7e4c7").grid(row=1, column=0, sticky="w")
        tk.Label(frame_clanarina, text="Cijena:", bg="#b7e4c7").grid(row=2, column=0, sticky="w")

        if TKCALENDAR_AVAILABLE:
            self.e_datum = DateEntry(frame_clanarina, date_pattern="dd.mm.yyyy")
        else:
            self.e_datum = tk.Entry(frame_clanarina)
            self.e_datum.insert(0, "dd.mm.gggg")

        self.e_trajanje = tk.Entry(frame_clanarina)
        self.e_cijena = tk.Entry(frame_clanarina)

        self.e_datum.grid(row=0, column=1, padx=4, pady=2)
        self.e_trajanje.grid(row=1, column=1, padx=4, pady=2)
        self.e_cijena.grid(row=2, column=1, padx=4, pady=2)

        tk.Button(frame_clanarina, text="Redovna", command=lambda: self.dodaj_clanarinu_tip("redovna"), bg="#95d5b2").grid(row=3, column=0, pady=6, sticky="we")
        tk.Button(frame_clanarina, text="Studentska", command=lambda: self.dodaj_clanarinu_tip("studentska"), bg="#95d5b2").grid(row=3, column=1, pady=6, sticky="we")

        frame_lista = tk.LabelFrame(root, text="Lista članova", bg="#b7e4c7")
        frame_lista.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        frame_lista.grid_rowconfigure(0, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)

        filter_frame = tk.Frame(frame_lista, bg="#b7e4c7")
        filter_frame.grid(row=0, column=0, sticky="we", padx=6, pady=(6, 0))
        tk.Label(filter_frame, text="Filter (ime/prezime):", bg="#b7e4c7").pack(side="left")
        self.filter_var = tk.StringVar()
        ent_filter = tk.Entry(filter_frame, textvariable=self.filter_var)
        ent_filter.pack(side="left", fill="x", expand=True, padx=(6,0))
        ent_filter.bind("<KeyRelease>", lambda e: self.prikazi_clanove())


        columns = ("ime", "prezime", "status", "istice", "cijena", "kontakt")
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("ime", text="Ime", command=lambda: self.sort_tree("ime", False))
        self.tree.heading("prezime", text="Prezime", command=lambda: self.sort_tree("prezime", False))
        self.tree.heading("status", text="Status", command=lambda: self.sort_tree("status", False))
        self.tree.heading("istice", text="Ističe", command=lambda: self.sort_tree("istice", False))
        self.tree.heading("cijena", text="Cijena", command=lambda: self.sort_tree("cijena", False))
        self.tree.heading("kontakt", text="Kontakt", command=lambda: self.sort_tree("kontakt", False))


        self.tree.column("ime", width=120, anchor="w")
        self.tree.column("prezime", width=120, anchor="w")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("istice", width=100, anchor="center")
        self.tree.column("cijena", width=80, anchor="e")
        self.tree.column("kontakt", width=150, anchor="w")

        self.tree.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self.tree.bind("<Double-1>", self.on_tree_double_click)


        btn_frame = tk.Frame(frame_lista, bg="#b7e4c7")
        btn_frame.grid(row=2, column=0, sticky="we", padx=6, pady=(0,6))
        tk.Button(btn_frame, text="Ažuriraj status", command=self.azuriraj_status, bg="#95d5b2").pack(side="left", padx=4)
        tk.Button(btn_frame, text="Uredi", command=self.uredi_odabranog, bg="#ffd166").pack(side="left", padx=4)
        tk.Button(btn_frame, text="Obriši", command=self.obrisi_odabranog, bg="#ef476f").pack(side="left", padx=4)
        tk.Button(btn_frame, text="Izvještaji", command=self.prikazi_izvjestaje, bg="#06d6a0").pack(side="left", padx=4)

        logo_text = r"""
  ____                     ______ _ _   
 / ___|_ __ ___  ___ _ __ |  ___(_) |_ 
| |  _| '__/ _ \/ _ \ '_ \| |_  | | __|
| |_| | | |  __/  __/ | | |  _| | | |_ 
 \____|_|  \___|\___|_| |_|_|   |_|\__|
"""
        self.logo_label = tk.Label(root, text=logo_text, font=("Courier New", 9, "bold"),
                                   bg="#95d5b2", fg="#1b4332", justify="left")
        self.logo_label.grid(row=2, column=0, columnspan=2, pady=2, sticky="we")


        self.status = tk.Label(root, text="Dobrodošli u GreenFit Evidenciju 2.0!", bd=1, relief=tk.SUNKEN, anchor="w", bg="#74c69d")
        self.status.grid(row=3, column=0, columnspan=2, sticky="we")


        self._sort_state = {}

    def azuriraj_statusna_traku(self, tekst: str):
        self.status.config(text=tekst)

    def izlaz(self):
        if messagebox.askyesno("Izlaz", "Želite li izaći iz aplikacije?"):
            self.root.destroy()

    def o_aplikaciji(self):
        prozor = tk.Toplevel(self.root)
        prozor.title("O aplikaciji")
        prozor.configure(bg="#d8f3dc")
        prozor.resizable(False, False)

        logo_text = (
            "  ____                     ______ _ _   \n"
            " / ___|_ __ ___  ___ _ __ |  ___(_) |_ \n"
            "| |  _| '__/ _ \\/ _ \\ '_ \\| |_  | | __|\n"
            "| |_| | | |  __/  __/ | | |  _| | | |_ \n"
            " \\____|_|  \\___|\\___|_| |_|_|   |_|\\__|\n"
        )

        label_logo = tk.Label(prozor, text=logo_text, font=("Courier New", 12, "bold"),
                              bg="#d8f3dc", fg="#1b4332", justify="left")
        label_logo.pack(padx=20, pady=(20, 10))

        info_text = (
            "GreenFit\n"
            "Verzija 2.0\n"
            "Autor: Antonio M.\n"
        )
        label_info = tk.Label(prozor, text=info_text, bg="#d8f3dc", fg="#000", justify="left")
        label_info.pack(padx=20, pady=(0, 20))

        btn_ok = tk.Button(prozor, text="U redu", command=prozor.destroy, bg="#95d5b2")
        btn_ok.pack(pady=(0, 20))

        prozor.transient(self.root)
        prozor.grab_set()
        self.root.wait_window(prozor)


    def dodaj_clana(self):
        ime = self.e_ime.get().strip()
        prezime = self.e_prezime.get().strip()
        kontakt = self.e_kontakt.get().strip()


        if not ime or not prezime:
            messagebox.showerror("Greška", "Ime i prezime su obavezni!")
            return
        if not valid_name(ime) or not valid_name(prezime):
            messagebox.showerror("Greška", "Ime i prezime smiju sadržavati samo slova, razmake ili crtice!")
            return
        if not valid_contact(kontakt):
            messagebox.showerror("Greška", "Kontakt nije u ispravnom formatu (email ili broj telefona)!")
            return

        novi = Clan(ime, prezime, kontakt)
        self.clanovi.append(novi)
        self.prikazi_clanove()
        self.e_ime.delete(0, tk.END)
        self.e_prezime.delete(0, tk.END)
        self.e_kontakt.delete(0, tk.END)
        self.azuriraj_statusna_traku("Član dodan (status ISTEKLA dok se ne doda članarina).")

    def dodaj_clanarinu_tip(self, tip):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberi člana na listi (klik) prije dodavanja članarine!")
            return
        try:
            idx = int(self.tree.item(sel, "text"))
            clan = self.clanovi[idx]
        except Exception:
            messagebox.showerror("Greška", "Ne mogu dohvatiti odabranog člana.")
            return

        try:
            unos_datuma = self.e_datum.get().strip()
            if TKCALENDAR_AVAILABLE:
                if isinstance(unos_datuma, date):
                    datum = datetime(unos_datuma.year, unos_datuma.month, unos_datuma.day)
                else:
                    datum = parse_date_str(unos_datuma)
            else:
                if unos_datuma.endswith('.'):
                    unos_datuma = unos_datuma[:-1]
                datum = parse_date_str(unos_datuma)
        except ValueError:
            messagebox.showerror("Greška", "Datum nije u ispravnom formatu (dd.mm.gggg).")
            return

        try:
            trajanje = int(self.e_trajanje.get().strip())
        except ValueError:
            messagebox.showerror("Greška", "Trajanje mora biti cijeli broj mjeseci.")
            return

        try:
            cijena = float(self.e_cijena.get().strip())
        except ValueError:
            messagebox.showerror("Greška", "Cijena mora biti broj (npr. 150.0).")
            return

        if tip == "redovna":
            clan.clanarina = RedovnaClanarina(datum, trajanje, cijena)
        else:
            clan.clanarina = StudentskaClanarina(datum, trajanje, cijena)

        if not TKCALENDAR_AVAILABLE:
            self.e_datum.delete(0, tk.END)
            self.e_datum.insert(0, "dd.mm.gggg")
        else:
            try:
                self.e_datum.set_date(date.today())
            except Exception:
                pass
        self.e_trajanje.delete(0, tk.END)
        self.e_cijena.delete(0, tk.END)

        self.prikazi_clanove()
        self.azuriraj_statusna_traku("Članarina dodana. Klikni 'Ažuriraj status' ili pogledaj člana dvoklikom.")

    def prikazi_clanove(self):
        for it in self.tree.get_children():
            self.tree.delete(it)

        filter_text = (self.filter_var.get() or "").strip().lower()

        for idx, clan in enumerate(self.clanovi):
            full = f"{clan.ime} {clan.prezime}".lower()
            if filter_text and filter_text not in full:
                continue
            status = clan.status_str()
            istice = format_date(clan.clanarina.datum_isteka()) if clan.clanarina else ""
            cijena = f"{clan.clanarina.cijena:.2f}" if clan.clanarina else ""
            kontakt = clan.kontakt or ""
            self.tree.insert("", tk.END, text=str(idx), values=(clan.ime, clan.prezime, status, istice, cijena, kontakt))
            iid = self.tree.get_children()[-1]
            if clan.clanarina and clan.clanarina.aktivna():
                self.tree.item(iid, tags=("aktivna",))
            else:
                self.tree.item(iid, tags=("istekla",))

        style = ttk.Style()
        try:
            style.map("Treeview", foreground=[])
            self.tree.tag_configure("aktivna", foreground="#1b4332")
            self.tree.tag_configure("istekla", foreground="#d00000")
        except Exception:
            pass

    def azuriraj_status(self):
        self.prikazi_clanove()
        self.azuriraj_statusna_traku("Status članova ažuriran.")

    def obrisi_odabranog(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberi člana za brisanje.")
            return
        try:
            idx = int(self.tree.item(sel, "text"))
            clan = self.clanovi[idx]
        except Exception:
            messagebox.showerror("Greška", "Ne mogu dohvatiti odabranog člana.")
            return
        if not messagebox.askyesno("Potvrdi", f"Obriši člana {clan.ime} {clan.prezime}?"):
            return
        # Remove
        self.clanovi.pop(idx)
        self.prikazi_clanove()
        self.azuriraj_statusna_traku("Član obrisan.")

    def uredi_odabranog(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberi člana za uređivanje.")
            return
        try:
            idx = int(self.tree.item(sel, "text"))
            self.otvori_prozor_clana(idx)
        except Exception:
            messagebox.showerror("Greška", "Ne mogu dohvatiti odabranog člana.")
            return

    def on_tree_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        try:
            idx = int(self.tree.item(item, "text"))
            self.otvori_prozor_clana(idx)
        except Exception:
            self.azuriraj_statusna_traku("Greška pri otvaranju detalja člana.")

    def otvori_prozor_clana(self, idx):
        """Otvara Toplevel prozor s detaljima člana, omogućuje edit i dodavanje nove članarine"""
        clan = self.clanovi[idx]

        top = tk.Toplevel(self.root)
        top.title(f"Detalji člana: {clan.ime} {clan.prezime}")
        top.configure(bg="#d8f3dc")


        tk.Label(top, text="Ime:", bg="#d8f3dc").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        e_ime = tk.Entry(top)
        e_ime.grid(row=0, column=1, padx=6, pady=4)
        e_ime.insert(0, clan.ime)

        tk.Label(top, text="Prezime:", bg="#d8f3dc").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        e_prez = tk.Entry(top)
        e_prez.grid(row=1, column=1, padx=6, pady=4)
        e_prez.insert(0, clan.prezime)

        tk.Label(top, text="Kontakt:", bg="#d8f3dc").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        e_kont = tk.Entry(top)
        e_kont.grid(row=2, column=1, padx=6, pady=4)
        e_kont.insert(0, clan.kontakt or "")

        def spremi_izmjene():
            ime_new = e_ime.get().strip()
            prez_new = e_prez.get().strip()
            kont_new = e_kont.get().strip()
            if not ime_new or not prez_new:
                messagebox.showerror("Greška", "Ime i prezime su obavezni!")
                return
            if not valid_name(ime_new) or not valid_name(prez_new):
                messagebox.showerror("Greška", "Ime i prezime smiju sadržavati samo slova, razmake ili crtice!")
                return
            if not valid_contact(kont_new):
                messagebox.showerror("Greška", "Kontakt nije u ispravnom formatu!")
                return
            clan.ime = ime_new
            clan.prezime = prez_new
            clan.kontakt = kont_new
            self.prikazi_clanove()
            self.azuriraj_statusna_traku("Podaci člana ažurirani.")
            top.destroy()

        tk.Button(top, text="Spremi izmjene", command=spremi_izmjene, bg="#95d5b2").grid(row=3, column=0, columnspan=2, pady=6)


        ttk.Separator(top, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="we", pady=6)

        if clan.clanarina:
            tk.Label(top, text="Trenutna članarina:", bg="#d8f3dc", font=("TkDefaultFont", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", padx=6)
            tk.Label(top, text=f"Datum uplate: {format_date(clan.clanarina.datum_uplate)}", bg="#d8f3dc").grid(row=6, column=0, columnspan=2, sticky="w", padx=6)
            tk.Label(top, text=f"Trajanje (mj): {clan.clanarina.trajanje_mjeseci}", bg="#d8f3dc").grid(row=7, column=0, columnspan=2, sticky="w", padx=6)
            tk.Label(top, text=f"Cijena: {clan.clanarina.cijena:.2f}", bg="#d8f3dc").grid(row=8, column=0, columnspan=2, sticky="w", padx=6)
            tk.Label(top, text=f"Ističe: {format_date(clan.clanarina.datum_isteka())}", bg="#d8f3dc").grid(row=9, column=0, columnspan=2, sticky="w", padx=6)
            tk.Label(top, text=f"Tip: {clan.clanarina.__class__.__name__}", bg="#d8f3dc").grid(row=10, column=0, columnspan=2, sticky="w", padx=6)
        else:
            tk.Label(top, text="Član trenutno nema članarinu.", bg="#d8f3dc").grid(row=5, column=0, columnspan=2, sticky="w", padx=6)

        ttk.Separator(top, orient="horizontal").grid(row=11, column=0, columnspan=2, sticky="we", pady=6)
        tk.Label(top, text="Dodaj novu članarinu:", bg="#d8f3dc").grid(row=12, column=0, columnspan=2, sticky="w", padx=6)
        tk.Label(top, text="Datum uplate:", bg="#d8f3dc").grid(row=13, column=0, sticky="w", padx=6, pady=2)
        if TKCALENDAR_AVAILABLE:
            e_dat = DateEntry(top, date_pattern="dd.mm.yyyy")
        else:
            e_dat = tk.Entry(top)
            e_dat.insert(0, "dd.mm.gggg")
        e_dat.grid(row=13, column=1, padx=6, pady=2)

        tk.Label(top, text="Trajanje (mj):", bg="#d8f3dc").grid(row=14, column=0, sticky="w", padx=6, pady=2)
        e_traj = tk.Entry(top)
        e_traj.grid(row=14, column=1, padx=6, pady=2)

        tk.Label(top, text="Cijena:", bg="#d8f3dc").grid(row=15, column=0, sticky="w", padx=6, pady=2)
        e_cij = tk.Entry(top)
        e_cij.grid(row=15, column=1, padx=6, pady=2)

        def dodaj_novu(tip="redovna"):
            try:
                unos = e_dat.get().strip()
                if TKCALENDAR_AVAILABLE and isinstance(unos, date):
                    datum_n = datetime(unos.year, unos.month, unos.day)
                else:
                    if unos.endswith('.'):
                        unos = unos[:-1]
                    datum_n = parse_date_str(unos)
            except ValueError:
                messagebox.showerror("Greška", "Datum nije ispravan (dd.mm.gggg).")
                return
            try:
                traj = int(e_traj.get().strip())
            except ValueError:
                messagebox.showerror("Greška", "Trajanje mora biti cijeli broj.")
                return
            try:
                cij = float(e_cij.get().strip())
            except ValueError:
                messagebox.showerror("Greška", "Cijena mora biti broj.")
                return
            if tip == "redovna":
                clan.clanarina = RedovnaClanarina(datum_n, traj, cij)
            else:
                clan.clanarina = StudentskaClanarina(datum_n, traj, cij)
            self.prikazi_clanove()
            self.azuriraj_statusna_traku("Dodana nova članarina (iz prozora člana).")
            top.destroy()

        tk.Button(top, text="Dodaj redovnu", command=lambda: dodaj_novu("redovna"), bg="#95d5b2").grid(row=16, column=0, pady=6, padx=6, sticky="we")
        tk.Button(top, text="Dodaj studentsku", command=lambda: dodaj_novu("studentska"), bg="#95d5b2").grid(row=16, column=1, pady=6, padx=6, sticky="we")

        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)

    def spremi_xml(self):
        root = ET.Element("clanovi")
        for clan in self.clanovi:
            clan_el = ET.SubElement(root, "clan")
            ET.SubElement(clan_el, "ime").text = clan.ime
            ET.SubElement(clan_el, "prezime").text = clan.prezime
            ET.SubElement(clan_el, "kontakt").text = clan.kontakt or ""

            if clan.clanarina:
                cl_el = ET.SubElement(clan_el, "clanarina")
                cl_el.set("tip", clan.clanarina.__class__.__name__)
                ET.SubElement(cl_el, "datum_uplate").text = clan.clanarina.datum_uplate.strftime("%d.%m.%Y")
                ET.SubElement(cl_el, "trajanje").text = str(clan.clanarina.trajanje_mjeseci)
                ET.SubElement(cl_el, "cijena").text = str(clan.clanarina.cijena)

        tree = ET.ElementTree(root)
        try:
            tree.write("clanovi.xml", encoding="utf-8", xml_declaration=True)
            self.azuriraj_statusna_traku("Podaci spremljeni u clanovi.xml.")
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu spremiti XML: {e}")

    def ucitaj_xml(self):
        if not os.path.exists("clanovi.xml"):
            messagebox.showerror("Greška", "Datoteka clanovi.xml ne postoji!")
            return
        try:
            tree = ET.parse("clanovi.xml")
            root = tree.getroot()
            self.clanovi = []
            for clan_el in root.findall("clan"):
                ime = clan_el.find("ime").text or ""
                prezime = clan_el.find("prezime").text or ""
                kontakt = clan_el.find("kontakt").text or ""
                clan = Clan(ime, prezime, kontakt)
                clanarina_el = clan_el.find("clanarina")
                if clanarina_el is not None:
                    try:
                        datum = parse_date_str(clanarina_el.find("datum_uplate").text)
                        trajanje = int(clanarina_el.find("trajanje").text)
                        cijena = float(clanarina_el.find("cijena").text)
                        tip = clanarina_el.get("tip", "RedovnaClanarina")
                        if tip == "StudentskaClanarina":
                            clan.clanarina = StudentskaClanarina(datum, trajanje, cijena)
                        else:
                            clan.clanarina = RedovnaClanarina(datum, trajanje, cijena)
                    except Exception as e:
                        messagebox.showwarning("Upozorenje", f"Problem s podacima za člana {ime} {prezime}: {e}")
                self.clanovi.append(clan)
            self.prikazi_clanove()
            self.azuriraj_statusna_traku("Podaci učitani iz clanovi.xml.")
        except ET.ParseError as e:
            messagebox.showerror("Greška", f"Ne mogu parsirati XML datoteku: {e}")
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu učitati XML: {e}")

    def sort_tree(self, col, numeric=False):
        data = []
        for iid in self.tree.get_children():
            idx = int(self.tree.item(iid, "text"))
            vals = self.tree.item(iid, "values")
            data.append((iid, idx, vals))

        col_map = {"ime": 0, "prezime": 1, "status": 2, "istice": 3, "cijena": 4, "kontakt": 5}
        if col not in col_map:
            return
        key_index = col_map[col]

        def keyfn(item):
            v = item[2][key_index]
            if key_index == 3:  
                try:
                    return datetime.strptime(v, "%d.%m.%Y")
                except Exception:
                    return datetime.min
            if key_index == 4:  
                try:
                    return float(v) if v else 0.0
                except Exception:
                    return 0.0
            return v.lower() if isinstance(v, str) else v

        rev = self._sort_state.get(col, False)
        data.sort(key=keyfn, reverse=not rev)
        self._sort_state[col] = not rev


        for iid, idx, vals in data:
            self.tree.move(iid, "", "end")
        self.azuriraj_statusna_traku(f"Sortirano po: {col} {'silazno' if not rev else 'rastuce'}.")


    def prikazi_izvjestaje(self):
        total = 0.0
        active_count = 0
        for clan in self.clanovi:
            if clan.clanarina:
                try:
                    total += float(clan.clanarina.cijena)
                except Exception:
                    pass
                if clan.clanarina.aktivna():
                    active_count += 1

        top = tk.Toplevel(self.root)
        top.title("Izvještaji")
        top.configure(bg="#d8f3dc")

        tk.Label(top, text="Izvještaji - GreenFit", font=("TkDefaultFont", 12, "bold"), bg="#d8f3dc").grid(row=0, column=0, padx=12, pady=8)
        tk.Label(top, text=f"Ukupan prihod od članarina: {total:.2f} kn", bg="#d8f3dc").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        tk.Label(top, text=f"Broj aktivnih članova (danas): {active_count}", bg="#d8f3dc").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        tk.Button(top, text="Zatvori", command=top.destroy, bg="#95d5b2").grid(row=3, column=0, pady=12)

        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)

def main():
    root = tk.Tk()
    app = EvidencijaApp(root)
    if not TKCALENDAR_AVAILABLE:
        app.azuriraj_statusna_traku("Upozorenje: tkcalendar nije dostupan. Datum odabirete ručno (dd.mm.gggg) ili instalirajte tkcalendar (pip install tkcalendar).")
    root.mainloop()

if __name__ == "__main__":
    main()
