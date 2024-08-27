from pymongo import MongoClient, errors
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_ips(file_name):
    with open(file_name, 'r') as file:
        ips = [line.strip() for line in file if line.strip()]
    return ips
sensitive_keywords = ['user', 'users', 'usr', 'login', 'logins', 'email', 'emails', 'account', 'accounts', 'credential', 'credentials', 'auth', 'authentication', 'profile', 'profiles']
def is_sensitive(collection_name):
    for keyword in sensitive_keywords:
        if keyword in collection_name.lower():
            return True
    return False

def scan_mongo(ip):
    try:
        client = MongoClient(f'mongodb://{ip}:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()
        sensitive_found = False
        for db_name in client.list_database_names():
            db = client[db_name]
            for collection_name in db.list_collection_names():
                if is_sensitive(collection_name):
                    collection = db[collection_name]
                    record_count = collection.count_documents({})
                    if record_count > 10:
                        print(f"[FOUND] Sensitive collection with {record_count} records: Database: {db_name}, Collection: {collection_name} on {ip}")
                        sensitive_found = True
        client.close()
        return sensitive_found, ip
    except errors.ServerSelectionTimeoutError:
        print(f"[ERROR] Unable to connect to MongoDB instance at {ip}")
        return False, ip
    except Exception as e:
        print(f"[ERROR] An error occurred while scanning {ip}: {str(e)}")
        return False, ip

def main(ips_file, max_threads=10):
    ips = load_ips(ips_file)
    total_ips = len(ips)
    good_ips = []
    print(f"Starting scan of {total_ips} IP addresses...")
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(scan_mongo, ip): ip for ip in ips}

        for future in as_completed(futures):
            sensitive_found, ip = future.result()
            if sensitive_found:
                good_ips.append(ip)
    with open("Good.txt", "w") as good_file:
        for good_ip in good_ips:
            good_file.write(f"{good_ip}\n")
    print(f"Scan complete. {len(good_ips)} IPs with sensitive collections found. Results saved to Good.txt.")
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <ips_file.txt>")
    else:
        main(sys.argv[1])
