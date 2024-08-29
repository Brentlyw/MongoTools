from pymongo import MongoClient, errors
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_ips(file_name):
    with open(file_name, 'r') as file:
        ips = [line.strip() for line in file if line.strip()]
    return ips

def scan_mongo(ip):
    try:
        client = MongoClient(f'mongodb://{ip}:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()
        qualifying_dbs = 0
        total_qualifying_collections = 0
        for db_name in client.list_database_names():
            db = client[db_name]
            db_total_rows = 0
            db_collections = 0
            for collection_name in db.list_collection_names():
                collection = db[collection_name]
                record_count = collection.count_documents({})
                db_total_rows += record_count
                db_collections += 1
            if db_total_rows > 100 and db_collections > 5:
                qualifying_dbs += 1
                total_qualifying_collections += db_collections
        client.close()
        if qualifying_dbs > 0:
            print(f"[FOUND] {ip} has {qualifying_dbs} database(s) with >100 rows and >5 collections. Total qualifying collections: {total_qualifying_collections}")
            return True, ip, qualifying_dbs, total_qualifying_collections
        return False, ip, 0, 0
    except errors.ServerSelectionTimeoutError:
        print(f"[ERROR] Unable to connect to MongoDB instance at {ip}")
        return False, ip, 0, 0
    except Exception as e:
        print(f"[ERROR] An error occurred while scanning {ip}: {str(e)}")
        return False, ip, 0, 0

def main(ips_file, max_threads=10):
    ips = load_ips(ips_file)
    total_ips = len(ips)
    good_ips = []
    print(f"Starting scan of {total_ips} IP addresses...")
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(scan_mongo, ip): ip for ip in ips}

        for future in as_completed(futures):
            found, ip, dbs_count, collections_count = future.result()
            if found:
                good_ips.append((ip, dbs_count, collections_count))

    with open("Good.txt", "w") as good_file:
        for ip, dbs_count, collections_count in good_ips:
            good_file.write(f"{ip},{dbs_count},{collections_count}\n")
    print(f"Scan complete. {len(good_ips)} IPs with databases having >100 rows and >5 collections found. Results saved to Good.txt.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <ips_file.txt>")
    else:
        main(sys.argv[1])
