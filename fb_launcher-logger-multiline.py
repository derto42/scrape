import tkinter as tk
from subprocess import Popen, PIPE, STDOUT
import time
import logging

# Configure logging
logging.basicConfig(filename='scraping_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_scraping(location, search_term, retries=3):
    attempt = 0
    while attempt < retries:
        logging.info(f"Attempt {attempt + 1}: Starting scrape for {location} with search term '{search_term}'...")
        try:
            start_time = time.time()
            process = Popen(['python', '1_fb_scrape.py', location, search_term], stdout=PIPE, stderr=STDOUT, text=True)
            output, _ = process.communicate()
            if process.returncode != 0:
                logging.error(f"Scraping script returned a non-zero exit code: {process.returncode}")
                logging.error(f"Output: {output}")
                attempt += 1
                continue
            elapsed_time = time.time() - start_time
            logging.info(f"Scrape completed successfully in {elapsed_time:.2f} seconds for {location}.")
            return output, False
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)}")
            attempt += 1

    logging.warning(f"Max retries reached for {location}. Moving on...")
    return f"Failed after {retries} retries.", True

def main():
    with open("locations.txt", "r") as file:
        locations = [line.strip() for line in file if line.strip()]

    root = tk.Tk()
    root.title("Scraping Launcher")

    search_terms_vars = [tk.StringVar() for _ in range(5)]
    progress_var = tk.StringVar()
    progress_var.set("0/{}".format(len(locations) * len(search_terms_vars)))

    tk.Label(root, text="Enter Search Terms:").pack()
    search_entries = [tk.Entry(root, textvariable=var) for var in search_terms_vars]
    for entry in search_entries:
        entry.pack()

    tk.Label(root, textvariable=progress_var).pack()

    def on_launch():
        total_processed = 0
        for search_var in search_terms_vars:
            search_term = search_var.get().strip()
            if not search_term:
                continue  # Skip empty search fields
            logging.info(f"Launching scraping process for term: {search_term}")
            for location in locations:
                output, retry = run_scraping(location, search_term)
                total_processed += 1
                progress_var.set(f"{total_processed}/{len(locations) * len(search_terms_vars)}")
        logging.info("All search terms and locations processed.")

    tk.Button(root, text="Launch", command=on_launch).pack()

    root.mainloop()

if __name__ == "__main__":
    main()
