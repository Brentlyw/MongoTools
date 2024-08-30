import shodan

SHODAN_API_KEY = ''
QUERY = 'port:27017 "MongoDB Server Information" -authentication country:US'

def search_shodan(api_key, query):
    api = shodan.Shodan(api_key)
    page = 1
    try:
        with open("shodan_ips.txt", "w") as file:
            while True:
                results = api.search(query, page=page)
                if not results['matches']:
                    break
                for result in results['matches']:
                    ip = result['ip_str']
                    file.write(f"{ip}\n")
                print(f"Page {page}: Retrieved {len(results['matches'])} results and saved to shodan_ips.txt.")
                page += 1  # Always move to the next page
    except shodan.APIError as e:
        print(f"Error: {e}")

def main():
    search_shodan(SHODAN_API_KEY, QUERY)
    print("All done. All IP addresses saved to shodan_ips.txt.")

if __name__ == "__main__":
    main()
