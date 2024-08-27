import asyncio
import motor.motor_asyncio
import sys
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

async def check_mongo(ip, timeout=2):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f'mongodb://{ip}:27017/',
        serverSelectionTimeoutMS=timeout * 1000,
        connectTimeoutMS=timeout * 1000,
    )
    try:
        await client.server_info()
        return True
    except Exception:
        return False
    finally:
        client.close()

async def process_ips(file_name, output_file):
    with open(file_name, 'r') as file:
        ips = [line.strip() for line in file if line.strip()]

    online_ips = []
    total_ips = len(ips)
    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Checking IPs...", total=total_ips)

        for ip in ips:
            result = await check_mongo(ip)
            if result:
                online_ips.append(ip)
                console.print(f"[green]Online: {ip}[/green]")
            else:
                console.print(f"[red]Offline: {ip}[/red]")
            progress.update(task, advance=1)
    with open(output_file, 'w') as file:
        for ip in online_ips:
            file.write(f"{ip}\n")

    elapsed_time = time.time() - start_time
    ips_per_second = total_ips / elapsed_time if elapsed_time > 0 else 0

    console.print(f"\n[bold green]Scan complete![/bold green]")
    console.print(f"[cyan]Total IPs checked: {total_ips}[/cyan]")
    console.print(f"[cyan]Online IPs found: {len(online_ips)}[/cyan]")
    console.print(f"[cyan]Average speed: {ips_per_second:.2f} IPs/second[/cyan]")
    console.print(f"[cyan]Results saved to: {output_file}[/cyan]")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        console.print("[bold red]Usage: python script.py <ips_file.txt>[/bold red]")
    else:
        asyncio.run(process_ips(sys.argv[1], "Online.txt"))
