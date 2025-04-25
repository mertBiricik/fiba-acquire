import requests
from bs4 import BeautifulSoup
import json

def fetch_html(url):
    """Fetches HTML content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def parse_overview(soup):
    """Parses the overview data from the BeautifulSoup object."""
    overview_data = {}
    print("Parsing overview...")

    # --- TODO: Inspect the HTML and add your parsing logic here ---
    # Find the quarter scores table
    score_table = None
    tables = soup.find_all('table')
    for table in tables:
        headers = [th.text.strip() for th in table.find_all('th')] # Check th elements first
        if not headers: # If no th, check td in the first row
             first_row = table.find('tr')
             if first_row:
                 headers = [cell.text.strip() for cell in first_row.find_all(['td', 'th'])]

        if 'Q1' in headers and 'Q2' in headers and 'Q3' in headers and 'Q4' in headers:
            score_table = table
            break

    if score_table:
        quarter_scores = {}
        rows = score_table.find_all('tr')
        # Find header index to handle potential variations
        header_cells = rows[0].find_all(['td', 'th'])
        col_indices = {cell.text.strip(): i for i, cell in enumerate(header_cells)}

        data_rows = rows[1:] # Assuming subsequent rows are data

        team_col_index = -1
        # Find the 'team' column index (might not be the first if structure varies)
        # Simple approach: assume first column without a Quarter name is the team
        for i, header in enumerate(headers):
            if header and not header.startswith('Q'):
                 team_col_index = i
                 break
        if team_col_index == -1: # Default to 0 if not found
            team_col_index = 0


        for row in data_rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) > max(col_indices.values()): # Ensure row has enough cells
                try:
                    team_name = cells[team_col_index].text.strip()
                    scores = {
                        'Q1': cells[col_indices['Q1']].text.strip(),
                        'Q2': cells[col_indices['Q2']].text.strip(),
                        'Q3': cells[col_indices['Q3']].text.strip(),
                        'Q4': cells[col_indices['Q4']].text.strip()
                    }
                    # Basic validation: check if scores look like numbers
                    if all(s.isdigit() for s in scores.values()):
                        quarter_scores[team_name] = scores
                except (IndexError, KeyError) as e:
                     print(f"Skipping row due to parsing error: {e} - Row: {row.text.strip()}")


        if quarter_scores: # Check if we actually found scores
            overview_data['quarter_scores'] = quarter_scores
        else:
             print("Found table but could not parse quarter scores.")
    else:
        print("Could not find the quarter scores table.")

    # --- End TODO ---

    print(f"Parsed overview data: {overview_data}")
    return overview_data

def parse_boxscore(soup):
    """Parses the boxscore data from the BeautifulSoup object."""
    boxscore_data = {"home_team": [], "away_team": []}
    print("Parsing boxscore...")

    # --- TODO: Inspect the HTML and add your parsing logic here ---
    # Example (replace with actual selectors):
    # You'll likely need to find the tables containing player stats for each team.
    # boxscore_tables = soup.find_all('table', class_='boxscore-table') # Fictional example
    # if len(boxscore_tables) == 2:
    #     home_table = boxscore_tables[0]
    #     away_table = boxscore_tables[1]
    #     # Iterate through rows (<tr>) and cells (<td>) of each table
    #     # to extract player names and their stats.
    #     # Append player data as dictionaries to boxscore_data['home_team'] and boxscore_data['away_team']
    #     pass
    # --- End TODO ---

    print(f"Parsed boxscore data (stub): {boxscore_data}")
    return boxscore_data

def parse_play_by_play(soup):
    """Parses the play-by-play data from the BeautifulSoup object."""
    play_by_play_data = []
    print("Parsing play-by-play...")

    # --- TODO: Inspect the HTML and add your parsing logic here ---
    # Example (replace with actual selectors):
    # Look for a table or list containing the sequence of game events.
    # pbp_table = soup.find('table', id='play-by-play-list') # Fictional example
    # if pbp_table:
    #     rows = pbp_table.find_all('tr') # Or list items 'li'
    #     for row in rows:
    #         # Extract timestamp, score, event description, player involved, etc.
    #         # event = { 'time': ..., 'score': ..., 'description': ... }
    #         # play_by_play_data.append(event)
    #         pass
    # --- End TODO ---

    print(f"Parsed play-by-play data (stub): {play_by_play_data}")
    return play_by_play_data

def main():
    urls = {
        "overview": "https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#overview",
        "boxscore": "https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#boxscore",
        "play_by_play": "https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#playByPlay",
    }

    all_game_data = {}

    # Although the URLs look similar with just fragment identifiers (#),
    # websites sometimes load different content dynamically based on the fragment.
    # It's safer to fetch each potentially distinct view, although it might
    # fetch the same base HTML multiple times if the site isn't dynamic.
    # A more advanced approach might involve browser automation (like Selenium)
    # if the content is indeed loaded dynamically via JavaScript clicks.
    # For now, we assume static or server-rendered content per URL variation.

    print("Fetching overview page...")
    html_overview = fetch_html(urls["overview"])
    if html_overview:
        soup_overview = BeautifulSoup(html_overview, 'html.parser')
        all_game_data['overview'] = parse_overview(soup_overview)

    print("\\nFetching boxscore page (might be same as overview)...")
    html_boxscore = fetch_html(urls["boxscore"])
    if html_boxscore:
        soup_boxscore = BeautifulSoup(html_boxscore, 'html.parser')
        # It's possible the boxscore elements are within the same HTML as overview
        # If they are different, use soup_boxscore. If same, you could reuse soup_overview.
        all_game_data['boxscore'] = parse_boxscore(soup_boxscore) # Or soup_overview

    print("\\nFetching play-by-play page (might be same as overview)...")
    html_pbp = fetch_html(urls["play_by_play"])
    if html_pbp:
        soup_pbp = BeautifulSoup(html_pbp, 'html.parser')
        # Similar logic as boxscore regarding reusing the soup object
        all_game_data['play_by_play'] = parse_play_by_play(soup_pbp) # Or soup_overview

    # --- Output the data ---
    output_filename = "game_data.json"
    print(f"\\nSaving data to {output_filename}...")
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_game_data, f, indent=4, ensure_ascii=False)
        print("Data saved successfully.")
    except IOError as e:
        print(f"Error writing data to file: {e}")
    except TypeError as e:
        print(f"Error serializing data to JSON (might be incomplete parsing): {e}")


if __name__ == "__main__":
    main() 