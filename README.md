![Alt text](https://i.postimg.cc/fbFNz9xK/mongotools.jpg)

# Whats Included?
- **MongoAnarchy**: A modified MongoBrute script, uses blacklists, chunking, and async requests. Slightly faster, as effective.
- **MongoDump**: Given you have credentials, this will list and dump/exfil the entirety of the MongoDB instance to ".csv" files.
- **MongoLatency**: Iterates through a ".txt" list of IPs and saves those which are online, and have low latency (2000ms).
- **MongoGem**: Used to scan a list of MongoDB IPs (unauthenticated) and scan for unbreached databases with >3 collections.
- **ShodanScrape**: Uses your Shodan API key to scrape public-facing MongoDB instance IP addresses and save to "Targets.txt."
- **Combo.txt**: A very effective MongoDB combolist.

# Notes
- Some scripts have a nice little UI, some dont. They all still work very well.
- I didn't include requirements.txt this time.
- MongoGem is to be used against a set of MongoDB IPs that **do not** require authentication. 99% of these are compromised already, but sometimes you can find a "gem."

# Update Log
*9/2/2024 - MongoAnarchy has been updated to include two login methods per combo, improved blacklist handling, and reduced false-positive blacklistings.*  
*9/2/2024 - MongoBrute & MongoBrute_Motor have been removed, as MongoAnarchy is now the best tool to use.*  
*9/2/2024 - MongoDump has had a complete backend overhaul regarding dumping, connecting, and user enumeration.*
