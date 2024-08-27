from pymongo import MongoClient, errors
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.progress import Progress
from tqdm import tqdm

console = Console()

def load_ips(file_name):
    with open(file_name, 'r') as file:
        ips = [line.strip() for line in file if line.strip()]
    return ips

def scan_mongo(ip, good_file):
    try:
        client = MongoClient(f'mongodb://{ip}:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()
        has_valid_db = False
        skip_ip = False
        total_rows = 0

        for db_name in client.list_database_names():
            if db_name in ["READ__ME_TO_RECOVER_YOUR_DATA", "READ_ME_TO_RECOVER_YOUR_DATA"]:
                skip_ip = True
                break

            db = client[db_name]
            for collection_name in db.list_collection_names():
                collection = db[collection_name]
                record_count = collection.count_documents({})
                total_rows += record_count
                if record_count > 10:
                    has_valid_db = True

        if total_rows == 19:
            skip_ip = True

        if not skip_ip and has_valid_db:
            good_file.write(f"{ip}\n")
            console.print(f"[bold green][SAVED][/bold green] IP: {ip} has valid database(s) without the target names, with collections having > 10 rows, and total rows != 19.")
        
        client.close()
        return True, ip
    
    except errors.ServerSelectionTimeoutError:
        return False, ip  # Skip IP since we cannot verify
    
    except Exception:
        return False, ip  # Skip IP due to error

def main(ips_file, max_threads=10):
    ips = load_ips(ips_file)
    total_ips = len(ips)

    console.print(f"[bold cyan]Starting scan of {total_ips} IP addresses...[/bold cyan]")
    
    with open("Good.txt", "w") as good_file:
        with ThreadPoolExecutor(max_threads) as executor:
            futures = {executor.submit(scan_mongo, ip, good_file): ip for ip in ips}
            
            with tqdm(total=total_ips, desc="Processing IPs", unit="ip") as pbar:
                for future in as_completed(futures):
                    _, ip = future.result()
                    pbar.update(1)
    
    console.print(f"[bold yellow]Scan complete.[/bold yellow] Results saved to Good.txt.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        console.print("[bold red]Usage: python script.py <ips_file.txt>[/bold red]")
    else:
        main(sys.argv[1])
