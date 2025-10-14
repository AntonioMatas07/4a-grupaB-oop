import tkinter as tk

#Faza1: Model Podataka (OOP temelj)
class ucenik:
    def __init__(self, ime, prezime, razred):
        self.ime = ime
        self.prezime = prezime
        self.razred = razred

    def __str__(self):
        return f"{self.prezime}, {self.ime} ({self.razred})"



#Faza2: Izrada Sučelja (GUI Layout)
class evidencijaapp:
    def __init__(self, root):
        self.root=root
        self.ucenici=[]
        self.odabrani_ucenik_index= None

        
        self.root.title("Evidencija učenika")
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

        tk.Label(unos_frame, text="Prezime:").grid(row=1, column=0, padx=5, pady=5, sticky="W")
        self.prezime_entry = tk.Entry(unos_frame)
        self.prezime_entry.grid(row=1, column=1, padx=5, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Razred:").grid(row=2, column=0, padx=5, pady=5, sticky="W")
        self.razred_entry = tk.Entry(unos_frame)
        self.razred_entry.grid(row=2, column=1, padx=5, pady=5, sticky="EW")


#Gumbi
        self.dodaj_gumb = tk.Button(unos_frame, text="Dodaj učenika")
        self.dodaj_gumb.grid(row=3, column=0, padx=5, pady=10)
        self.spremi_gumb = tk.Button(unos_frame, text="Spremi izmjene")
        self.spremi_gumb.grid(row=3, column=1, padx=5, pady=10, sticky="W")

#Listbox i scrollbar
        self.listbox = tk.Listbox(prikaz_frame)
        self.listbox.grid(row=0, column=0, sticky="NSEW")

        scrollbar = tk.Scrollbar(prikaz_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.listbox.config(yscrollcommand=scrollbar.set)

 

#Faza3: Implementacija Logike (Funkcionalnost)


#Dodavanje učenika
    def dodaj_ucenika(self):
        ime = self.ime_entry.get()
        prezime = self.prezime_entry.get()
        razred = self.razred_entry.get()

        if ime and prezime and razred:
            novi = ucenik(ime, prezime, razred)
            self.ucenici.append(novi)
            self.osvjezi_prikaz()

          
            self.ime_entry.delete(0, tk.END)
            self.prezime_entry.delete(0, tk.END)
            self.razred_entry.delete(0, tk.END)

#Osvježavanje prikaza
    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)
        for u in self.ucenici:
            self.listbox.insert(tk.END, str(u))

#Biranje učenika
    def odaberi_ucenika(self):
        odabrani = self.listbox.curselection()
        if not odabrani:
            return
        self.odabrani_ucenik_index = odabrani[0]
        u = self.ucenici[self.odabrani_ucenik_index]

        self.ime_entry.delete(0, tk.END)
        self.ime_entry.insert(0, u.ime)
        self.prezime_entry.delete(0, tk.END)
        self.prezime_entry.insert(0, u.prezime)
        self.razred_entry.delete(0, tk.END)
        self.razred_entry.insert(0, u.razred)

#Spremanje
    def spremi_izmjene(self):
        if self.odabrani_ucenik_index is None:
            return

        u = self.ucenici[self.odabrani_ucenik_index]
        u.ime = self.ime_entry.get()
        u.prezime = self.prezime_entry.get()
        u.razred = self.razred_entry.get()
        self.osvjezi_prikaz()


#Pokretanje
if __name__ == "__main__":
    root = tk.Tk()
    app = evidencijaapp(root)

    app.dodaj_gumb.config(command=app.dodaj_ucenika)
    app.spremi_gumb.config(command=app.spremi_izmjene)
    app.listbox.bind("<<ListboxSelect>>", lambda e: app.odaberi_ucenika())


    root.mainloop()


















