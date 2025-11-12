import requests

def fetch_users():
    url = "https://jsonplaceholder.typicode.com/users"

    try:
        
        response = requests.get(url)

        
        if response.status_code == 200:
            users = response.json()

            if not users:
                print("No users found.")
                return

            print("Fetched Users:\n")

            count = 1
            for user in users:
                name = user.get("name")
                username = user.get("username")
                email = user.get("email")
                city = user.get("address", {}).get("city")

                # BONUS: Only print users whose city starts with 'S'
                if city and city.startswith("S"):
                    print(f"User {count}:")
                    print(f"Name: {name}")
                    print(f"Username: {username}")
                    print(f"Email: {email}")
                    print(f"City: {city}")
                    print("-" * 30)
                    count += 1

        else:
            print(f"Failed to fetch data. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


# Run the function
if __name__ == "__main__":
    fetch_users()
