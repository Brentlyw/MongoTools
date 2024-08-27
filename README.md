# MongoTools
A collection of Mongodb offensive python tools for database dumping.

# Whats Included?
- **MongoBrute**: *A MongoDB auth bruteforcer which uses a common user:pass combolist, targets a list of IPs.*
- **MongoBrute_Motor**: *A modified MongoBrute script using the Motor library for concurrent requests, much faster, less pretty, sometimes less accurate.*
- **MongoDump**: *Given you have credentials, this will list and dump the entirety of the MongoDB instance to multiple .csv files.*
- **MongoLatency**: *Itterates through a .txt list of IPs and saves those which have low latency (<2s).*
- **MongoGem**: *Used to scan a .txt file of MongoDB IPs (unauthenticated) and scan collections for sensitive data. This doesnt find much.*
- **ShodanMongo**: *Uses your Shodan API key to scrape public-facing MongoDB instances IP addresses and save to "Targets.txt".*
