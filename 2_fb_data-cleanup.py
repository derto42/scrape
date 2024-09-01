import json
import re

def clean_title(title):
    # Regex to find the pattern "in City, State" at the end of the title
    pattern = re.compile(r'\s+in\s+[A-Za-z\s]+,\s+[A-Z]{2}$|\s+in\s+$')
    # Remove the pattern if found
    clean_title = re.sub(pattern, '', title)
    return clean_title

def clean_link(link):
    # Clean the link by removing specified URL parameters
    clean_link = re.split(r'\?ref=search', link)[0]
    return clean_link

def process_items(file_path):
    # Load the JSON data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Process each item in the JSON data
    for product_group, locations in data.items():
        for location, items in locations.items():
            for item in items:
                # Clean the title and link of each item
                item['title'] = clean_title(item['title'])
                item['link'] = clean_link(item['link'])

    # Save the cleaned data to a new JSON file
    with open('fb_local_items_cleaned.json', 'w') as file:
        json.dump(data, file, indent=4)

# Path to the JSON file containing the data
file_path = 'fb_local_items.json'
process_items(file_path)
