# MongoTools
A collection of Mongodb offensive python tools for database dumping.

# Whats Included?
- **MongoBrute**: *A MongoDB authentication bruteforcer which uses a user:pass combolist, targets a list of IPs.*
- **MongoBrute_Motor**: *A modified MongoBrute script using the Motor library for concurrent requests, **much faster, less pretty, sometimes less accurate.***
- **MongoDump**: *Given you have credentials, this will list and dump/exfil the entirety of the MongoDB instance to .csv files.*
- **MongoLatency**: *Itterates through a .txt list of IPs and saves those which have low latency (< 2s).*
- **MongoGem**: *Used to scan a .txt file of MongoDB IPs (unauthenticated) and scan collections for sensitive data.*
- **ShodanMongo**: *Uses your Shodan API key to scrape public-facing MongoDB instances IP addresses and save to "Targets.txt".*

# Notes
- I didn't include a requirements.txt this time.  
- MongoGem is to be used against a set of MongoDB IPs which **dont** require authentication. 99% of these are compromised already, but sometimes you can find a "gem"
- I prefer using MongoBrute against smaller lists of IPs, while using the Motor fork for larger lists. I reccomend this.
