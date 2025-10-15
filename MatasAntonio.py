import tkinker as tk

class kontakt:
    def __init__(self, ime, email, telefon):
        self.ime=ime
        self.email=email
        self.telefon=telefon

    def __str__(self):
        return f"{self.ime}, {self.email}, {self.telefon}"

class imenikapp:
    def __init__(self, root):
        self.root=root
        self.kontakti=[]
        self.odabrani_kontakt_index= None

        
        self.root.title("Lista kontaktova")
        self.root.geometry("500x400")
        

#Konfiguracija responzivnosti glavnog prozora
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        

#Okviri
        unos_frame = tk.Frame(self.root, padx=10, pady=10)
        unos_frame.grid(row=0, column=0, sticky="EW") 

        prikaz_frame = tk.Frame(self.root, padx=10, pady=10)
        prikaz_frame.grid(row=1, column=0, sticky="NSEW") 

        prikaz_frame.columnconfigure(0, weight=1)
        prikaz_frame.rowconfigure(0, weight=1)


#Dodavanje widgeta u okvir
        tk.Label(unos_frame, text="Ime:").grid(row=0, column=0, padx=5, pady=5, sticky="W")
        self.ime_entry = tk.Entry(unos_frame)
        self.ime_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="W")
        self.email_entry = tk.Entry(unos_frame)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Telefon:").grid(row=2, column=0, padx=5, pady=5, sticky="W")
        self.telefon_entry = tk.Entry(unos_frame)
        self.telefon_entry.grid(row=2, column=1, padx=5, pady=5, sticky="EW")


#Gumbi
        self.dodaj_gumb = tk.Button(unos_frame, text="Spremi kontakt")
        self.dodaj_gumb.grid(row=3, column=0, padx=5, pady=10)
        self.spremi_gumb = tk.Button(unos_frame, text="Učitaj kontakt")
        self.spremi_gumb.grid(row=3, column=1, padx=5, pady=10, sticky="W")

#Listbox i scrollbar
        self.listbox = tk.Listbox(prikaz_frame)
        self.listbox.grid(row=0, column=0, sticky="NSEW")

        scrollbar = tk.Scrollbar(prikaz_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.listbox.config(yscrollcommand=scrollbar.set)


        


#Dodavanje učenika
    def dodaj_kontakt(self):
        ime = self.ime_entry.get()
        email = self.email_entry.get()
        telefon = self.telefon_entry.get()

        if ime and email and telefon:
            novi = kontakt(ime, email, telefon)
            self.kontakti.append(novi)
            self.osvjezi_prikaz()

          
            self.ime_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.telefon_entry.delete(0, tk.END)

#Osvježavanje prikaza
    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)
        for u in self.kontakti:
            self.listbox.insert(tk.END, str(u))


#Biranje učenika
    def odaberi_kontakt(self):
        odabrani = self.listbox.curselection()
        if not odabrani:
            return
        self.odabrani_kontakt_index = odabrani[0]
        u = self.kontakti[self.odabrani_ucenik_index]

        self.ime_entry.delete(0, tk.END)
        self.ime_entry.insert(0, u.ime)
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, u.email)
        self.telefon_entry.delete(0, tk.END)
        self.telefon_entry.insert(0, u.telefon)

#Spremanje
    def spremi_izmjene(self):
        if self.odabrani_kontakt_index is None:
            return

        u = self.kontakti[self.odabrani_kontakt_index]
        u.ime = self.ime_entry.get()
        u.email = self.email_entry.get()
        u.telefon = self.telefon_entry.get()
        self.osvjezi_prikaz()








if __name__ == "__main__":
    root=tk.Tk()
    app = imenikapp(root)

    app.dodaj_gumb.config(command=app.spremi_kontakte)
    app.spremi_gumb.config(command=app.učitaj_kontakte)
    app.listbox.bind("<<ListboxSelect>>", lambda e: app.odaberi_kontakt())
    
    root.mainloop()






    
        
