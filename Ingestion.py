import os
import json
import requests


class WorldCupIngestion:

    def __init__(self, api_key, season=2022):

        self.api_key = api_key
        self.season = season

        self.base_url = "https://v3.football.api-sports.io/fixtures"

        self.headers = {
            "x-apisports-key": self.api_key
        }

        # FIFA World Cup
        self.league_id = 1

        # Local storage
        self.data_dir = "data"

        self.cache_file = (
            f"{self.data_dir}/world_cup_{self.season}_raw.json"
        )

    # ----------------------------------
    # Create data folder if needed
    # ----------------------------------

    def ensure_data_directory(self):

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    # ----------------------------------
    # Load local cached data
    # ----------------------------------

    def load_local_data(self):

        print(f"Loading cached data: {self.cache_file}")

        with open(
            self.cache_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # ----------------------------------
    # Save API response locally
    # ----------------------------------

    def save_local_data(self, fixtures):

        self.ensure_data_directory()

        with open(
            self.cache_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                fixtures,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"Saved cache: {self.cache_file}"
        )

    # ----------------------------------
    # Fetch from API
    # ----------------------------------

    def fetch_fixtures(self):

        print(
            f"Fetching World Cup {self.season} from API..."
        )

        params = {
            "league": self.league_id,
            "season": self.season
        }

        response = requests.get(
            self.base_url,
            headers=self.headers,
            params=params,
            timeout=30
        )

        if response.status_code != 200:

            raise Exception(
                f"API Error {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        fixtures = data["response"]

        print(
            f"Downloaded {len(fixtures)} fixtures"
        )

        return fixtures

    # ----------------------------------
    # Main pipeline
    # ----------------------------------

    def run(self, force_refresh=False):

        self.ensure_data_directory()

        # Use cache if available

        if (
            os.path.exists(self.cache_file)
            and not force_refresh
        ):

            return self.load_local_data()

        # Otherwise call API

        fixtures = self.fetch_fixtures()

        self.save_local_data(fixtures)

        return fixtures


# ----------------------------------
# Test script
# ----------------------------------

if __name__ == "__main__":

    API_KEY = "fb754d332cf4c51c9940300fe4b20398"

    ingestion = WorldCupIngestion(
        api_key=API_KEY,
        season=2022
    )

    fixtures = ingestion.run()

    print()
    print(
        f"Loaded {len(fixtures)} fixtures"
    )

    print()
    print("First fixture:")
    print(fixtures[0])