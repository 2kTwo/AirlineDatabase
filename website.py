import customtkinter as ctk
from CLI import OpenFlightsCLI

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# Palette 
SIDEBAR_BG = "#0f1117"
HEADER_BG = "#13161f"
CONTENT_BG = "#181c27"
CARD_BG = "#1e2235"
ACCENT = "#4f9eff"
ACCENT2 = "#3de8b0"
ACCENT_DIM = "#1a3a5c"
TEXT_PRIMARY = "#e8edf8"
TEXT_MUTED = "#6b7a99"
TEXT_LABEL = "#9ba8c0"
ACTIVE_NAV = "#1e2a42"
BORDER = "#252c3f"

FONT_BODY = ("Segoe UI", 13)
FONT_MONO = ("Cascadia Code", 12)
FONT_LABEL = ("Segoe UI", 11)
FONT_HEADING = ("Segoe UI Semibold", 15)
FONT_SMALL = ("Segoe UI", 10)

NAV_ITEMS = [
    ("Airports", "airports"),
    ("Airlines", "airlines"),
    ("Destinations", "destinations"),
    ("Routes", "routes"),
    ("By Country", "country"),
    ("Route Count", "routecount"),
     ("Board", "board"),
    ("Aircraft", "aircraft")
]


class OpenFlightsGUI(ctk.CTk):
    def __init__(self, cli: OpenFlightsCLI):
        super().__init__()
        self.cli = cli
        self.title("Flights Explorer")
        self.geometry("1020x640")
        self.minsize(800, 500)
        self.configure(fg_color=CONTENT_BG)
        self._active_panel = None
        self._nav_buttons = {}
        self._panels = {}
        self._build()

    # Layout skeleton

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()
        self._switch("airports")

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width = 190, fg_color = SIDEBAR_BG, corner_radius = 0)
        sb.grid(row = 0, column = 0, sticky = "nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(10, weight=1)

        for i, (label, key) in enumerate(NAV_ITEMS):
            btn = ctk.CTkButton(
                sb, text = label, anchor = "w",
                font = FONT_BODY, height = 36,
                fg_color = "transparent", hover_color = ACTIVE_NAV,
                text_color = TEXT_LABEL, corner_radius = 8,
                command = lambda k = key: self._switch(k)
            )
            btn.grid(row = i + 3, column = 0, sticky = "ew", padx = 10, pady = 2)
            self._nav_buttons[key] = btn



    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color = CONTENT_BG, corner_radius = 0)
        main.grid(row = 0, column = 1, sticky = "nsew")
        main.grid_columnconfigure(0, weight = 1)
        main.grid_rowconfigure(1, weight = 1)

        # Header bar
        self._header = ctk.CTkFrame(main, height = 64, fg_color = HEADER_BG, corner_radius = 0)
        self._header.grid(row = 0, column = 0, sticky = "ew")
        self._header.grid_propagate(False)
        self._header_title = ctk.CTkLabel(
            self._header, text= "", font = FONT_HEADING, text_color = TEXT_PRIMARY)
        self._header_title.place(x = 24, rely = 0.35, anchor = "w")
        self._header_sub = ctk.CTkLabel(
            self._header, text = "", font = FONT_SMALL, text_color = TEXT_MUTED)
        self._header_sub.place(x = 24, rely = 0.72, anchor = "w")

        self._status_pill = ctk.CTkLabel(
            self._header, text= "", 
            font = ("Segoe UI", 11),
            text_color = ACCENT2, 
            fg_color = ACCENT_DIM,
            corner_radius = 10, 
            padx = 12, 
            pady = 3)
        self._status_pill.place(relx = 1.0, rely = 0.5, anchor = "e", x = -20)

        # Content
        self._content = ctk.CTkFrame(main, fg_color = CONTENT_BG, corner_radius = 0)
        self._content.grid(row = 1, column = 0, sticky = "nsew")
        self._content.grid_columnconfigure(0, weight = 1)
        self._content.grid_rowconfigure(0, weight = 1)

        self._panels["airports"] = self._make_airports_panel()
        self._panels["airlines"] = self._make_airlines_panel()
        self._panels["destinations"] = self._make_destinations_panel()
        self._panels["routes"] = self._make_routes_panel()
        self._panels["country"] = self._make_country_panel()
        self._panels["routecount"] = self._make_routecount_panel()
        self._panels["board"] = self._make_board_panel()
        self._panels["aircraft"] = self._make_aircraft_panel()

    # Navigation

    def _switch(self, key):
        if self._active_panel:
            self._active_panel.grid_remove()
        for k, btn in self._nav_buttons.items():
            btn.configure(
                fg_color=ACTIVE_NAV if k == key else "transparent",
                text_color=TEXT_PRIMARY if k == key else TEXT_LABEL
            )
        titles = {
            "airports": ("Search Airports", "You can search with name, city, country, IATA or ICAO code. All results shown have those letters in order."),
            "airlines": ("Search Airlines", "Search for letters in an airline name or country"),
            "destinations": ("Destinations", "Airports reachable from a given hub"),
            "routes": ("Routes Between Airports", "Airlines operating a specific city pair"),
            "country": ("Airports by Country", "All airports in a given country"),
            "routecount": ("Airline Route Count", "How many routes does an airline operate?"),
            "board": ("Arrivals / Departures", "Mock-live style board for any airport"),
            "aircraft": ("Aircraft by Country", "Top aircraft types used from a country's airports"),
        }
        title, sub = titles[key]
        self._header_title.configure(text = title)
        self._header_sub.configure(text = sub)
        self._status_pill.configure(text= "")
        panel = self._panels[key]
        panel.grid(row = 0, column = 0, sticky = "nsew")
        self._active_panel = panel

# Builders

    def _make_panel(self):
        p = ctk.CTkFrame(self._content, fg_color = CONTENT_BG, corner_radius = 0)
        p.grid_columnconfigure(0, weight = 1)
        p.grid_rowconfigure(1, weight = 1)
        return p

    def _make_search_bar(self, parent, *fields, btn_text = "Search", cmd = None):
        bar = ctk.CTkFrame(parent, fg_color = CARD_BG, corner_radius = 12, height = 56)
        bar.grid(row = 0, column = 0, sticky = "ew", padx = 20, pady = (16, 10))
        bar.grid_propagate(False)
        entries = []
        col = 0
        for item in fields:
            if isinstance(item, str):
                ctk.CTkLabel(bar, text = item, font = ("Segoe UI", 14),
                             text_color = TEXT_MUTED
                             ).grid(row = 0, column = col, padx = 6)
                col += 1
            else:
                placeholder, width = item
                e = ctk.CTkEntry(
                    bar, placeholder_text = placeholder, width = width,
                    font = FONT_BODY, fg_color = CONTENT_BG,
                    border_color = BORDER, border_width = 1,
                    text_color = TEXT_PRIMARY,
                    placeholder_text_color = TEXT_MUTED,
                    corner_radius = 8, height = 36
                )
                e.grid(row = 0, column = col,
                       padx = (12 if col == 0 else 4, 4), pady = 10)
                entries.append(e)
                col += 1
        ctk.CTkButton(
            bar, text = btn_text, 
            command = cmd,
            width = 90, 
            height = 36, 
            corner_radius = 8,
            font = ("Segoe UI Semibold", 13),
            fg_color = ACCENT, 
            hover_color = "#3a7fd4", 
            text_color ="#ffffff"
        ).grid(row = 0, column = col, padx = (4, 14), pady = 10)
        return entries

    def _make_results_box(self, parent):
        box = ctk.CTkTextbox(
            parent, font = FONT_MONO,
            fg_color = CARD_BG, text_color = TEXT_PRIMARY,
            border_width = 0, corner_radius = 12,
            scrollbar_button_color = BORDER,
            scrollbar_button_hover_color = ACCENT_DIM
        )
        box.grid(row = 1, column = 0, sticky = "nsew", padx = 20, pady = (0, 16))
        box.configure(state = "disabled")
        box.tag_config("code", foreground=ACCENT)
        box.tag_config("accent2",foreground=ACCENT2)
        box.tag_config("muted", foreground=TEXT_MUTED)
        box.tag_config("active", foreground="#3de8b0")
        box.tag_config("inactive",foreground="#e87070")
        box.tag_config("header", foreground=TEXT_MUTED)
        return box

    def _clear(self, box):
        box.configure(state = "normal")
        box.delete("1.0", "end")

    def _done(self, box):
        box.configure(state = "disabled")

    def _set_status(self, text):
        self._status_pill.configure(text = f"  {text}  " if text else "")

    # Airports

    def _make_airports_panel(self):
        p = self._make_panel()
        (self._ap_entry,) = self._make_search_bar(
            p, ("Name, city, country, IATA or ICAO...", 320),
            btn_text = "Search", cmd = self._search_airports)
        self._ap_entry.bind("<Return>", lambda e: self._search_airports())
        self._ap_box = self._make_results_box(p)
        return p

    def _search_airports(self):
        q = self._ap_entry.get().lower().strip()
        if not q:
            return
        hits = [a for a in self.cli.airports
                if q in a["name"].lower() or q in a["city"].lower()
                or q in a["country"].lower()
                or q == a["iata"].lower() or q == a["icao"].lower()]
        bx = self._ap_box
        self._clear(bx)
        if not hits:
            bx.insert("end", "  No airports found.", "muted")
        else:
            bx.insert("end", f"  {'IATA':<5}  {'ICAO':<5}  {'Airport':<38}  {'City':<22}  Country\n", "header")
            bx.insert("end", "  " + "-" * 88 + "\n", "muted")
            for a in hits:
                iata = a["iata"] if a["iata"] != "\\N" else "  — "
                icao = a["icao"] if a["icao"] != "\\N" else "  — "
                bx.insert("end", "  ")
                bx.insert("end", f"{iata:<5}", "code")
                bx.insert("end", f"  {icao:<5}  ")
                bx.insert("end", f"{a['name'][:36]:<38}", "accent2")
                bx.insert("end", f"  {a['city'][:20]:<22}  {a['country']}\n")
        self._done(bx)
        n = len(hits)
        self._set_status(f"{n} result{'s' if n!=1 else ''}" if hits else "")

    # Airlines

    def _make_airlines_panel(self):
        p = self._make_panel()
        (self._al_entry,) = self._make_search_bar(
            p, ("Airline name or country...", 300),
            btn_text = "Search", cmd = self._search_airlines)
        self._al_entry.bind("<Return>", lambda e: self._search_airlines())
        self._al_box = self._make_results_box(p)
        return p

    def _search_airlines(self):
        q = self._al_entry.get().lower().strip()
        if not q:
            return
        hits = [a for a in self.cli.airlines
                if q in a["name"].lower() or q in a["country"].lower()]
        bx = self._al_box
        self._clear(bx)
        if not hits:
            bx.insert("end", "  No airlines found.", "muted")
        else:
            bx.insert("end", f"  {'IATA':<5}  {'Status':<12}  {'Airline':<38}  Country\n", "header")
            bx.insert("end", "  " + "-" * 74 + "\n", "muted")
            for a in hits:
                iata   = a["iata"] if a["iata"] != "\\N" else " — "
                active = a["active"] == "Y"
                bx.insert("end", "  ")
                bx.insert("end", f"{iata:<5}", "code")
                bx.insert("end", "  ")
                bx.insert("end", f"{'active':<12}" if active else f"{'inactive':<12}",
                          "active" if active else "inactive")
                bx.insert("end", f"{a['name'][:36]:<38}  {a['country']}\n")
        self._done(bx)
        n = len(hits)
        self._set_status(f"{n} result{'s' if n!=1 else ''}" if hits else "")

    # Destinations

    def _make_destinations_panel(self):
        p = self._make_panel()
        (self._dest_entry,) = self._make_search_bar(
            p, ("Source IATA  (ex. CLE)", 200),
            btn_text = "List", cmd = self._list_destinations)
        self._dest_entry.bind("<Return>", lambda e: self._list_destinations())
        self._dest_box = self._make_results_box(p)
        return p

    def _list_destinations(self):
        code = self._dest_entry.get().upper().strip()
        bx = self._dest_box
        self._clear(bx)
        if not code or code not in self.cli.routes_by_source:
            bx.insert("end", "  No routes found for that code.", "muted")
            self._done(bx); return
        destinations = sorted({r["destination"] for r in self.cli.routes_by_source[code]})
        bx.insert("end", f"  {'IATA':<5}  {'Airport':<38}  {'City':<22}  Country\n", "header")
        bx.insert("end", "  " + "-" * 80 + "\n", "muted")
        for d in destinations:
            ap = self.cli.airport_by_code.get(d)
            bx.insert("end", "  ")
            bx.insert("end", f"{d:<5}", "code")
            if ap:
                bx.insert("end", f"  {ap['name'][:36]:<38}", "accent2")
                bx.insert("end", f"  {ap['city'][:20]:<22}  {ap['country']}\n")
            else:
                bx.insert("end", "  -\n", "muted")
        self._done(bx)
        n = len(destinations)
        self._set_status(f"{n} destination{'s' if n!=1 else ''} from {code}")

    # Routes

    def _make_routes_panel(self):
        p = self._make_panel()
        self._rt_from, self._rt_to = self._make_search_bar(
            p,
            ("From  (ex. LHR)", 160), "->", ("To  (ex. JFK)", 160),
            btn_text = "Find", cmd = self._search_routes)
        self._rt_to.bind("<Return>", lambda e: self._search_routes())
        self._rt_box = self._make_results_box(p)
        return p

    def _search_routes(self):
        src = self._rt_from.get().upper().strip()
        dst = self._rt_to.get().upper().strip()
        bx  = self._rt_box
        self._clear(bx)
        if not src or not dst:
            bx.insert("end", "  Enter both airport codes.", "muted")
            self._done(bx); return
        codes = {r["airline"] for r in self.cli.routes_by_source.get(src, [])
                 if r["destination"] == dst}
        if not codes:
            bx.insert("end", f"  No direct routes found from {src} to {dst}.", "muted")
            self._done(bx); self._set_status(""); return
        bx.insert("end", f"  {'Code':<5}  {'Status':<12}  {'Airline':<38}  Country\n", "header")
        bx.insert("end", "  " + "-" * 74 + "\n", "muted")
        for code in sorted(codes):
            al = self.cli.airlines_by_code.get(code)
            bx.insert("end", "  ")
            bx.insert("end", f"{code:<5}", "code")
            bx.insert("end", "  ")
            if al:
                active = al["active"] == "Y"
                bx.insert("end", f"{'active':<12}" if active else f"{'inactive':<12}",
                          "active" if active else "inactive")
                bx.insert("end", f"{al['name'][:36]:<38}  {al['country']}\n")
            else:
                bx.insert("end", f"{'-':<12}", "muted")
                bx.insert("end", "Unknown\n")
        self._done(bx)
        n = len(codes)
        self._set_status(f"{n} airline{'s' if n!=1 else ''} · {src} -> {dst}")

    # By Country

    def _make_country_panel(self):
        p = self._make_panel()
        (self._co_entry,) = self._make_search_bar(
            p, ("Country name  (e.x. Japan)", 260),
            btn_text = "Search", cmd = self._search_country)
        self._co_entry.bind("<Return>", lambda e: self._search_country())
        self._co_box = self._make_results_box(p)
        return p

    def _search_country(self):
        country = self._co_entry.get().strip()
        bx = self._co_box
        self._clear(bx)
        airports = self.cli.airports_by_country.get(country, [])
        if not airports:
            bx.insert("end", f"  No airports found for \"{country}\".", "muted")
            self._done(bx); return
        bx.insert("end", f"  {'IATA':<5}  {'ICAO':<5}  {'Airport':<38}  City\n", "header")
        bx.insert("end", "  " + "-" * 68 + "\n", "muted")
        for a in airports:
            iata = a["iata"] if a["iata"] != "\\N" else "  — "
            icao = a["icao"] if a["icao"] != "\\N" else "  — "
            bx.insert("end", "  ")
            bx.insert("end", f"{iata:<5}", "code")
            bx.insert("end", f"  {icao:<5}  ")
            bx.insert("end", f"{a['name'][:36]:<38}", "accent2")
            bx.insert("end", f"  {a['city']}\n")
        self._done(bx)
        n = len(airports)
        self._set_status(f"{n} airport{'s' if n!=1 else ''} in {country}")

    # Route Count

    def _make_routecount_panel(self):
        p = self._make_panel()
        (self._arc_entry,) = self._make_search_bar(
            p, ("Airline IATA code  (e.x. AA)", 220),
            btn_text = "Lookup", cmd = self._airline_route_count)
        self._arc_entry.bind("<Return>", lambda e: self._airline_route_count())
        self._arc_box = self._make_results_box(p)
        return p

    def _airline_route_count(self):
        code = self._arc_entry.get().upper().strip()
        bx   = self._arc_box
        self._clear(bx)
        if not code:
            self._done(bx); return
        count = sum(1 for r in self.cli.routes if r["airline"] == code)
        al = self.cli.airlines_by_code.get(code)
        name = al["name"]    if al else code
        country = al["country"] if al else "—"
        active = (al["active"] == "Y") if al else False

        bx.insert("end", "\n")
        bx.insert("end", "  Airline  ", "header"); bx.insert("end", f"{name}\n", "accent")
        bx.insert("end", "  IATA     ", "header"); bx.insert("end", f"{code}\n", "code")
        bx.insert("end", "  Country  ", "header"); bx.insert("end", f"{country}\n")
        bx.insert("end", "  Status   ", "header")
        if al:
            bx.insert("end", "Active\n" if active else "Inactive\n",
                      "active" if active else "inactive")
        bx.insert("end", "\n")
        bx.insert("end", "  Routes   ", "header")
        bx.insert("end", f"{count:,}\n", "accent")
        self._done(bx)
        self._set_status(f"{count:,} routes -- {name}")

    #arrival departure board
    def _make_board_panel(self):
        p = self._make_panel()
        (self._board_entry,) = self._make_search_bar(
            p, ("Airport code  (ex. JFK)", 200),
            btn_text = "Show", cmd = self._show_board)
        self._board_entry.bind("<Return>", lambda e: self._show_board())
        self._board_box = self._make_results_box(p)
        return p
 
    def _show_board(self):
        code = self._board_entry.get().upper().strip()
        bx = self._board_box
        self._clear(bx)
        if not code:
            self._done(bx); return
 
        ap_name = self.cli.get_airport_name(code)
 
        departures = [
            {
                "airline": self.cli.get_airline_name(r["airline"]),
                "to":      self.cli.get_airport_name(r["destination"]),
                "dep":     r["departure"],
                "arr":     r["arrival"],
            }
            for r in self.cli.routes_by_source.get(code, [])
        ]
        arrivals = [
            {
                "airline": self.cli.get_airline_name(r["airline"]),
                "from":    self.cli.get_airport_name(r["source"]),
                "dep":     r["departure"],
                "arr":     r["arrival"],
            }
            for r in self.cli.routes_by_destination.get(code, [])
        ]
 
        if not departures and not arrivals:
            bx.insert("end", f"  No routes found for {code}.", "muted")
            self._done(bx); return
 
        def section(title, rows, col_a, col_b, label_a, label_b):
            bx.insert("end", f"\n  {title}\n", "accent2")
            bx.insert("end", "  " + "─" * 80 + "\n", "muted")
            bx.insert("end", f"  {'Airline':<28}  {label_a:<32}  {'Dep':>6}  {'Arr':>6}\n", "header")
            bx.insert("end", "  " + "─" * 80 + "\n", "muted")
            for r in rows[:25]:
                bx.insert("end", "  ")
                bx.insert("end", f"{r['airline'][:26]:<28}", "accent2")
                bx.insert("end", f"  {r[col_b][:30]:<32}  ")
                bx.insert("end", f"{r['dep']:>6}  {r['arr']:>6}\n")
 
        if departures:
            section("DEPARTURES", departures, "to", "to", "To", "To")
        if arrivals:
            section("ARRIVALS",   arrivals,   "from", "from", "From", "From")
 
        self._done(bx)
        self._set_status(f"{len(departures)} departures · {len(arrivals)} arrivals · {ap_name}")

    #aircraft by country
    def _make_aircraft_panel(self):
        p = self._make_panel()
        (self._aircraft_entry,) = self._make_search_bar(
            p, ("Country ISO code  (ex. US, GB)", 260),
            btn_text = "Search", cmd = self._show_aircraft)
        self._aircraft_entry.bind("<Return>", lambda e: self._show_aircraft())
        self._aircraft_box = self._make_results_box(p)
        return p
 
    def _show_aircraft(self):
        from collections import Counter
        iso = self._aircraft_entry.get().upper().strip()
        bx  = self._aircraft_box
        self._clear(bx)
        if not iso:
            self._done(bx); return
 
        country_name = None
        try:
            import csv
            with open("countries.dat", encoding="utf-8") as f:
                for row in csv.reader(f):
                    if row[1].upper() == iso:
                        country_name = row[0]
                        break
        except FileNotFoundError:
            bx.insert("end", "  countries.dat not found.", "muted")
            self._done(bx); return
 
        if not country_name:
            bx.insert("end", f"  ISO code '{iso}' not found.", "muted")
            self._done(bx); return
 
        airports = self.cli.airports_by_country.get(country_name, [])
        airport_codes = {a["iata"] for a in airports if a["iata"] != "\\N"}
 
        counter = Counter()
        for route in self.cli.routes:
            if route["source"] in airport_codes:
                eq = route.get("equipment", "")
                if eq and eq != "\\N":
                    for plane in eq.split():
                        counter[plane] += 1
 
        if not counter:
            bx.insert("end", f"  No aircraft data found for {country_name}.", "muted")
            self._done(bx); return
 
        bx.insert("end", f"\n  Top aircraft from {country_name} ({iso})\n", "accent2")
        bx.insert("end", "  " + "-" * 40 + "\n", "muted")
        bx.insert("end", f"  {'Aircraft':<12}  {'Flights':>10}\n", "header")
        bx.insert("end", "  " + "-" * 40 + "\n", "muted")
        for aircraft, count in counter.most_common(10):
            bx.insert("end", "  ")
            bx.insert("end", f"{aircraft:<12}", "code")
            bx.insert("end", f"  {count:>10,}\n")
 
        self._done(bx)
        self._set_status(f"{len(counter)} aircraft types ~ {country_name}")

def main():
    cli = OpenFlightsCLI()
    cli.load_all()
    app = OpenFlightsGUI(cli)
    app.mainloop()
 
 
if __name__ == "__main__":
    main()