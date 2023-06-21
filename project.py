'''
CS50P Introduction to Programming with Python
Final Project: Anime-Tracker
Name: Abhiram Sadanand Chinta
From: Solapur, Maharashtra, India
Github: https://github.com/Abhiram-044
LinkedIn: https://www.linkedin.com/in/abhiram-chinta-221806238/
'''

from bs4 import BeautifulSoup
import csv
import requests
import re
from tabulate import tabulate
import sys
import pyfiglet

def main():
    print(pyfiglet.figlet_format("Welcome To Anime-Tracker!!", font="slant"))
    # asks for user_id and if no user_id creates the csv file with the user_id as name
    q1 = input("Do you have a User ID?[yes(1) no(2)]: ")
    try:
        query = int(q1)
    except (ValueError):
        print("Enter valid input")
        pass
    if query == 1:
        user_id = input("Enter User ID: ").replace(' ', '_')
        user_csv = user_id + '.csv'
    elif query == 2:
        user_id = input("Enter New Username: ").replace(' ', '_')
        user_csv = create_user(user_id)
    else:
        print("Enter Valid Input")
        pass
    options = [{"action": "display top anime" , "key": "T" },
               {"action": "search anime" , "key": "S" },
               {"action": "add anime to list" , "key": "A" },
               {"action": "display your list" , "key": "D" },
               {"action": "update status of anime" , "key": "U"},
               {"action": "exit", "key": "E"}]
    # Displays the queries(options) in tabulate and executes actions as per the input and starts over if any ERROR encountered
    while True:
        display(options)
        query = input("Enter Query: ").upper()
        match query:
            case "T":
                animes = top()
                display(animes)
            case "S":
                query = input("Search Anime: ")
                animes = search(query)
                display(animes)
            case "A":
                try:
                    id1 = int(input("Enter Id of Anime to add: "))
                except (ValueError):
                    print("Enter Valid Id")
                    continue
                else:
                    anime = animes[id1-1]
                    try:
                        user_rate = int(input(f"Enter Rating for {anime['title']}: "))
                    except (ValueError):
                        print("Enter Valid rating[1-10]: ")
                        continue
                    else:
                        statuses = ["Watching", "Completed", "Dropped", "Plan to Watch"]
                        status = int(input("Enter Status[1.Watching, 2.Completed, 3.Dropped, 4.Plan to Watch]: "))
                        added = add_list(user_csv ,animes[id1-1], user_rate, statuses[status-1])
                        print(added)
            case "D":
                with open(user_csv, mode='r') as f:
                    data = csv.DictReader(f)
                    display(data)
            case "U":
                try:
                    id2 = int(input("Enter Id to Update: "))
                except (ValueError):
                    print("Enter Valid Id")
                    continue
                else:
                    statuses = ["Watching", "Completed", "Dropped", "Plan to Watch"]
                    try:
                        status = int(input("Enter updated Status[1.Watching, 2.Completed, 3.Dropped, 4.Plan to Watch]: "))
                    except (ValueError):
                        print("Enter Valid Input")
                        continue
                    else:
                        updated = update_status(user_csv, id2, statuses[status-1])
                        print(updated)
            case "E":
                sys.exit(pyfiglet.figlet_format("Thanks for Using Anime-Tracker!!", font="slant"))
            case _:
                print("Enter Valid Input")
                pass


# Displays the data in tabulate form
def display(data):
    print(tabulate(data, headers="keys", tablefmt="grid"))


# Returns an list of dict containing the top 50 anime
def top():
    url="https://myanimelist.net/topanime.php" # website from where the top shows are scraped from
    link = requests.get(url)
    soup = BeautifulSoup(link.text, "lxml")
    anime_html = soup.find_all("tr", class_="ranking-list") # Finds all <tr> tags with "ranking-list" class that has information of the shows
    animes = []
    id = 1
    for anime in anime_html:
        title = anime.find("h3", class_="hoverinfo_trigger fl-l fs14 fw-b anime_ranking_h3").find_next("a").text # Scraps the Title of the show from the anchor tag present in h3
        spans = anime.find_all("span") # finds all span tags
        for span in spans:
            classes = ' '.join(span.attrs["class"]) #Collects the class names of span tags
            if re.match(r"text on score-label score-[0-9]", classes): #Check if it matches the regular expression
                rating = span.text
        animes.append(
            {
                "id": id,
                "title": title,
                "rating": rating
            }
        ) # appends the shows id, title, rating as dict to a list
        id += 1
    return animes


# Searches the query and returns the top 15 searches list of dict
def search(q):
    query = q.replace(' ', '+')
    url = f"https://myanimelist.net/anime.php?q={query}&cat=anime" # Search link where the top results are scraped from
    link = requests.get(url)
    soup = BeautifulSoup(link.text, "lxml")
    div = soup.find("div", class_="js-categories-seasonal js-block-list list").find_next("tr")
    anime_html = div.find_next_siblings("tr") # Finds all the <tr> tags inside the div
    animes = []
    id = 1
    for anime in anime_html[:15]: # Iterates only the first 15 shows
        title = anime.find("a", class_="hoverinfo_trigger fw-b fl-l").text # Scraps the title of the show from anchor tag
        rating = anime.find("td", class_=f"borderClass ac bgColor{num(id)}", width="50").text.strip() # Scraps the rating from the <td>
        animes.append(
            {
                "id": id,
                "title": title,
                "rating": rating
            }
        ) # Appends the show details as dict to the list
        id += 1
    return animes


# A func for returning 0 or 1 for changing class names of the element
def num(id):
    if id%2 == 0:
        return 1
    else:
        return 0


# Creates a user_csv with the headers and file_name as user_id and returns the filename
def create_user(user_id):
    user_csv = user_id + '.csv'
    user_csv = user_csv.lower()
    with open(user_csv, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "user_rate", "status"])
        writer.writeheader()
    return user_csv


# Adds the anime to the user list with user_rating and status of anime
def add_list(user_csv, anime, user_rate, status):
    reader = csv.reader(open(user_csv))
    id1 = len(list(reader))
    with open(user_csv, "a") as f:
        writer = csv.DictWriter(f, fieldnames=["id" ,"title", "user_rate", "status"])
        writer.writerow({"id": id1, "title": anime["title"], "user_rate": user_rate, "status": status})
        added = {"id": id1, "title": anime["title"], "user_rate": user_rate, "status": status}
    return f"Added Element: {added}"


# Changes the status of the anime in the list with querying the id of the anime
def update_status(user_csv, id, status):
    updated_rows = []
    with open(user_csv, "r") as f:
        reader = csv.DictReader(f, fieldnames=["id" ,"title", "user_rate", "status"])
        for i, row in enumerate(reader):
            if i == id:
                updated_rows.append({'id': id, 'title': row['title'], 'user_rate': row['user_rate'], 'status': status})
            else:
                updated_rows.append(row)
    with open(user_csv, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["id" ,"title", "user_rate", "status"])
        for row in updated_rows:
            writer.writerow(row)
    return f"Updated status of {id}ID: {status}"

if __name__ == "__main__":
    main()