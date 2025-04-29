import requests
from bs4 import BeautifulSoup
import time # Added for potential waits
import re # Added for regex-based foul counting

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# URLs from README.md
urls = {
    "overview": "https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#overview",
    "boxscore": "https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#boxscore",
    "play_by_play": "https://www.championsleague.basketball/en/youth/games/126767-REG-SPAR#playByPlay",
}

def fetch_html(url):
    """Fetches static HTML content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_static_data(html_content, data_type):
    """Parses static HTML and extracts relevant data (overview, boxscore)."""
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')

    print(f"--- Scraping {data_type} ---")

    # --- Placeholder for data extraction logic ---
    # TODO: Inspect the HTML structure of the pages to find the correct selectors
    # for overview and boxscore data.

    if data_type == "overview":
        # Example: Find the main content area for overview
        # overview_data = soup.find('div', id='overview-content') # Replace with actual selector
        # print(overview_data.text if overview_data else "Overview data not found")
        print("TODO: Add overview extraction logic")
        pass
    elif data_type == "boxscore":
        # Example: Find the boxscore table
        # boxscore_table = soup.find('table', class_='boxscore-table') # Replace with actual selector
        # print(boxscore_table if boxscore_table else "Boxscore data not found")
        print("TODO: Add boxscore extraction logic")
        pass
    # --- End Placeholder ---

    print("-" * (len(data_type) + 14)) # Separator line
    print("\n")

    return None # Return actual data later

def scrape_play_by_play_dynamic(url):
    """Uses Selenium to scrape PBP entries and count fouls per team/quarter."""
    print(f"--- Scraping play_by_play (dynamic) ---")

    # --- WebDriver Setup ---
    # TODO: Ensure you have the appropriate WebDriver installed (e.g., chromedriver)
    # and it's in your PATH or provide the path explicitly:
    # options = webdriver.ChromeOptions()
    # service = webdriver.ChromeService(executable_path='/path/to/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-notifications') # Disable browser notifications
    # options.add_argument('--headless') # Optional: Run headless
    # options.add_argument('--no-sandbox') # Optional: Needed for some environments
    # options.add_argument('--disable-dev-shm-usage') # Optional: Needed for some environments
    try:
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        print("Browser window maximized.")
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        print("Please ensure WebDriver is installed and configured correctly.")
        return None

    # --- Team Identification --- 
    # Assumption based on HTML analysis (Needs verification if counts are wrong)
    team1_name = "REG"
    team2_name = "SPAR"
    # Corrected IDs based on debug output
    team1_org_id = "709"   # Confirmed ID for REG
    team2_org_id = "2102"  # Correct ID for SPAR (was 58357)
    print(f"Assuming teams: {team1_name} (Org ID {team1_org_id}), {team2_name} (Org ID {team2_org_id})")

    quarterly_fouls = {}
    driver.get(url)

    try:
        # --- Handle Cookie Banner ---
        cookie_handled = False
        try:
            cookie_wait = WebDriverWait(driver, 12) # Slightly longer wait
            iframe_selector = 'iframe[id*="axeptio"], iframe[src*="axeptio"]'
            # Target the link by its exact text
            consent_link_text = 'Continue without consent'

            time.sleep(0.5) # Small pause before checking iframe

            # Check if the iframe exists
            try:
                cookie_iframe = cookie_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector)))
                print("Switching to cookie iframe...")
                driver.switch_to.frame(cookie_iframe)
            except TimeoutException:
                print("Cookie iframe not found, proceeding in default content.")
                # No iframe found, assume link is in the main document
                pass

            # Wait for the link within the current context (main document or iframe)
            consent_link = cookie_wait.until(EC.element_to_be_clickable(
                (By.LINK_TEXT, consent_link_text) # Use LINK_TEXT for exact match
            ))

            print(f"Cookie consent link ('{consent_link_text}') found, attempting click...")
            try:
                # Try standard click first
                consent_link.click()
                print("Standard click attempted on consent link.")
            except Exception as click_err:
                print(f"Standard click failed on consent link: {click_err}. Trying JavaScript click.")
                # Fallback to JavaScript click
                driver.execute_script("arguments[0].click();", consent_link)
                print("JavaScript click attempted on consent link.")

            # Switch back to default content IF we switched to an iframe
            if 'cookie_iframe' in locals() and cookie_iframe is not None:
                print("Switching back to default content...")
                driver.switch_to.default_content()

            # Wait for the link to disappear (verify click worked)
            # Note: Sometimes only the parent banner/iframe disappears.
            try:
                print("Waiting for consent link to disappear...")
                WebDriverWait(driver, 5).until_not(
                    EC.presence_of_element_located((By.LINK_TEXT, consent_link_text))
                )
                print("Consent link disappeared.")
                cookie_handled = True
            except TimeoutException:
                 # If link didn't disappear, check if iframe is gone (alternative check)
                 try:
                     WebDriverWait(driver, 2).until_not(
                         EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector))
                     )
                     print("Cookie iframe disappeared.")
                     cookie_handled = True
                 except TimeoutException:
                     print("Consent link/iframe did not disappear after click attempt.")

        except TimeoutException:
            print(f"Cookie consent link ('{consent_link_text}') not found or timed out.")
        except Exception as cookie_err:
            print(f"Error handling cookie banner: {cookie_err}")
        finally:
            # Ensure we are in the default content even if errors occurred
            try:
                driver.switch_to.default_content()
            except Exception:
                pass # Ignore errors if already in default content or context is lost

        if not cookie_handled:
             print("Warning: Failed to confirm cookie banner dismissal. Proceeding anyway...")

        # --- Find Quarter Selectors --- 
        wait = WebDriverWait(driver, 15)
        quarter_labels = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'label[for^="game-tab-roster-teams-quarter-"]')
        ))
        quarter_ids = [label.get_attribute('for').split('-')[-1] for label in quarter_labels]
        print(f"Found quarter selectors for: {quarter_ids}")

        for i, label in enumerate(quarter_labels):
            quarter = quarter_ids[i]
            print(f"  Clicking {quarter}...")
            # Initialize foul counts for the quarter
            quarter_fouls = {team1_name: 0, team2_name: 0}

            try:
                # Scroll into view and click
                driver.execute_script("arguments[0].scrollIntoView(true);", label)
                time.sleep(0.5) # Brief pause before click
                label.click()
                time.sleep(0.5) # Brief pause after click

                # --- Wait for PBP Data Container to Load --- 
                pbp_container_selector = 'div._6nwioy6' # Selector for the main PBP container
                entry_selector = 'div.iqxq5d1'       # Selector for individual entries
                print(f"    Waiting for PBP container '{pbp_container_selector}'...")
                try:
                    # Wait for the container itself
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, pbp_container_selector)))
                    # Optional: Add a short static sleep IF data inside container loads slower
                    time.sleep(1.0) 
                    print("    PBP container found.")
                except TimeoutException:
                    print(f"    Warning: Timed out waiting for PBP container '{pbp_container_selector}'. Skipping quarter {quarter}.")
                    quarterly_fouls[quarter] = {team1_name: 'Error', team2_name: 'Error'}
                    continue # Skip to next quarter

                # --- Extract PBP Entries and Count Fouls --- 
                page_soup = BeautifulSoup(driver.page_source, 'html.parser')
                pbp_entries = page_soup.select(entry_selector)

                print(f"    Found {len(pbp_entries)} PBP entries for {quarter}.")

                if not pbp_entries:
                    print(f"    Warning: No PBP entries found with selector '{entry_selector}'.")

                for entry in pbp_entries:
                    entry_text = entry.get_text(separator=" ", strip=True)
                    team_logo_img = entry.select_one('img[src*="organisation_"]')
                    entry_team = None

                    if team_logo_img and team_logo_img.get('src'):
                        img_src = team_logo_img['src']
                        if f"organisation_{team1_org_id}" in img_src:
                            entry_team = team1_name
                        elif f"organisation_{team2_org_id}" in img_src:
                            entry_team = team2_name

                    # Check for specific foul types, ignore "foul drawn"
                    is_committed_foul = re.search(r'(personal|offensive|technical|unsportsmanlike) foul', entry_text, re.IGNORECASE)

                    if is_committed_foul: # Use the new check for committed fouls
                        debug_img_src = team_logo_img['src'] if team_logo_img and team_logo_img.get('src') else "No Img Src Found"
                        debug_assigned_team = entry_team if entry_team else "None"
                        print(f"      [DEBUG FOUL] Text: {entry_text[:60]}... | Img Src: {debug_img_src} | Assigned Team: {debug_assigned_team}") # Debug print for fouls
                        if entry_team: # Only increment if a team was assigned
                            quarter_fouls[entry_team] += 1

                quarterly_fouls[quarter] = quarter_fouls
                print(f"    Foul counts for {quarter}: {quarter_fouls}")

            except (NoSuchElementException, TimeoutException, Exception) as process_err:
                print(f"    Error processing quarter {quarter}: {process_err}")
                quarterly_fouls[quarter] = {team1_name: 'Error', team2_name: 'Error'}

    except TimeoutException:
        print("Error: Could not find quarter selectors within the time limit.")
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
    finally:
        print("Closing WebDriver...")
        driver.quit()

    print("--- Finished Play-by-Play Scraping ---\n")
    return quarterly_fouls


if __name__ == "__main__":
    scraped_data = {}
    for data_type, url in urls.items():
        if data_type == "play_by_play":
            # Use Selenium for dynamic PBP data - now gets foul counts
            foul_counts = scrape_play_by_play_dynamic(url)
            scraped_data['quarterly_fouls'] = foul_counts # Store foul counts
        else:
            # Use requests/BeautifulSoup for static pages
            print(f"Fetching {data_type} data from: {url}")
            html = fetch_html(url)
            content = scrape_static_data(html, data_type)
            scraped_data[data_type] = content

    # TODO: Process or save the scraped_data dictionary
    print("\n--- All Scraped Data (including Foul Counts) ---")
    import json
    print(json.dumps(scraped_data, indent=2)) 