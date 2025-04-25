# Basketball Game Data Scraper

This script scrapes game data (overview, boxscore, play-by-play) from specific game pages on the Youth Basketball Champions League website.

## Setup

1.  **Install Python:** Make sure you have Python 3 installed.
2.  **Install Libraries:** Navigate to the script's directory in your terminal and install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Inspect HTML:** Open the target game URLs in your web browser:
    *   Overview: [https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#overview](https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#overview)
    *   Boxscore: [https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#boxscore](https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#boxscore)
    *   Play-by-Play: [https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#playByPlay](https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#playByPlay)
    
    Use your browser's developer tools (usually by right-clicking on the element you want and selecting "Inspect" or "Inspect Element") to find the HTML tags, IDs, and classes associated with the data you want to extract (e.g., team names, scores, player stats tables, play-by-play event list).

2.  **Update Script:** Edit the `scraper.py` file. Locate the `TODO` sections within the `parse_overview`, `parse_boxscore`, and `parse_play_by_play` functions. Replace the example comments with actual `BeautifulSoup` code (e.g., `soup.find(...)`, `soup.find_all(...)`, `soup.select(...)`) using the selectors you identified in the previous step to extract the data.

3.  **Run Script:** Execute the script from your terminal:
    ```bash
    python scraper.py
    ```

4.  **Output:** The script will fetch the data, attempt to parse it based on your added logic, print status messages, and save the extracted data into a `game_data.json` file in the same directory.

## Notes

*   Web scraping can be fragile. If the website structure changes, the script may need to be updated.
*   Be respectful of the website's terms of service and avoid sending too many requests in a short period.
*   The script currently assumes the content for overview, boxscore, and play-by-play might be loaded separately or within the same initial HTML. If the site heavily relies on JavaScript to load data *after* the initial page load (e.g., when clicking tabs), a more complex approach using tools like Selenium or Playwright might be necessary to automate browser actions. 