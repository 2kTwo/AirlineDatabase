import csv
import sqlite3


class OpenFlightsSQLCLI:

    def __init__(self, db_name="openflights.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.executescript("""
            DROP TABLE IF EXISTS Routes;
            DROP TABLE IF EXISTS Airports;
            DROP TABLE IF EXISTS Airlines;
            DROP TABLE IF EXISTS Cities;
            DROP TABLE IF EXISTS Countries;

            CREATE TABLE Cities (
                city_id TEXT PRIMARY KEY,
                city TEXT,
                country TEXT,
                timezone TEXT,
                dst TEXT,
                tz TEXT
            );

            CREATE TABLE Airports (
                id TEXT PRIMARY KEY,
                name TEXT,
                city_id TEXT,
                iata TEXT,
                icao TEXT,
                FOREIGN KEY (city_id) REFERENCES Cities(city_id)
            );

            CREATE TABLE Airlines (
                id TEXT PRIMARY KEY,
                name TEXT,
                alias TEXT,
                iata TEXT,
                icao TEXT,
                callsign TEXT,
                country TEXT,
                active TEXT
            );

            CREATE TABLE Countries (
                name TEXT,
                iso_code TEXT PRIMARY KEY,
                dafif_code TEXT
            );

            CREATE TABLE Routes (
                airline TEXT,
                airline_id TEXT,
                source TEXT,
                source_id TEXT,
                destination TEXT,
                destination_id TEXT,
                codeshare TEXT,
                stops INTEGER,
                equipment TEXT,
                departure TEXT,
                arrival TEXT
            );
        """)

        self.conn.commit()

    def create_indexes(self):
        self.cursor.executescript("""
            CREATE INDEX IF NOT EXISTS idx_airports_iata ON Airports(iata);
            CREATE INDEX IF NOT EXISTS idx_airports_icao ON Airports(icao);
            CREATE INDEX IF NOT EXISTS idx_airports_city_id ON Airports(city_id);

            CREATE INDEX IF NOT EXISTS idx_airlines_iata ON Airlines(iata);
            CREATE INDEX IF NOT EXISTS idx_airlines_icao ON Airlines(icao);

            CREATE INDEX IF NOT EXISTS idx_routes_source ON Routes(source);
            CREATE INDEX IF NOT EXISTS idx_routes_destination ON Routes(destination);
            CREATE INDEX IF NOT EXISTS idx_routes_airline ON Routes(airline);

            CREATE INDEX IF NOT EXISTS idx_cities_country ON Cities(country);
            CREATE INDEX IF NOT EXISTS idx_countries_iso ON Countries(iso_code);
        """)

        self.conn.commit()

    def load_cities(self):
        rows = []

        with open("cities.dat", encoding="utf-8") as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) < 6:
                    continue

                rows.append((
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5]
                ))

        self.cursor.executemany("""
            INSERT INTO Cities
            (city_id, city, country, timezone, dst, tz)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rows)

    def load_airports(self):
        rows = []

        with open("airports.dat", encoding="utf-8") as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) < 5:
                    continue

                rows.append((
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4]
                ))

        self.cursor.executemany("""
            INSERT INTO Airports
            (id, name, city_id, iata, icao)
            VALUES (?, ?, ?, ?, ?)
        """, rows)

    def load_airlines(self):
        rows = []

        with open("airlines.dat", encoding="utf-8") as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) < 8:
                    continue

                rows.append((
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7]
                ))

        self.cursor.executemany("""
            INSERT INTO Airlines
            (id, name, alias, iata, icao, callsign, country, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)

    def load_countries(self):
        rows = []
        seen_iso_codes = set()

        with open("countries.dat", encoding="utf-8") as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) < 3:
                    continue

                name = row[0].strip()
                iso_code = row[1].strip().upper()
                dafif_code = row[2].strip()

                # Skip header row if it exists
                if iso_code == "ISO_CODE":
                    continue

                # Skip blank or duplicate ISO codes
                if not iso_code or iso_code in seen_iso_codes:
                    continue

                seen_iso_codes.add(iso_code)

                rows.append((
                    name,
                    iso_code,
                    dafif_code
                ))

        self.cursor.executemany("""
            INSERT OR IGNORE INTO Countries
            (name, iso_code, dafif_code)
            VALUES (?, ?, ?)
        """, rows)

    def load_routes(self):
        rows = []

        with open("routes.dat", encoding="utf-8") as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) < 11:
                    continue

                rows.append((
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[-2],
                    row[-1]
                ))

        self.cursor.executemany("""
            INSERT INTO Routes
            (
                airline,
                airline_id,
                source,
                source_id,
                destination,
                destination_id,
                codeshare,
                stops,
                equipment,
                departure,
                arrival
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)

    def load_all(self):
        print("Creating database tables...")
        self.create_tables()

        print("Loading data...")

        self.load_cities()
        self.load_airports()
        self.load_airlines()
        self.load_countries()
        self.load_routes()

        self.conn.commit()
        self.create_indexes()

        print("Data loaded into SQLite database.")

    def search_airports(self):
        query = input("Search airport city/name/code: ").lower().strip()

        self.cursor.execute("""
            SELECT
                Airports.name,
                Cities.city,
                Cities.country,
                Airports.iata,
                Airports.icao
            FROM Airports
            JOIN Cities
                ON Airports.city_id = Cities.city_id
            WHERE LOWER(Airports.name) LIKE ?
               OR LOWER(Cities.city) LIKE ?
               OR LOWER(Cities.country) LIKE ?
               OR LOWER(Airports.iata) = ?
               OR LOWER(Airports.icao) = ?
            ORDER BY Airports.name
            LIMIT 25;
        """, (
            f"%{query}%",
            f"%{query}%",
            f"%{query}%",
            query,
            query
        ))

        rows = self.cursor.fetchall()

        if not rows:
            print("No airports found.")
            return

        for name, city, country, iata, icao in rows:
            print(f"{name} | {city}, {country} | IATA: {iata} | ICAO: {icao}")

    def search_airlines(self):
        query = input("Search airline name or country: ").lower().strip()

        self.cursor.execute("""
            SELECT name, country, iata, active
            FROM Airlines
            WHERE LOWER(name) LIKE ?
               OR LOWER(country) LIKE ?
            ORDER BY name
            LIMIT 25;
        """, (
            f"%{query}%",
            f"%{query}%"
        ))

        rows = self.cursor.fetchall()

        if not rows:
            print("No airlines found.")
            return

        for name, country, iata, active in rows:
            print(f"{name} | {country} | IATA: {iata} | Active: {active}")

    def list_destinations(self):
        code = input("Source airport code: ").upper().strip()

        self.cursor.execute("""
            SELECT DISTINCT destination
            FROM Routes
            WHERE source = ?
            ORDER BY destination;
        """, (code,))

        rows = self.cursor.fetchall()

        if not rows:
            print("No routes found.")
            return

        print(f"\nDestinations from {code}:")

        for destination in rows:
            print(destination[0])

        print(f"\nTotal destinations: {len(rows)}")

    def airlines_between_airports(self):
        source = input("Source airport: ").upper().strip()
        destination = input("Destination airport: ").upper().strip()

        self.cursor.execute("""
            SELECT DISTINCT
                COALESCE(Airlines.name, Routes.airline) AS airline_name
            FROM Routes
            LEFT JOIN Airlines
                ON Routes.airline = Airlines.iata
                OR Routes.airline = Airlines.icao
            WHERE Routes.source = ?
              AND Routes.destination = ?
            ORDER BY airline_name;
        """, (source, destination))

        rows = self.cursor.fetchall()

        if not rows:
            print("No routes found.")
            return

        print("\nAirlines flying this route:")

        for airline_name in rows:
            print(airline_name[0])

    def airports_in_country(self):
        country = input("Enter country name: ").strip()

        self.cursor.execute("""
            SELECT
                Airports.name,
                Cities.city,
                Airports.iata
            FROM Airports
            JOIN Cities
                ON Airports.city_id = Cities.city_id
            WHERE Cities.country = ?
            ORDER BY Airports.name;
        """, (country,))

        rows = self.cursor.fetchall()

        if not rows:
            print("No airports found.")
            return

        for name, city, iata in rows:
            print(f"{name} | {city} | IATA: {iata}")

        print(f"\nTotal airports: {len(rows)}")

    def airline_route_count(self):
        code = input("Enter airline IATA code: ").upper().strip()

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM Routes
            WHERE airline = ?;
        """, (code,))

        count = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT name
            FROM Airlines
            WHERE iata = ?
               OR icao = ?
            LIMIT 1;
        """, (code, code))

        result = self.cursor.fetchone()

        if result:
            print(f"{result[0]} operates {count} routes")
        else:
            print(f"{code} operates {count} routes")

    def route_finder(self):
        source = input("Enter departure airport IATA code: ").upper().strip()
        destination = input("Enter destination airport IATA code: ").upper().strip()

        self.cursor.execute("""
            SELECT
                COALESCE(Airlines.name, Routes.airline) AS airline_name,
                Routes.source,
                Routes.destination,
                Routes.stops,
                Routes.equipment,
                Routes.departure,
                Routes.arrival
            FROM Routes
            LEFT JOIN Airlines
                ON Routes.airline = Airlines.iata
                OR Routes.airline = Airlines.icao
            WHERE Routes.source = ?
              AND Routes.destination = ?
            ORDER BY Routes.departure;
        """, (source, destination))

        rows = self.cursor.fetchall()

        if not rows:
            print("No routes found between airports.")
            return

        print(f"\nFlights between {source} and {destination}:\n")

        for airline_name, src, dest, stops, equipment, departure, arrival in rows:
            print(f"Airline: {airline_name}")
            print(f"Route: {src} -> {dest}")
            print(f"Stops: {stops}")
            print(f"Equipment: {equipment}")
            print(f"Departure: {departure}")
            print(f"Arrival: {arrival}")
            print()

    def get_airport_name(self, code):
        self.cursor.execute("""
            SELECT name
            FROM Airports
            WHERE iata = ?
               OR icao = ?
            LIMIT 1;
        """, (code, code))

        row = self.cursor.fetchone()

        if row:
            return f"{row[0]} ({code})"

        return code

    def print_board(self, title, rows):
        print("\n" + "=" * 110)
        print(title.center(110))
        print("=" * 110)
        print(f'{"Airline":25} {"From":25} {"To":25} {"Departure":12} {"Arrival":12}')
        print("-" * 110)

        for row in rows:
            print(
                f'{row["airline"][:25]:25} '
                f'{row["from"][:25]:25} '
                f'{row["to"][:25]:25} '
                f'{row["departure"]:12} '
                f'{row["arrival"]:12}'
            )

        print("=" * 110)

    def board_maker(self):
        code = input("Enter airport code:\n").upper().strip()

        airport_name = self.get_airport_name(code)

        self.cursor.execute("""
            SELECT
                COALESCE(Airlines.name, Routes.airline) AS airline_name,
                Routes.destination,
                Routes.departure,
                Routes.arrival
            FROM Routes
            LEFT JOIN Airlines
                ON Routes.airline = Airlines.iata
                OR Routes.airline = Airlines.icao
            WHERE Routes.source = ?
            ORDER BY Routes.departure
            LIMIT 20;
        """, (code,))

        departure_rows = self.cursor.fetchall()

        departures = []

        for airline_name, destination, departure, arrival in departure_rows:
            departures.append({
                "airline": airline_name,
                "from": airport_name,
                "to": self.get_airport_name(destination),
                "departure": departure,
                "arrival": arrival
            })

        self.cursor.execute("""
            SELECT
                COALESCE(Airlines.name, Routes.airline) AS airline_name,
                Routes.source,
                Routes.departure,
                Routes.arrival
            FROM Routes
            LEFT JOIN Airlines
                ON Routes.airline = Airlines.iata
                OR Routes.airline = Airlines.icao
            WHERE Routes.destination = ?
            ORDER BY Routes.arrival
            LIMIT 20;
        """, (code,))

        arrival_rows = self.cursor.fetchall()

        arrivals = []

        for airline_name, source, departure, arrival in arrival_rows:
            arrivals.append({
                "airline": airline_name,
                "from": self.get_airport_name(source),
                "to": airport_name,
                "departure": departure,
                "arrival": arrival
            })

        print(f"\nAirport board for {airport_name}")

        if departures:
            self.print_board("DEPARTURES", departures)
        else:
            print("\nNo departures found.")

        if arrivals:
            self.print_board("ARRIVALS", arrivals)
        else:
            print("\nNo arrivals found.")

    def aircraft_count(self):
        iso = input("Enter country ISO code: ").upper().strip()

        self.cursor.execute("""
            SELECT Countries.name
            FROM Countries
            WHERE UPPER(TRIM(Countries.iso_code)) = ?
            LIMIT 1;
        """, (iso,))

        country_row = self.cursor.fetchone()

        if not country_row:
            print("Country ISO code not found.")

            # Debug help: show a few ISO codes that actually exist
            self.cursor.execute("""
                SELECT iso_code, name
                FROM Countries
                LIMIT 10;
            """)
            sample_rows = self.cursor.fetchall()

            print("\nSample ISO codes loaded:")
            for code, name in sample_rows:
                print(f"{code} - {name}")

            return

        country_name = country_row[0]

        self.cursor.execute("""
            SELECT
                Routes.equipment,
                COUNT(*) AS usage
            FROM Routes
            JOIN Airports
                ON Routes.source = Airports.iata
            JOIN Cities
                ON Airports.city_id = Cities.city_id
            JOIN Countries
                ON Cities.country = Countries.name
            WHERE UPPER(TRIM(Countries.iso_code)) = ?
            AND Routes.equipment IS NOT NULL
            AND Routes.equipment <> ''
            AND Routes.equipment <> '\\N'
            GROUP BY Routes.equipment
            ORDER BY usage DESC
            LIMIT 3;
        """, (iso,))

        rows = self.cursor.fetchall()

        if not rows:
            print(f"No aircraft data found for {country_name} ({iso}).")
            return

        print(f"\nTop 3 aircraft used for flights from {country_name} ({iso}):\n")

        for equipment, usage in rows:
            print(f"{equipment}: {usage} flights")

    def menu(self):
        while True:
            print("\n--- SQLite OpenFlights CLI ---")
            print("1 Search airports")
            print("2 Search airlines")
            print("3 List destinations from airport")
            print("4 Airlines flying between two airports")
            print("5 Airports in a country")
            print("6 Airline route count")
            print("7 Flight finder")
            print("8 Arrivals/Departures board")
            print("9 Aircraft by country")
            print("0 Exit")

            choice = input("Choose option: ").strip()

            if choice == "1":
                self.search_airports()

            elif choice == "2":
                self.search_airlines()

            elif choice == "3":
                self.list_destinations()

            elif choice == "4":
                self.airlines_between_airports()

            elif choice == "5":
                self.airports_in_country()

            elif choice == "6":
                self.airline_route_count()

            elif choice == "7":
                self.route_finder()

            elif choice == "8":
                self.board_maker()

            elif choice == "9":
                self.aircraft_count()

            elif choice == "0":
                break

            else:
                print("Invalid option")

    def close(self):
        self.conn.close()


def main():
    cli = OpenFlightsSQLCLI()

    rebuild = input("Rebuild SQLite database from .dat files? y/n: ").lower().strip()

    if rebuild == "y":
        cli.load_all()
    else:
        print("Using existing openflights.db")

    try:
        cli.menu()
    finally:
        cli.close()


if __name__ == "__main__":
    main()