# MongoTools
A collection of Mongodb offensive python tools.

# Whats Included?
- **MongoBrute**: *A MongoDB auth bruteforcer which uses a common user:pass combolist, targets a list of IPs.*
- **MongoDump**: *Given you have credentials, this will list and dump the entirety of the MongoDB instance to multiple .csv files.*
- **MongoLatency**: *Itterates through a .txt list of IPs and saves those which have low latency (<2s).*
- **MongoGem**: *Used to scan a .txt file of MongoDB IPs (unauthenticated) and scan collections for sensitive data. This doesnt find much.*
- **ShodanScrape**: *Uses your Shodan API key to scrape public-facing MongoDB instances IP addresses and save to "Targets.txt".*
