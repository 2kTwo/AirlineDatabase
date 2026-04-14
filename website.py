import customtkinter as ctk
from CLI import OpenFlightsCLI

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class OpenFlightsGUI(ctk.CTk):
    def __init__(self, cli: OpenFlightsCLI):
        super().__init__()
        self.cli = cli
        self.title("OpenFlights")
        self.geometry("750x480")
        self.resizable(True, True)
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Search
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        ctk.CTkLabel(top, text="Search airports", font=("", 16, "bold")).pack(side="left", padx=(0, 16))
        self.entry = ctk.CTkEntry(top, placeholder_text="Name, city, country or code", width=280)
        self.entry.pack(side="left", padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self._search())
        ctk.CTkButton(top, text="Search", command=self._search, width=80).pack(side="left")

        # Output
        self.out = ctk.CTkTextbox(self, font=("Courier", 13))
        self.out.grid(row=1, column=0, sticky="nswe", padx=16, pady=(0, 16))
        self.out.configure(state="disabled")

        # Status
        self.status = ctk.CTkLabel(self, text="", font=("", 12), text_color="gray")
        self.status.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 8))

    def _search(self):
        q = self.entry.get().lower().strip()
        if not q:
            return
        
        
        hits = [
            a for a in self.cli.airports
            if q in a["name"].lower()
            or q in a["city"].lower()
            or q in a["country"].lower()
            or q == a["iata"].lower()
            or q == a["icao"].lower()
        ]

        self.out.configure(state="normal")
        self.out.delete("1.0", "end")

        for a in hits:
            self.out.insert("end", f'{a["iata"]:5} {a["icao"]:5}  {a["name"]:40}  {a["city"]}, {a["country"]}\n')

        if not hits:
            self.out.insert("end", "No results found.")

        self.out.configure(state="disabled")
        self.status.configure(text=f"{len(hits)} result{'s' if len(hits) != 1 else ''}" if hits else "")


def main():
    cli = OpenFlightsCLI()
    cli.load_all()
    app = OpenFlightsGUI(cli)
    app.mainloop()


if __name__ == "__main__":
    main()