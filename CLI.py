import csv
from collections import defaultdict, Counter


class OpenFlightsCLI:

    def __init__(self):
        self.airports = []
        self.airlines = []
        self.routes = []
        self.cities = []

        self.city_by_id = {}
        self.airport_by_code = {}
        self.airports_by_country = defaultdict(list)
        self.routes_by_source = defaultdict(list)
        self.routes_by_destination = defaultdict(list)
        self.airlines_by_code = {}

    def load_cities(self):
        with open("cities.dat", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                city = {
                    "city_id": row[0],
                    "city": row[1],
                    "country": row[2],
                    "timezone": row[3],
                    "dst": row[4],
                    "tz": row[5]
                }

                self.cities.append(city)
                self.city_by_id[city["city_id"]] = city

    def load_airports(self):
        with open("airports.dat", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                city_info = self.city_by_id.get(row[2], {})

                airport = {
                    "id": row[0],
                    "name": row[1],
                    "city_id": row[2],
                    "city": city_info.get("city", "Unknown"),
                    "country": city_info.get("country", "Unknown"),
                    "timezone": city_info.get("timezone", ""),
                    "dst": city_info.get("dst", ""),
                    "tz": city_info.get("tz", ""),
                    "iata": row[3],
                    "icao": row[4]
                }

                self.airports.append(airport)

                if airport["iata"] != "\\N":
                    self.airport_by_code[airport["iata"]] = airport

                if airport["icao"] != "\\N":
                    self.airport_by_code[airport["icao"]] = airport

                self.airports_by_country[airport["country"]].append(airport)

    def load_airlines(self):
        with open("airlines.dat", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                airline = {
                    "id": row[0],
                    "name": row[1],
                    "country": row[6],
                    "iata": row[3],
                    "icao": row[4],
                    "active": row[7]
                }

                self.airlines.append(airline)

                if airline["iata"] != "\\N":
                    self.airlines_by_code[airline["iata"]] = airline

                if airline["icao"] != "\\N":
                    self.airlines_by_code[airline["icao"]] = airline

    def load_routes(self):
        with open("routes.dat", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                route = {
                    "airline": row[0],
                    "source": row[2],
                    "destination": row[4],
                    "stops": row[7],
                    "equipment": row[8],
                    "departure": row[-2],
                    "arrival": row[-1]
                }

                self.routes.append(route)
                self.routes_by_source[route["source"]].append(route)
                self.routes_by_destination[route["destination"]].append(route)

    def load_all(self):
        print("Loading data...")

        self.load_cities()
        self.load_airports()
        self.load_airlines()
        self.load_routes()

        print(f"{len(self.cities)} cities loaded")
        print(f"{len(self.airports)} airports loaded")
        print(f"{len(self.airlines)} airlines loaded")
        print(f"{len(self.routes)} routes loaded")

    def search_airports(self):
        query = input("Search airport city/name/code: ").lower()

        for airport in self.airports:
            if (
                query in airport["name"].lower()
                or query in airport["city"].lower()
                or query in airport["country"].lower()
                or query == airport["iata"].lower()
                or query == airport["icao"].lower()
            ):
                print(
                    f'{airport["name"]} | {airport["city"]}, {airport["country"]} '
                    f'| IATA: {airport["iata"]} | ICAO: {airport["icao"]}'
                )

    def search_airlines(self):
        query = input("Search airline name or country: ").lower()

        for airline in self.airlines:
            if query in airline["name"].lower() or query in airline["country"].lower():
                print(
                    f'{airline["name"]} | {airline["country"]} '
                    f'| IATA: {airline["iata"]} | Active: {airline["active"]}'
                )

    def list_destinations(self):
        code = input("Source airport code: ").upper()

        if code not in self.routes_by_source:
            print("No routes found.")
            return

        destinations = set()

        for route in self.routes_by_source[code]:
            destinations.add(route["destination"])

        print(f"\nDestinations from {code}:")
        for dest in sorted(destinations):
            print(dest)

        print(f"\nTotal destinations: {len(destinations)}")

    def airlines_between_airports(self):
        source = input("Source airport: ").upper()
        dest = input("Destination airport: ").upper()

        airlines = set()

        for route in self.routes_by_source[source]:
            if route["destination"] == dest:
                airlines.add(route["airline"])

        if not airlines:
            print("No routes found.")
            return

        print("\nAirlines flying this route:")

        for code in airlines:
            airline = self.airlines_by_code.get(code)
            if airline:
                print(airline["name"])
            else:
                print(code)

    def airports_in_country(self):
        country = input("Enter country name: ")

        airports = self.airports_by_country.get(country)

        if not airports:
            print("No airports found.")
            return

        for airport in airports:
            print(
                f'{airport["name"]} | {airport["city"]} '
                f'| IATA: {airport["iata"]}'
            )

        print(f"\nTotal airports: {len(airports)}")

    def airline_route_count(self):
        code = input("Enter airline IATA code: ").upper()

        count = 0

        for route in self.routes:
            if route["airline"] == code:
                count += 1

        airline = self.airlines_by_code.get(code)

        if airline:
            print(f'{airline["name"]} operates {count} routes')
        else:
            print(f"{code} operates {count} routes")

    def route_finder(self):
        source = input("Enter departure airport IATA code: ").upper()
        dest = input("Enter destination airport IATA code: ").upper()

        routes = []

        for route in self.routes_by_source[source]:
            if route["destination"] == dest and route["source"] == source:
                routes.append(route)

        if not routes:
            print("No routes found between airports")
            return
        
        print(f"\nFlights between {source} and {dest}:\n")

        for route in routes:
            print(route)
            print()

    def get_airport_name(self, code):
        airport = self.airport_by_code.get(code)
        if airport:
            return f'{airport["name"]} ({code})'
        return code

    def get_airline_name(self, code):
        airline = self.airlines_by_code.get(code)
        if airline:
            return airline["name"]
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

        departures = []
        arrivals = []

        airport_name = self.get_airport_name(code)

        for route in self.routes_by_source.get(code, []):
            departures.append({
                "airline": self.get_airline_name(route["airline"]),
                "from": airport_name,
                "to": self.get_airport_name(route["destination"]),
                "departure": route["departure"],
                "arrival": route["arrival"]
            })

        for route in self.routes_by_destination.get(code, []):
            arrivals.append({
                "airline": self.get_airline_name(route["airline"]),
                "from": self.get_airport_name(route["source"]),
                "to": airport_name,
                "departure": route["departure"],
                "arrival": route["arrival"]
            })

        print(f"\nAirport board for {airport_name}")

        if departures:
            self.print_board("DEPARTURES", departures[:20])
        else:
            print("\nNo departures found.")

        if arrivals:
            self.print_board("ARRIVALS", arrivals[:20])
        else:
            print("\nNo arrivals found.")

    def aircraft_count(self):
        iso = input("Enter country ISO code: ").upper().strip()

        country_name = None

        with open("countries.dat", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[1].upper() == iso:
                    country_name = row[0]
                    break

        if not country_name:
            print("Country ISO code not found.")
            return

        airports = self.airports_by_country.get(country_name)

        if not airports:
            print("No airports found for this country.")
            return

        airport_codes = {
            airport["iata"] for airport in airports
            if airport["iata"] != "\\N"
        }

        aircraft_counter = Counter()

        for route in self.routes:
            if route["source"] in airport_codes:
                equipment = route.get("equipment")

                if equipment and equipment != "\\N":
                    planes = equipment.split()

                    for plane in planes:
                        aircraft_counter[plane] += 1

        if not aircraft_counter:
            print("No aircraft data found.")
            return

        print(f"\nTop 3 aircraft used for flights from {country_name} ({iso}):\n")

        for aircraft, count in aircraft_counter.most_common(3):
            print(f"{aircraft} : {count} flights")

    def menu(self):

        while True:

            print("\n--- OpenFlights CLI ---")
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

            choice = input("Choose option: ")

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


def main():
    cli = OpenFlightsCLI()
    cli.load_all()
    cli.menu()


if __name__ == "__main__":
    main()