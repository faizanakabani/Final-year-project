import json

# Load the scraped data from the JSON file
with open("scraped_data.json", "r", encoding="utf-8") as f:
    scraped_data = json.load(f)

# Print the type of the scraped_data
print(type(scraped_data))

# Print the keys of the scraped_data
for key in scraped_data.keys():
    print(key)

    import requests
    response = requests.get(key)

    print(response.status_code)
