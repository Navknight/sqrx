from websockets.sync.client import connect
import json

def print_json(json_data):
    print(json.dumps(json_data, indent=4, sort_keys=True))

if __name__ == "__main__":
    with connect('ws://localhost:5000/ws') as ws:
        url = "www.wikipedia.com"
        ws.send(json.dumps({"url": url}))
        response = ws.recv()
        print_json(json.loads(response))
        
        while True:
            print("\nMenu:")
            print("1. Set URL")
            print("2. Get Info")
            print("3. Get Subdomains")
            print("4. Get Asset Domains")
            print("5. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                url = input("Enter URL: ")
                ws.send(json.dumps({"url": url}))
                message = ws.recv()
                print_json(json.loads(message))
            elif choice == "2":
                ws.send(json.dumps({"operation": "get_info"}))
                message = ws.recv()
                print_json(json.loads(message))
            elif choice == "3":
                ws.send(json.dumps({"operation": "get_subdomains"}))
                message = ws.recv()
                print_json(json.loads(message))
            elif choice == "4":
                ws.send(json.dumps({"operation": "get_asset_domains"}))
                message = ws.recv()
                print_json(json.loads(message))
            elif choice == "5":
                ws.close()
                break
            else:
                print("Invalid choice, please try again.")
