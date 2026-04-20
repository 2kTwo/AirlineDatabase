import customtkinter as ctk
from CLI import OpenFlightsCLI
 
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")
 
 
class OpenFlightsGUI(ctk.CTk):
    def __init__(self, cli: OpenFlightsCLI):
        super().__init__()
        self.cli = cli
        self.title("OpenFlights Explorer")
        self.geometry("900x560")
        self.resizable(True, True)
        self._build()
 
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
 
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
 
        self._build_airports_tab()
        self._build_airlines_tab()
        self._build_destinations_tab()
        self._build_routes_tab()
        self._build_country_tab()
        self._build_route_count_tab()
 
        # Shared status bar
        self.status = ctk.CTkLabel(self, text="", font=("", 12), text_color="gray")
        self.status.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 8))
 
    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
 
    def _make_tab(self, name):
        self.tabs.add(name)
        tab = self.tabs.tab(name)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        return tab
 
    def _make_search_row(self, parent, label, placeholder, width=260):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
 
        ctk.CTkLabel(row, text=label, font=("", 14, "bold")).pack(side="left", padx=(0, 12))
        entry = ctk.CTkEntry(row, placeholder_text=placeholder, width=width)
        entry.pack(side="left", padx=(0, 8))
        return row, entry
 
    def _make_textbox(self, parent):
        box = ctk.CTkTextbox(parent, font=("Courier", 13))
        box.grid(row=1, column=0, sticky="nsew")
        box.configure(state="disabled")
        return box
 
    def _write(self, box, lines, status_text=""):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", "\n".join(lines) if lines else "No results found.")
        box.configure(state="disabled")
        self.status.configure(text=status_text)
 
    # ------------------------------------------------------------------
    # Tab: Airports
    # ------------------------------------------------------------------
 
    def _build_airports_tab(self):
        tab = self._make_tab("Airports")
        row, self.ap_entry = self._make_search_row(tab, "Search airports", "Name, city, country or code")
        ctk.CTkButton(row, text="Search", command=self._search_airports, width=80).pack(side="left")
        self.ap_entry.bind("<Return>", lambda e: self._search_airports())
        self.ap_out = self._make_textbox(tab)
 
    def _search_airports(self):
        q = self.ap_entry.get().lower().strip()
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
        lines = [
            f'{a["iata"]:5} {a["icao"]:5}  {a["name"][:38]:38}  {a["city"]}, {a["country"]}'
            for a in hits
        ]
        n = len(hits)
        self._write(self.ap_out, lines, f"{n} result{'s' if n != 1 else ''}" if hits else "")
 
    # ------------------------------------------------------------------
    # Tab: Airlines
    # ------------------------------------------------------------------
 
    def _build_airlines_tab(self):
        tab = self._make_tab("Airlines")
        row, self.al_entry = self._make_search_row(tab, "Search airlines", "Airline name or country")
        ctk.CTkButton(row, text="Search", command=self._search_airlines, width=80).pack(side="left")
        self.al_entry.bind("<Return>", lambda e: self._search_airlines())
        self.al_out = self._make_textbox(tab)
 
    def _search_airlines(self):
        q = self.al_entry.get().lower().strip()
        if not q:
            return
        hits = [
            a for a in self.cli.airlines
            if q in a["name"].lower() or q in a["country"].lower()
        ]
        lines = [
            f'{a["iata"]:4}  {"[ACTIVE]" if a["active"] == "Y" else "[INACTIVE]":10}  {a["name"][:35]:35}  {a["country"]}'
            for a in hits
        ]
        n = len(hits)
        self._write(self.al_out, lines, f"{n} result{'s' if n != 1 else ''}" if hits else "")
 
    # ------------------------------------------------------------------
    # Tab: Destinations from airport
    # ------------------------------------------------------------------
 
    def _build_destinations_tab(self):
        tab = self._make_tab("Destinations")
        row, self.dest_entry = self._make_search_row(tab, "Destinations from", "Source IATA code (e.g. JFK)", width=160)
        ctk.CTkButton(row, text="List", command=self._list_destinations, width=80).pack(side="left")
        self.dest_entry.bind("<Return>", lambda e: self._list_destinations())
        self.dest_out = self._make_textbox(tab)
 
    def _list_destinations(self):
        code = self.dest_entry.get().upper().strip()
        if not code or code not in self.cli.routes_by_source:
            self._write(self.dest_out, [], "No routes found.")
            return
        destinations = sorted({r["destination"] for r in self.cli.routes_by_source[code]})
        lines = []
        for d in destinations:
            airport = self.cli.airport_by_code.get(d)
            if airport:
                lines.append(f'{d:5}  {airport["name"][:38]:38}  {airport["city"]}, {airport["country"]}')
            else:
                lines.append(d)
        n = len(destinations)
        self._write(self.dest_out, lines, f"{n} destination{'s' if n != 1 else ''} from {code}")
 
    # ------------------------------------------------------------------
    # Tab: Airlines between two airports
    # ------------------------------------------------------------------
 
    def _build_routes_tab(self):
        tab = self._make_tab("Routes")
        tab.grid_columnconfigure(0, weight=1)
 
        row = ctk.CTkFrame(tab, fg_color="transparent")
        row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
 
        ctk.CTkLabel(row, text="Airlines between airports", font=("", 14, "bold")).pack(side="left", padx=(0, 12))
        self.rt_from = ctk.CTkEntry(row, placeholder_text="From (e.g. LHR)", width=130)
        self.rt_from.pack(side="left", padx=(0, 6))
        ctk.CTkLabel(row, text="→").pack(side="left", padx=(0, 6))
        self.rt_to = ctk.CTkEntry(row, placeholder_text="To (e.g. JFK)", width=130)
        self.rt_to.pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="Find", command=self._search_routes, width=70).pack(side="left")
        self.rt_to.bind("<Return>", lambda e: self._search_routes())
 
        self.rt_out = self._make_textbox(tab)
 
    def _search_routes(self):
        src = self.rt_from.get().upper().strip()
        dst = self.rt_to.get().upper().strip()
        if not src or not dst:
            return
        airlines = set()
        for route in self.cli.routes_by_source.get(src, []):
            if route["destination"] == dst:
                airlines.add(route["airline"])
        if not airlines:
            self._write(self.rt_out, [], f"No direct routes from {src} to {dst}.")
            return
        lines = []
        for code in sorted(airlines):
            airline = self.cli.airlines_by_code.get(code)
            if airline:
                active = "[ACTIVE]" if airline["active"] == "Y" else "[INACTIVE]"
                lines.append(f'{code:4}  {active:10}  {airline["name"][:35]:35}  {airline["country"]}')
            else:
                lines.append(code)
        n = len(lines)
        self._write(self.rt_out, lines, f"{n} airline{'s' if n != 1 else ''} on {src} → {dst}")
 
    # ------------------------------------------------------------------
    # Tab: Airports in a country
    # ------------------------------------------------------------------
 
    def _build_country_tab(self):
        tab = self._make_tab("By Country")
        row, self.co_entry = self._make_search_row(tab, "Airports in", "Country name (e.g. Japan)", width=220)
        ctk.CTkButton(row, text="Search", command=self._search_country, width=80).pack(side="left")
        self.co_entry.bind("<Return>", lambda e: self._search_country())
        self.co_out = self._make_textbox(tab)
 
    def _search_country(self):
        country = self.co_entry.get().strip()
        if not country:
            return
        airports = self.cli.airports_by_country.get(country, [])
        lines = [
            f'{a["iata"]:5} {a["icao"]:5}  {a["name"][:38]:38}  {a["city"]}'
            for a in airports
        ]
        n = len(airports)
        self._write(self.co_out, lines, f"{n} airport{'s' if n != 1 else ''} in {country}" if airports else "")
 
    # ------------------------------------------------------------------
    # Tab: Airline route count
    # ------------------------------------------------------------------
 
    def _build_route_count_tab(self):
        tab = self._make_tab("Route Count")
        row, self.arc_entry = self._make_search_row(tab, "Airline routes", "IATA code (e.g. BA)", width=140)
        ctk.CTkButton(row, text="Lookup", command=self._airline_route_count, width=80).pack(side="left")
        self.arc_entry.bind("<Return>", lambda e: self._airline_route_count())
        self.arc_out = self._make_textbox(tab)
 
    def _airline_route_count(self):
        code = self.arc_entry.get().upper().strip()
        if not code:
            return
        count = sum(1 for r in self.cli.routes if r["airline"] == code)
        airline = self.cli.airlines_by_code.get(code)
        name = airline["name"] if airline else code
        country = airline["country"] if airline else ""
        lines = [
            f'Airline  : {name}',
            f'IATA     : {code}',
            f'Country  : {country}',
            f'Routes   : {count}',
        ]
        self._write(self.arc_out, lines, f"{count} route{'s' if count != 1 else ''} for {name}")
 
 
def main():
    cli = OpenFlightsCLI()
    cli.load_all()
    app = OpenFlightsGUI(cli)
    app.mainloop()
 
 
if __name__ == "__main__":
    main()