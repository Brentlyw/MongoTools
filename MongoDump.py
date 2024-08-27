import os
import csv
from pymongo import MongoClient, errors
from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.table import Table

console = Console()

def list_db_col(ip, username, password):
    try:
        client = MongoClient(f'mongodb://{username}:{password}@{ip}:27017/', serverSelectionTimeoutMS=5000)
        console.print(f"[bold green]Connected to MongoDB instance at {ip}.[/bold green]")
        databases = client.list_database_names()
        if not databases:
            console.print("[bold yellow]No databases found on the server.[/bold yellow]")
            return []
        db_collection_map = []
        for db_name in databases:
            try:
                db = client[db_name]
                collections = db.list_collection_names()
                if collections:
                    db_collection_map.append((db_name, collections))
                else:
                    console.print(f"[bold yellow]No collections found in database {db_name}.[/bold yellow]")
            except errors.OperationFailure as e:
                console.print(f"[bold yellow]Skipping database {db_name} due to insufficient permissions.[/bold yellow]")
                continue
        return db_collection_map
    except errors.ServerSelectionTimeoutError:
        console.print(f"[bold red]Unable to connect to MongoDB instance at {ip} (Timeout).[/bold red]")
    except errors.OperationFailure as e:
        console.print(f"[bold red]Authentication failed: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
    finally:
        if 'client' in locals():
            client.close()

def dumpCol(db, collection_name, ip):
    try:
        collection = db[collection_name]
        folder_name = f"dumps/{ip}/{db.name}"
        os.makedirs(folder_name, exist_ok=True)
        file_path = os.path.join(folder_name, f"{collection_name}.csv")
        cursor = collection.find()
        if cursor.collection.count_documents({}) == 0:
            return 0
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            first_doc = next(cursor, None)
            if not first_doc:
                return 0
            header = first_doc.keys()
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerow(first_doc)
            row_count = 1
            for document in cursor:
                if set(document.keys()) != set(header):
                    header = document.keys()
                    file.seek(0)
                    writer = csv.DictWriter(file, fieldnames=header)
                    writer.writeheader()

                writer.writerow(document)
                row_count += 1

        return row_count
    except errors.OperationFailure:
        return 0
    except Exception:
        return 0

def dumpAllCol(ip, username, password, db_collection_map):
    try:
        client = MongoClient(f'mongodb://{username}:{password}@{ip}:27017/', serverSelectionTimeoutMS=5000)
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Database Name", style="bold magenta")
        table.add_column("Number of Collections", style="bold cyan")
        table.add_column("Status", style="bold green")
        total_databases = 0
        total_collections = 0
        total_rows = 0
        for db_name, collections in db_collection_map:
            table.add_row(db_name, str(len(collections)), "[bold yellow]In progress...[/bold yellow]")
        with Live(table, console=console, refresh_per_second=4) as live:
            for row_num, (db_name, collections) in enumerate(db_collection_map):
                success = True
                db = client[db_name]
                database_rows = 0
                collections_dumped = 0
                for collection in collections:
                    row_count = dumpCol(db, collection, ip)
                    if row_count == 0:
                        success = False
                        console.print(f"[bold yellow]Collection '{collection}' in database '{db_name}' was skipped (no data or error).[/bold yellow]")
                    else:
                        total_collections += 1
                        collections_dumped += 1
                        database_rows += row_count
                if success:
                    total_databases += 1
                total_rows += database_rows
                status = f"[bold green][DUMPED {collections_dumped}/{len(collections)}][/bold green]" if collections_dumped == len(collections) else f"[bold red][FAILED {collections_dumped}/{len(collections)}][/bold red]"
                new_table = Table(show_header=True, header_style="bold cyan")
                new_table.add_column("Database Name", style="bold magenta")
                new_table.add_column("Number of Collections", style="bold cyan")
                new_table.add_column("Status", style="bold green")
                for i, (db_name, collections) in enumerate(db_collection_map):
                    if i < row_num:
                        final_status = f"[bold green][DUMPED {len(collections)}/{len(collections)}][/bold green]"
                    elif i == row_num:
                        final_status = status
                    else:
                        final_status = "[bold yellow]In progress...[/bold yellow]"
                    new_table.add_row(db_name, str(len(collections)), final_status)
                live.update(new_table)
        return total_databases, total_collections, total_rows
    except Exception as e:
        console.print(f"[bold red]Err while dumping: {e}[/bold red]")
        return 0, 0, 0
    finally:
        if 'client' in locals():
            client.close()




if __name__ == "__main__":
    console.print("[bold magenta]MongoDB Database Dumper [MDBDD v1.0][/bold magenta]")
    ip = Prompt.ask("[bold bright_white]Enter MongoDB address[/bold bright_white]", default="localhost")
    username = Prompt.ask("[bold bright_white]Enter username[/bold bright_white]", default="admin")
    password = Prompt.ask("[bold bright_white]Enter password[/bold bright_white]", password=True)
    db_collection_map = list_db_col(ip, username, password)
    if db_collection_map:
        console.print("\n[bold cyan]Starting dumper...[/bold cyan]")
        total_databases, total_collections, total_rows = dumpAllCol(ip, username, password, db_collection_map)
        console.print(f"\n[bold green]{total_databases} Databases | {total_collections} Collections | {total_rows} Rows Successfully Dumped.[/bold green]")
    else:
        console.print("[bold red]No collections to dump.[/bold red]")
