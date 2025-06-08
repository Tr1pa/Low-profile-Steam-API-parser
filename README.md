### Русская версия

# Steam Game Data Parser & Tracker

Это консольный скрипт на Python для получения актуальной информации об играх из Steam. Он позволяет отслеживать количество игроков онлайн, текущие цены и другую информацию, сохраняя все данные в локальной базе данных SQLite для последующего просмотра.

## 🚀 Ключевые возможности

*   **Получение данных по App ID:** Вы можете добавить одну или несколько игр в очередь на обработку, указав их уникальный `App ID` в Steam.
*   **Актуальные данные:** Скрипт обращается к двум разным API Steam, чтобы получить:
    *   **Детали игры:** Название, текущая цена, является ли игра бесплатной (free-to-play).
    *   **Количество игроков:** Актуальное число пользователей, находящихся в игре в данный момент.
*   **Локальная база данных:** Все полученные результаты сохраняются в файл базы данных SQLite (`steamapiparser.db`). Это позволяет:
    *   Сохранять данные между запусками скрипта.
    *   Быстро просматривать уже собранную информацию без повторных запросов к API.
    *   Автоматически обновлять запись об игре, если она уже есть в базе.
*   **Форматированный вывод:** Результаты отображаются в виде аккуратной, отформатированной таблицы прямо в консоли. Таблица автоматически сортируется по количеству игроков онлайн (от большего к меньшему).
*   **Цветовое кодирование:** Для лучшей читаемости в выводе используются цвета: цены, названия и онлайн подсвечиваются, что делает информацию наглядной.

## ⚙️ Как это работает

1.  **Инициализация:** При запуске скрипт создает экземпляр класса `SteamDB_API` и подключается к базе данных SQLite, создавая таблицу `games`, если она еще не существует.
2.  **Добавление игр:** Вы добавляете `App ID` интересующих вас игр в стек обработки с помощью метода `add_game()`.
3.  **Обработка стека:** Метод `process_stack()` последовательно извлекает ID из стека и для каждого из них выполняет два HTTP-запроса:
    *   `store.steampowered.com/api/appdetails` — для получения названия и цены.
    *   `api.steampowered.com/ISteamUserStats/...` — для получения количества игроков онлайн (требует API-ключ).
4.  **Сохранение в БД:** Полученные данные объединяются и сохраняются в базу данных с помощью команды `INSERT OR REPLACE`, которая либо создает новую запись, либо обновляет существующую.
5.  **Отображение результатов:** Метод `show_res()` запрашивает все записи из базы данных, сортирует их, вычисляет необходимую ширину столбцов и выводит красивую таблицу в консоль.

## 🛠️ Технологии и библиотеки

*   **Python 3**
*   **requests:** для выполнения HTTP-запросов к Steam API.
*   **sqlite3:** для работы с локальной реляционной базой данных.
*   **colorama:** для кросс-платформенного цветного вывода в терминале.
*   **os, time:** стандартные библиотеки для системных команд (очистка экрана) и установки задержек между запросами.

## 📋 Как использовать

1.  **Установите зависимости:**
    ```bash
    pip install requests colorama
    ```
2.  **Получите API-ключ Steam:**
    *   Для получения данных об игроках онлайн необходим ключ Steam Web API.
    *   Вы можете бесплатно получить его здесь: [https://steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
3.  **Настройте скрипт:**
    *   Откройте файл скрипта и найдите строку: `api_key='My API very goooooooood!'`.
    *   Замените `'My API very goooooooood!'` на ваш реальный API-ключ.
4.  **Добавьте игры и запустите:**
    *   В блоке `if __name__ == "__main__":` добавьте `App ID` нужных игр:
      ```python
      parser.add_game(730)      # Counter-Strike 2
      parser.add_game(578080)   # PUBG
      ```
    *   Запустите скрипт из терминала:
      ```bash
      python your_script_name.py
      ```
    *   Наслаждайтесь результатом! Данные будут сохранены в файле `steamapiparser.db` в той же папке.

---

### English Version

# Steam Game Data Parser & Tracker

This is a Python command-line script for fetching up-to-date information about Steam games. It allows you to track player counts, current prices, and other details, storing all the data in a local SQLite database for easy viewing.

## 🚀 Key Features

*   **Fetch Data by App ID:** You can add one or more games to a processing queue by providing their unique Steam `App ID`.
*   **Real-time Data:** The script queries two different Steam APIs to retrieve:
    *   **Game Details:** Name, current price, and free-to-play status.
    *   **Player Count:** The current number of users actively playing the game.
*   **Persistent Data Storage:** All fetched results are saved into a local SQLite database file (`steamapiparser.db`). This enables you to:
    *   Retain data between script executions.
    *   Quickly view previously collected information without making new API requests.
    *   Automatically update a game's record if it already exists in the database.
*   **Formatted Tabular Display:** The results are displayed in a clean, well-formatted table directly in the console. The table is automatically sorted by the number of online players in descending order.
*   **Color-Coded Output:** To improve readability, the console output is color-coded. Prices, names, and player counts are highlighted, making the data easy to scan.

## ⚙️ How It Works

1.  **Initialization:** On startup, the script instantiates the `SteamDB_API` class and connects to an SQLite database, creating a `games` table if one doesn't already exist.
2.  **Adding Games:** You add the `App ID` of the games you're interested in to a processing stack using the `add_game()` method.
3.  **Processing the Stack:** The `process_stack()` method iterates through the stack, and for each ID, it performs two HTTP requests:
    *   `store.steampowered.com/api/appdetails` — to get the name and price.
    *   `api.steampowered.com/ISteamUserStats/...` — to get the online player count (requires an API key).
4.  **Saving to DB:** The collected data is combined and saved to the database using an `INSERT OR REPLACE` statement, which either creates a new record or updates an existing one.
5.  **Displaying Results:** The `show_res()` method queries all records from the database, sorts them, calculates the required column widths for alignment, and prints a beautiful table to the console.

## 🛠️ Technologies & Libraries

*   **Python 3**
*   **requests:** For making HTTP requests to the Steam API.
*   **sqlite3:** For working with a local relational database.
*   **colorama:** For cross-platform colored terminal output.
*   **os, time:** Standard libraries for system commands (clearing the screen) and setting delays between requests.

## 📋 How to Use

1.  **Install Dependencies:**
    ```bash
    pip install requests colorama
    ```
2.  **Get a Steam API Key:**
    *   A Steam Web API key is required to fetch player count data.
    *   You can get one for free here: [https://steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
3.  **Configure the Script:**
    *   Open the script file and find the line: `api_key='My API very goooooooood!'`.
    *   Replace `'My API very goooooooood!'` with your actual API key.
4.  **Add Games and Run:**
    *   In the `if __name__ == "__main__":` block, add the `App ID`s of the games you want to track:
      ```python
      parser.add_game(730)      # Counter-Strike 2
      parser.add_game(578080)   # PUBG
      ```
    *   Run the script from your terminal:
      ```bash
      python your_script_name.py
      ```
    *   Enjoy the results! The data will be saved in the `steamapiparser.db` file in the same directory.
