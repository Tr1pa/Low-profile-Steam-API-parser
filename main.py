# ------------------ imports ----------------------
# Here are the guides I used:
# https://andorei.github.io/learnwithpython.ru2e/ch17.html
# https://python-scripts.com/requests
# https://qna.habr.com/q/1119460
# https://habr.com/ru/articles/754400/
import requests
import time
import os
import sqlite3
from colorama import init, Fore, Style
init()
clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')
# ------------------ stack ------------------------
class SteamDB_API:
    def __init__(self, api_key: str, db_name="steamapiparser.db"):
        if not api_key: raise ValueError("API ключ не может быть пустым.")
        self.app_id_stack = []
        self.res = []
        self.api_key = api_key
        self.session = requests.Session()
        self.switch = True
        self.session.headers.update({'User-Agent': 'SteamAPIPythonClient/1.0'})

        self.db_conn = sqlite3.connect(db_name)
        self.db_cursor = self.db_conn.cursor()
        self._init_db_()

        print(Fore.GREEN + 'Initialized' + Style.RESET_ALL)

    def _init_db_(self):
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                players_online INTEGER,
                current_price TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_conn.commit()

    def add_game(self, *app_ids):
        for app_id in app_ids:
            if isinstance(app_id, int):
                self.app_id_stack.insert(0, app_id)
                print(f"{Fore.YELLOW + '[*]' + Style.RESET_ALL} ID {Fore.LIGHTBLUE_EX + str(app_id) + Style.RESET_ALL} added to the stack. Current stack size: {Fore.LIGHTBLUE_EX + str(len(self.app_id_stack)) + Style.RESET_ALL}")
            else:
                print(f"{Fore.RED + '[!]' + Style.RESET_ALL} ERROR: {Fore.LIGHTBLUE_EX + str(app_id) + Style.RESET_ALL} it is not a valid ID. Skipped.")

    def _get_game_details(self, app_id: int):
        url = "https://store.steampowered.com/api/appdetails"
        params = {
            'appids': app_id,
            'cc': 'us',
            'l': 'english'
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            app_data = data.get(str(app_id))
            if app_data and app_data.get('success'):
                return app_data.get('data', {})
            return None
        except (requests.RequestException, ValueError) as e:
            print(f"{Fore.RED + '[!]' + Style.RESET_ALL} Error when receiving the details for the ID {Fore.LIGHTBLUE_EX + str(app_id) + Style.RESET_ALL}: {e}")
            return None

    def _get_online_count(self, app_id: int):
        url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
        params = {
            'key': self.api_key,
            'appid': app_id
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('response', {}).get('result') == 1:
                return data['response'].get('player_count', -1)
            return -1
        except (requests.RequestException, ValueError) as e:
            print(f"{Fore.RED + '[!]' + Style.RESET_ALL} Error when getting online for ID {Fore.LIGHTBLUE_EX + str(app_id) + Style.RESET_ALL}: {e}")
            self.switch = False
            return -1

    def process_stack(self):
        clear()
        print(f"\n{Fore.LIGHTGREEN_EX + '[+]' + Style.RESET_ALL} stack processing. Game in stack: {Fore.LIGHTBLUE_EX + str(len(self.app_id_stack)) + Style.RESET_ALL}")
        if not self.app_id_stack: print(f"{Fore.RED + '[!]' + Style.RESET_ALL} Stack nothing"); return

        while self.app_id_stack:
            app_id = self.app_id_stack.pop()
            print(f"\n-processing {Fore.LIGHTBLUE_EX + str(app_id) + Style.RESET_ALL}-")
            details = self._get_game_details(app_id)
            online = self._get_online_count(app_id)
            res_data = {
                'id': app_id,
                'name': 'N/A',
                'players_online': online,
                'current_price': 'N/A'
            }

            if details:
                res_data['name'] = details.get('name', 'N/A')
                if details.get('is_free'): res_data['current_price'] = "Free"
                elif 'price_overview' in details: res_data['current_price'] = details['price_overview'].get('final_formatted', 'N/A')
                else: res_data['current_price'] = 'Not sold individually'

            self.db_cursor.execute('''
                INSERT OR REPLACE INTO games (id, name, players_online, current_price, last_updated)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (res_data['id'], res_data['name'], res_data['players_online'], res_data['current_price']))
            self.db_conn.commit()

            # self.res.append(res_data)

            self.res.append(res_data)
            if not self.switch: self.switch = True 
            else: print(f"{Fore.LIGHTGREEN_EX + '[+]' + Style.RESET_ALL} result for ID: {Fore.LIGHTBLUE_EX + str(app_id) + Style.RESET_ALL}: {res_data}")

            if self.app_id_stack: time.sleep(1.5)

        print(f"\n{Fore.LIGHTGREEN_EX + '[+]' + Style.RESET_ALL} Processing completed")

    def show_res(self):
        clear()
        self.db_cursor.execute("SELECT id, name, players_online, current_price FROM games ORDER BY players_online DESC")
        results = self.db_cursor.fetchall()
        if not results: print('No results in database.'); return

        col_widths = {'id': 0, 'name': 0, 'online': 0, 'price': 0}
        for row in results:
            col_widths['id'] = max(col_widths['id'], len(str(row[0])))
            col_widths['name'] = max(col_widths['name'], len(row[1]))
            online_str = "N/A" if row[2] == -1 else f"{row[2]:,}"
            col_widths['online'] = max(col_widths['online'], len(online_str))
            col_widths['price'] = max(col_widths['price'], len(row[3]))
        
        id_h = 'ID'.ljust(col_widths['id'])
        name_h = 'Name'.ljust(col_widths['name'])
        online_h = 'Online'.ljust(col_widths['online'])
        price_h = 'Price'.ljust(col_widths['price'])

        print(Fore.LIGHTYELLOW_EX + f'{id_h} | {name_h} | {online_h} | {price_h}' + Style.RESET_ALL)
        print(f'{"-"*col_widths["id"]}-+-{"-"*col_widths["name"]}-+-{"-"*col_widths["online"]}-+-{"-"*col_widths["price"]}')

        for r in results:
            id_val = str(r[0]).ljust(col_widths['id'])
            name_val = r[1].ljust(col_widths['name'])
            
            online_count = r[2]
            if online_count == -1:
                online_val = "N/A".ljust(col_widths['online'])
                online_color = Fore.WHITE
            else:
                online_val = f"{online_count:,}".ljust(col_widths['online'])
                online_color = Fore.CYAN

            price_val_raw = r[3]
            if price_val_raw == "Free":
                price_color = Fore.GREEN
            elif price_val_raw in ['N/A', 'Not sold individually']:
                 price_color = Fore.WHITE
            else:
                 price_color = Fore.RED
            price_val = price_val_raw.ljust(col_widths['price'])
            
            print(f"{Fore.LIGHTBLUE_EX}{id_val}{Style.RESET_ALL} | {name_val} | {online_color}{online_val}{Style.RESET_ALL} | {price_color}{price_val}{Style.RESET_ALL}")

    def close(self):
        if self.db_conn:
            self.db_conn.close()
            print(Fore.YELLOW + "Database connection OFF" + Style.RESET_ALL)
            if api_key == 'My API very goooooooood!':
                print(f"{Fore.RED} [!] WARNING: Please replace 'My API very goooooooood!' with your real Steam API key if you are the developer of the game to get more information and remove restrictions{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        api_key='My API very goooooooood!'
        parser = SteamDB_API(api_key)

        for i in range(500, 1000):
            parser.add_game(i)

        # parser.add_game(730)      # Counter-Strike 2
        # parser.add_game(578080)   # PUBG
        # parser.add_game(1245620)  # ELDEN RING
        # parser.add_game(1643320)  # Vampire Survivors
        # parser.add_game(271590)   # Grand Theft Auto V
        # parser.add_game(7)        # Хз что это в steam

        parser.process_stack()
        parser.show_res()

    except ValueError as e:
        print(f"FAIL Initialized: {e}")
    except Exception as e:
        print(f"An unexpected error has occurred: {e}")