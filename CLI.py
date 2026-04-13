import csv
from collections import defaultdict


class OpenFlightsCLI:

    def __init__(self):
        self.airports = []
        self.airlines = []
        self.routes = []

        # Fast lookup structures
        self.airport_by_code = {}
        self.airports_by_country = defaultdict(list)
        self.routes_by_source = defaultdict(list)
        self.airlines_by_code = {}

    # --------------------
    # DATA LOADING
    # --------------------

    def load_airports(self):
        with open("airports.dat", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                airport = {
                    "id": row[0],
                    "name": row[1],
                    "city": row[2],
                    "country": row[3],
                    "iata": row[4],
                    "icao": row[5]
                }

                self.airports.append(airport)

                if airport["iata"] != "\\N":
                    self.airport_by_code[airport["iata"]] = airport

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

    def load_routes(self):
        with open("routes.dat", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                route = {
                    "airline": row[0],
                    "source": row[2],
                    "destination": row[4],
                    "stops": row[7]
                }

                self.routes.append(route)
                self.routes_by_source[route["source"]].append(route)

    def load_all(self):
        print("Loading data...")

        self.load_airports()
        self.load_airlines()
        self.load_routes()

        print(f"{len(self.airports)} airports loaded")
        print(f"{len(self.airlines)} airlines loaded")
        print(f"{len(self.routes)} routes loaded")

    # --------------------
    # SEARCH FUNCTIONS
    # --------------------

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

    # --------------------
    # CLI MENU
    # --------------------

    def menu(self):

        while True:

            print("\n--- OpenFlights CLI ---")
            print("1 Search airports")
            print("2 Search airlines")
            print("3 List destinations from airport")
            print("4 Airlines flying between two airports")
            print("5 Airports in a country")
            print("6 Airline route count")
            print("7 Exit")

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
                break

            else:
                print("Invalid option")


def main():
    cli = OpenFlightsCLI()
    cli.load_all()
    cli.menu()


if __name__ == "__main__":
    main()