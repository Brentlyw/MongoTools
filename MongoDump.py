import os
import csv
import json
from pymongo import MongoClient, errors
from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.table import Table

console = Console()

def connect_to_mongodb(ip, username, password):
    try:
        client = MongoClient(f'mongodb://{username}:{password}@{ip}:27017/?authSource=admin', serverSelectionTimeoutMS=5000)
        client.server_info()
        return client
    except errors.OperationFailure:
        try:
            client = MongoClient(f'mongodb://{username}:{password}@{ip}:27017/', serverSelectionTimeoutMS=5000)
            client.server_info()
            return client
        except errors.OperationFailure as e:
            console.print(f"[bold red]Authentication failed: {e}[/bold red]")
            return None
    except errors.ServerSelectionTimeoutError:
        console.print(f"[bold red]Unable to connect to MongoDB instance at {ip} (Timeout).[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during connection: {str(e)}[/bold red]")
        return None

def get_admin_users(client):
    admin_db = client['admin']
    try:
        users = list(admin_db.command("usersInfo")["users"])
        return users
    except errors.OperationFailure:
        try:
            users = list(admin_db['system.users'].find())
            return users
        except errors.OperationFailure:
            console.print("[bold yellow]Unable to retrieve user information from admin database.[/bold yellow]")
            return None

def display_users_grid(users):
    if not users:
        console.print("[bold yellow]No user information available.[/bold yellow]")
        return

    table = Table(title="MongoDB Users")
    table.add_column("Username", style="cyan")
    table.add_column("Permissions", style="magenta")

    for user in users:
        username = user.get("user", "N/A")
        roles = ', '.join([f"{role['role']}@{role['db']}" for role in user.get("roles", [])])
        table.add_row(username, roles)
    console.print("[bold green]Successfully retrieved user information.[/bold green]")
    console.print(table)

def list_db_col(client):
    try:
        databases = client.list_database_names()
        if not databases:
            console.print("[bold yellow]No databases found or insufficient permissions to list databases.[/bold yellow]")
            return []
        
        db_collection_map = []
        for db_name in databases:
            try:
                db = client[db_name]
                collections = db.list_collection_names()
                if collections:
                    db_collection_map.append((db_name, collections))
                else:
                    console.print(f"[bold yellow]No collections found in database {db_name} or insufficient permissions.[/bold yellow]")
            except errors.OperationFailure:
                pass
        return db_collection_map
    except errors.OperationFailure:
        console.print("[bold yellow]Insufficient permissions to list databases.[/bold yellow]")
        return []
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred while listing databases: {str(e)}[/bold red]")
        return []

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
                    header = list(set(header) | set(document.keys()))
                    file.seek(0)
                    writer = csv.DictWriter(file, fieldnames=header)
                    writer.writeheader()
                writer.writerow({k: document.get(k, '') for k in header})
                row_count += 1
        return row_count
    except errors.OperationFailure:
        console.print(f"[bold red]Error: Insufficient permissions to dump collection '{collection_name}'.[/bold red]")
        return -1
    except Exception as e:
        console.print(f"[bold red]Error dumping collection {collection_name}: {str(e)}[/bold red]")
        return -1

def dumpAllCol(client, ip, db_collection_map):
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Database Name", style="bold magenta")
    table.add_column("Number of Collections", style="bold cyan")
    table.add_column("Status", style="bold green")
    total_databases = 0
    total_collections = 0
    total_rows = 0
    statuses = []

    for db_name, collections in db_collection_map:
        table.add_row(db_name, str(len(collections)), "[bold yellow]In progress...[/bold yellow]")
        statuses.append("[bold yellow]In progress...[/bold yellow]")

    with Live(table, console=console, refresh_per_second=4) as live:
        for row_num, (db_name, collections) in enumerate(db_collection_map):
            db = client[db_name]
            database_rows = 0
            collections_dumped = 0
            collections_failed = 0
            collections_empty = 0
            for collection in collections:
                row_count = dumpCol(db, collection, ip)
                if row_count > 0:
                    total_collections += 1
                    collections_dumped += 1
                    database_rows += row_count
                elif row_count == 0:
                    collections_empty += 1
                else:
                    collections_failed += 1
            
            if collections_dumped + collections_empty == len(collections):
                total_databases += 1
                status = f"[bold green][DUMPED {collections_dumped}/{len(collections)}][/bold green]"
            else:
                status = f"[bold red][FAILED {collections_failed}/{len(collections)}][/bold red]"
            
            if collections_empty > 0:
                status += f" [bold yellow][EMPTY {collections_empty}][/bold yellow]"
            
            total_rows += database_rows
            
            statuses[row_num] = status
            
            new_table = Table(show_header=True, header_style="bold cyan")
            new_table.add_column("Database Name", style="bold magenta")
            new_table.add_column("Number of Collections", style="bold cyan")
            new_table.add_column("Status", style="bold green")
            
            for i, ((db_name, collections), status) in enumerate(zip(db_collection_map, statuses)):
                new_table.add_row(db_name, str(len(collections)), status)
            
            live.update(new_table)

    return total_databases, total_collections, total_rows

def connect_to_mongodb(ip, username, password):
    connection_strings = [
        f'mongodb://{username}:{password}@{ip}:27017/?authSource=admin',
        f'mongodb://{username}:{password}@{ip}:27017/'
    ]
    
    for connection_string in connection_strings:
        try:
            client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            client.server_info()
            return client
        except (errors.OperationFailure, errors.ServerSelectionTimeoutError, Exception):
            continue
    
    return None

def attempt_login_and_dump(ip, username, password, is_initial=False):
    client = connect_to_mongodb(ip, username, password)
    if client:
        if is_initial:
            console.print(f"[bold green]Connected to MongoDB instance at {ip}.[/bold green]")
        console.print(f"[bold green]Successfully logged in with username: {username}[/bold green]")
        db_collection_map = list_db_col(client)
        if db_collection_map:
            console.print("\n[bold cyan]Dumping...[/bold cyan]")
            total_databases, total_collections, total_rows = dumpAllCol(client, ip, db_collection_map)
            console.print(f"\n[bold green]{total_databases} Databases | {total_collections} Collections | {total_rows} Rows Successfully Dumped.[/bold green]")
            client.close()
            return True
        else:
            console.print("[bold yellow]No accessible databases or collections found. This may be due to limited permissions.[/bold yellow]")
            client.close()
    return False

def main():
    console.print("[bold magenta]MongoDB Database Dumper Tool [v1.8][/bold magenta]")
    ip = Prompt.ask("[bold bright_white]Enter MongoDB IP address[/bold bright_white]", default="localhost")
    initial_username = Prompt.ask("[bold bright_white]Username[/bold bright_white]", default="admin")
    initial_password = Prompt.ask("[bold bright_white]Password[/bold bright_white]", password=True)

    # 1. Attempt initial connection and login
    client = connect_to_mongodb(ip, initial_username, initial_password)
    if client:
        console.print(f"[bold green]Connected to MongoDB instance at {ip}.[/bold green]")
        console.print(f"[bold green]Successfully logged in with username: {initial_username}[/bold green]")
        db_collection_map = list_db_col(client)
        if db_collection_map:
            console.print("\n[bold cyan]Starting dumper...[/bold cyan]")
            total_databases, total_collections, total_rows = dumpAllCol(client, ip, db_collection_map)
            console.print(f"\n[bold green]{total_databases} Databases | {total_collections} Collections | {total_rows} Rows Successfully Dumped.[/bold green]")
            client.close()
            return
        else:
            console.print("[bold red][!] No accessible databases. Permission error.[/bold red]")
            console.print("[bold yellow]Attempting to retrieve user list.[/bold yellow]")
        users = get_admin_users(client)
        if users:
            display_users_grid(users)
            console.print("\n[bold yellow]Attempting to log in as other users.[/bold yellow]")
            for user in users:
                username = user.get("user")
                if username != initial_username:
                    if attempt_login_and_dump(ip, username, initial_password):
                        client.close()
                        return
                    if attempt_login_and_dump(ip, username, username):
                        client.close()
                        return
            console.print("[bold red]Failed to dump databases with any available username.[/bold red]")
        else:
            console.print("[bold yellow]Unable to retrieve user information from admin database.[/bold yellow]")
        
        client.close()
    else:
        console.print("[bold red]Failed to connect to MongoDB. Please check your credentials and try again.[/bold red]")

if __name__ == "__main__":
    main()
