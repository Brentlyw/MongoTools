![Alt text](https://i.postimg.cc/fbFNz9xK/mongotools.jpg)

# Whats Included?
- **MongoBrute**: A MongoDB authentication bruteforcer that uses a user:pass combolist and targets a list of IPs.
- **MongoAnarchy**: A modified MongoBrute script, uses blacklists, chunking, and async requests. Slightly faster, as effective.
- **MongoBrute_Motor**: A modified MongoBrute script using the Motor library for concurrent requests, much faster, less pretty, and sometimes less accurate.
- **MongoDump**: Given you have credentials, this will list and dump/exfil the entirety of the MongoDB instance to ".csv" files.
- **MongoLatency**: Iterates through a ".txt" list of IPs and saves those which are online, and have low latency (2000ms).
- **MongoGem**: Used to scan a list of MongoDB IPs (unauthenticated) and scan for unbreached databases with >3 collections.
- **ShodanMongo**: Uses your Shodan API key to scrape public-facing MongoDB instance IP addresses and save to "Targets.txt."
- **Combo.txt**: The first combolist to try, most effective.
- **Combo2.txt**: The second combolist to try, less effective.

# Notes
- Some scripts have a nice little UI, some dont. They all still work.
- I didn't include requirements.txt this time.
- MongoGem is to be used against a set of MongoDB IPs that **do not** require authentication. 99% of these are compromised already, but sometimes you can find a "gem."
- I prefer using MongoBrute against smaller lists of IPs, while using the Motor fork or MongoAnarchy for larger lists. I recommend this.
