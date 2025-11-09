import tkinter as tk
from tkinter import messagebox, Menu
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os


class Clanarina:
    def __init__(self, datum_uplate, trajanje_mjeseci, cijena):
        self.datum_uplate = datum_uplate
        self.trajanje_mjeseci = trajanje_mjeseci
        self.cijena = cijena

    def datum_isteka(self):
        return self.datum_uplate + timedelta(days=30 * self.trajanje_mjeseci)

    def aktivna(self):
        return datetime.now().date() <= self.datum_isteka().date()


class RedovnaClanarina(Clanarina):
    pass


class StudentskaClanarina(Clanarina):
    def __init__(self, datum_uplate, trajanje_mjeseci, cijena):
        super().__init__(datum_uplate, trajanje_mjeseci, cijena * 0.8)


class Clan:
    def __init__(self, ime, prezime, kontakt):
        self.ime = ime
        self.prezime = prezime
        self.kontakt = kontakt
        self.clanarina = None

    def __str__(self):
        status = "AKTIVNA" if self.clanarina and self.clanarina.aktivna() else "ISTEKLA"
        return f"{self.ime} {self.prezime} - {status}"



class EvidencijaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GreenFit Evidencija 1.0")
        self.root.configure(bg="#d8f3dc")
        self.clanovi = []


        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Spremi (XML)", command=self.spremi_xml)
        file_menu.add_command(label="Učitaj (XML)", command=self.ucitaj_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Izlaz", command=self.izlaz)
        menu.add_cascade(label="Datoteka", menu=file_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="O aplikaciji", command=self.o_aplikaciji)
        menu.add_cascade(label="Pomoć", menu=help_menu)


        frame_clan = tk.LabelFrame(root, text="Unos člana", bg="#b7e4c7", fg="black")
        frame_clan.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(frame_clan, text="Ime:", bg="#b7e4c7").grid(row=0, column=0)
        tk.Label(frame_clan, text="Prezime:", bg="#b7e4c7").grid(row=1, column=0)
        tk.Label(frame_clan, text="Kontakt:", bg="#b7e4c7").grid(row=2, column=0)

        self.e_ime = tk.Entry(frame_clan)
        self.e_prezime = tk.Entry(frame_clan)
        self.e_kontakt = tk.Entry(frame_clan)

        self.e_ime.grid(row=0, column=1)
        self.e_prezime.grid(row=1, column=1)
        self.e_kontakt.grid(row=2, column=1)

        tk.Button(frame_clan, text="Dodaj člana", command=self.dodaj_clana, bg="#95d5b2").grid(row=3, columnspan=2, pady=5)


        frame_clanarina = tk.LabelFrame(root, text="Unos članarine", bg="#b7e4c7")
        frame_clanarina.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(frame_clanarina, text="Datum uplate (dd.mm.gggg):", bg="#b7e4c7").grid(row=0, column=0)
        tk.Label(frame_clanarina, text="Trajanje (mj):", bg="#b7e4c7").grid(row=1, column=0)
        tk.Label(frame_clanarina, text="Cijena:", bg="#b7e4c7").grid(row=2, column=0)

        self.e_datum = tk.Entry(frame_clanarina)
        self.e_trajanje = tk.Entry(frame_clanarina)
        self.e_cijena = tk.Entry(frame_clanarina)

        self.e_datum.grid(row=0, column=1)
        self.e_trajanje.grid(row=1, column=1)
        self.e_cijena.grid(row=2, column=1)

        tk.Button(frame_clanarina, text="Redovna članarina", command=lambda: self.dodaj_clanarinu("redovna"), bg="#95d5b2").grid(row=3, column=0, pady=5)
        tk.Button(frame_clanarina, text="Studentska članarina", command=lambda: self.dodaj_clanarinu("studentska"), bg="#95d5b2").grid(row=3, column=1, pady=5)


        frame_lista = tk.LabelFrame(root, text="Lista članova", bg="#b7e4c7")
        frame_lista.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.lista = tk.Listbox(frame_lista, width=45)
        self.lista.grid(row=0, column=0)

        tk.Button(frame_lista, text="Ažuriraj status", command=self.azuriraj_status, bg="#95d5b2").grid(row=1, column=0, pady=5)


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

        self.status = tk.Label(root, text="Dobrodošli u GreenFit Evidenciju!",
                               bd=1, relief=tk.SUNKEN, anchor="w", bg="#74c69d")
        self.status.grid(row=3, column=0, columnspan=2, sticky="we")


    def azuriraj_statusna_traku(self, tekst):
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
            "Verzija 1.0\n"
            "Autor: Antonio M.\n"
        )
        label_info = tk.Label(prozor, text=info_text, bg="#d8f3dc", fg="#000",
                              justify="left")
        label_info.pack(padx=20, pady=(0, 20))

        btn_ok = tk.Button(prozor, text="U redu", command=prozor.destroy, bg="#95d5b2")
        btn_ok.pack(pady=(0, 20))

        prozor.update_idletasks()
        w = prozor.winfo_width()
        h = prozor.winfo_height()
        ws = prozor.winfo_screenwidth()
        hs = prozor.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        prozor.geometry(f"{w}x{h}+{x}+{y}")

        prozor.transient(self.root)
        prozor.grab_set()
        self.root.wait_window(prozor)

    def dodaj_clana(self):
        ime = self.e_ime.get()
        prezime = self.e_prezime.get()
        kontakt = self.e_kontakt.get()


        if not ime or not prezime:
            messagebox.showerror("Greška", "Ime i prezime su obavezni!")
            return
        if not ime.isalpha() or not prezime.isalpha():
            messagebox.showerror("Greška", "Ime i prezime smiju sadržavati samo slova!")
            return


        novi_clan = Clan(ime, prezime, kontakt)
        self.clanovi.append(novi_clan)
        self.lista.insert(tk.END, str(novi_clan))
        self.lista.itemconfig(tk.END, {'fg': '#d00000'})

        self.e_ime.delete(0, tk.END)
        self.e_prezime.delete(0, tk.END)
        self.e_kontakt.delete(0, tk.END)
        self.azuriraj_statusna_traku("Član dodan (status ISTEKLA dok se ne ažurira).")

    def dodaj_clanarinu(self, tip):
        odabrani = self.lista.curselection()
        if not odabrani:
            messagebox.showwarning("Upozorenje", "Odaberi člana!")
            return

        clan = self.clanovi[odabrani[0]]
        try:
            unos_datuma = self.e_datum.get().strip()
            if unos_datuma.endswith('.'):
                unos_datuma = unos_datuma[:-1]  # makni točku ako je na kraju
            datum = datetime.strptime(unos_datuma, "%d.%m.%Y")
            trajanje = int(self.e_trajanje.get())
            cijena = float(self.e_cijena.get())
        except:
            messagebox.showerror("Greška", "Provjeri datum, trajanje i cijenu! (format: dd.mm.gggg)")
            return

        if tip == "redovna":
            clan.clanarina = RedovnaClanarina(datum, trajanje, cijena)
        else:
            clan.clanarina = StudentskaClanarina(datum, trajanje, cijena)

        self.e_datum.delete(0, tk.END)
        self.e_trajanje.delete(0, tk.END)
        self.e_cijena.delete(0, tk.END)
        self.azuriraj_statusna_traku("Članarina dodana (klikni 'Ažuriraj status').")

    def prikazi_clanove(self):
        self.lista.delete(0, tk.END)
        for clan in self.clanovi:
            self.lista.insert(tk.END, str(clan))
            if clan.clanarina and clan.clanarina.aktivna():
                self.lista.itemconfig(tk.END, {'fg': '#1b4332'})
            else:
                self.lista.itemconfig(tk.END, {'fg': '#d00000'})

    def azuriraj_status(self):
        self.prikazi_clanove()
        self.azuriraj_statusna_traku("Status članova ažuriran.")

    def spremi_xml(self):
        root = ET.Element("clanovi")
        for clan in self.clanovi:
            clan_el = ET.SubElement(root, "clan")
            ET.SubElement(clan_el, "ime").text = clan.ime
            ET.SubElement(clan_el, "prezime").text = clan.prezime
            ET.SubElement(clan_el, "kontakt").text = clan.kontakt

            if clan.clanarina:
                cl_el = ET.SubElement(clan_el, "clanarina")
                cl_el.set("tip", clan.clanarina.__class__.__name__)
                ET.SubElement(cl_el, "datum_uplate").text = clan.clanarina.datum_uplate.strftime("%d.%m.%Y")
                ET.SubElement(cl_el, "trajanje").text = str(clan.clanarina.trajanje_mjeseci)
                ET.SubElement(cl_el, "cijena").text = str(clan.clanarina.cijena)

        tree = ET.ElementTree(root)
        tree.write("clanovi.xml", encoding="utf-8", xml_declaration=True)
        self.azuriraj_statusna_traku("Podaci spremljeni u XML datoteku.")

    def ucitaj_xml(self):
        if not os.path.exists("clanovi.xml"):
            messagebox.showerror("Greška", "Datoteka clanovi.xml ne postoji!")
            return

        try:
            tree = ET.parse("clanovi.xml")
            root = tree.getroot()
            self.clanovi = []

            for clan_el in root.findall("clan"):
                ime = clan_el.find("ime").text
                prezime = clan_el.find("prezime").text
                kontakt = clan_el.find("kontakt").text
                clan = Clan(ime, prezime, kontakt)

                clanarina_el = clan_el.find("clanarina")
                if clanarina_el is not None:
                    datum = datetime.strptime(clanarina_el.find("datum_uplate").text, "%d.%m.%Y")
                    trajanje = int(clanarina_el.find("trajanje").text)
                    cijena = float(clanarina_el.find("cijena").text)
                    if clanarina_el.get("tip") == "StudentskaClanarina":
                        clan.clanarina = StudentskaClanarina(datum, trajanje, cijena)
                    else:
                        clan.clanarina = RedovnaClanarina(datum, trajanje, cijena)

                self.clanovi.append(clan)

            self.prikazi_clanove()
            self.azuriraj_statusna_traku("Podaci učitani iz XML datoteke.")
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu učitati XML: {e}")



if __name__ == "__main__":
    root = tk.Tk()
    app = EvidencijaApp(root)
    root.mainloop()

