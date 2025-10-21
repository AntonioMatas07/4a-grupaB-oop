
import tkinter as tk
import csv
import os


class Kontakt:
    def __init__(self, ime, email, telefon):
        self.ime = ime
        self.email = email
        self.telefon = telefon

    def __str__(self):
        return f"{self.ime} - {self.email} ({self.telefon})"


class ImenikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jednostavni digitalni imenik")

        self.kontakti = [] 

        
        tk.Label(root, text="Ime i prezime:").grid(row=0, column=0)
        tk.Label(root, text="Email:").grid(row=1, column=0)
        tk.Label(root, text="Telefon:").grid(row=2, column=0)

        self.entry_ime = tk.Entry(root)
        self.entry_email = tk.Entry(root)
        self.entry_telefon = tk.Entry(root)

        self.entry_ime.grid(row=0, column=1)
        self.entry_email.grid(row=1, column=1)
        self.entry_telefon.grid(row=2, column=1)

        tk.Button(root, text="Dodaj kontakt", command=self.dodaj_kontakt).grid(row=3, column=0, columnspan=2, pady=5)

        
        self.listbox = tk.Listbox(root, width=40, height=10)
        self.listbox.grid(row=4, column=0, columnspan=2, pady=5)

        
        tk.Button(root, text="Spremi kontakte", command=self.spremi_kontakte).grid(row=5, column=0, pady=5)
        tk.Button(root, text="Učitaj kontakte", command=self.ucitaj_kontakte).grid(row=5, column=1, pady=5)

        
        self.ucitaj_kontakte()

    def dodaj_kontakt(self):
        ime = self.entry_ime.get().strip()
        email = self.entry_email.get().strip()
        telefon = self.entry_telefon.get().strip()


        if not (ime and email and telefon):
            print("Sva polja moraju biti popunjena")
            return

        if len(ime)<=2:
            print("Ime mora imati najmanje 3 slova")
            return
        
       
        if "@" not in email:
            print("Email mora sadržavati znak @")
            return
        
        if ".com" not in email and "skole.hr" not in email and ".hr" not in email:
            print("Nedostaju potrebni znakovi")
            return



        
        if not (telefon.isdigit() and len(telefon.replace(" ",""))==10):
            print("Broj mora sadržavati 10 znakova")
            return

        if ime and email and telefon:
            kontakt = Kontakt(ime, email, telefon)
            self.kontakti.append(kontakt)
            self.osvjezi_prikaz()
            self.entry_ime.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_telefon.delete(0, tk.END)





    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)
        for k in self.kontakti:
            self.listbox.insert(tk.END, str(k))

    def spremi_kontakte(self):
        f = open("kontakti.csv", "w", newline="", encoding="utf-8")
        writer = csv.writer(f)
        for k in self.kontakti:
            writer.writerow([k.ime, k.email, k.telefon])
        f.close()
        self.osvjezi_prikaz()
        
    def ucitaj_kontakte(self):
        """Učitaj kontakte samo ako datoteka postoji."""
        self.kontakti.clear()
        if "kontakti.csv" in os.listdir():
            f = open("kontakti.csv", "r", encoding="utf-8")
            reader = csv.reader(f)
            for red in reader:
                if len(red) == 3:
                    ime, email, telefon = red
                    self.kontakti.append(Kontakt(ime, email, telefon))
            f.close()
            self.osvjezi_prikaz()


root = tk.Tk()
app = ImenikApp(root)
root.mainloop()

