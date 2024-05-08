from bs4 import BeautifulSoup
import sqlite3
import maskpass
import requests
import re
from tabulate import tabulate
import sys
import pyfiglet
from recommender import find_similar_animes

# Connects to the database
conn = sqlite3.connect("database.db")


def main():
    print(pyfiglet.figlet_format("Welcome To Anime-Tracker!!", font="slant"))
    # asks for user_id and password and if no user_id creates the table in database with the user_id as name
    q1 = input("Do you have a User ID?[yes(1) no(2)]: ")
    try:
        query = int(q1)
    except ValueError:
        print("Enter valid input")
        pass
    if query == 1:
        cursor = conn.execute("SELECT * FROM USERS;")
        flag = -1
        check = ""
        while flag == -1:
            user_table = input("Enter User ID: ").lower()
            for i, x in enumerate(cursor):
                if user_table.lower() == str(x[0]).lower():
                    flag = i
                    check = x[1]
                    break
        while True:
            password = maskpass.askpass("Enter Password: ", "#")
            if password == check:
                break
        
    elif query == 2:
        user_id = input("Enter New Username: ")
        while True:
            password = maskpass.askpass("Enter a Password: ", "#")
            if len(password) > 10 or len(password) < 6:
                continue
            check = maskpass.askpass("Re-Enter the Password: ", "#")
            if password == check:
                break
            else:
                print("Enter Same Password for both")
        user_table = create_user(user_id.lower(), password)
    else:
        print("Enter Valid Input")
        pass
    options = [
        {"action": "display top anime", "key": "T"},
        {"action": "search anime", "key": "S"},
        {"action": "add anime to list", "key": "A"},
        {"action": "display your list", "key": "D"},
        {"action": "update status of anime", "key": "U"},
        {"action": "Recommend based off last watched", "key": "R"},
        {"action": "exit", "key": "E"},
    ]
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
                    ids = map(int, (input("Enter Id of Anime to add: ").split()))
                except ValueError:
                    print("Enter Valid Id")
                    continue
                else:
                    id_list = list(ids)
                    statuses = ["Watching", "Completed", "Dropped", "Plan to Watch"]
                    while True:
                        for id1 in id_list:
                            anime = animes[id1 - 1]
                            present_id = is_anime_in_table(user_table, anime)
                            if present_id != 0:
                                while True:
                                    try:
                                        status = int(
                                            input(
                                                "Enter Updated Status[1.Watching, 2.Completed, 3.Dropped, 4.Plan to Watch]: "
                                            )
                                        )
                                        status1 = statuses[status - 1]
                                    except (ValueError, IndexError):
                                        print("Enter Valid Input")
                                        continue
                                    else:
                                        updated = update_status(
                                            user_table, present_id, status1
                                        )
                                        print(updated)
                                        break
                                continue
                            while True:
                                try:
                                    user_rate = int(
                                        input(f"Enter Rating for {anime['title']}: ")
                                    )
                                    if user_rate > 10 or user_rate < 0:
                                        raise ValueError
                                except ValueError:
                                    print("Enter Valid rating[1-10]: ")
                                    continue
                                else:
                                    try:
                                        status = int(
                                            input(
                                                "Enter Status[1.Watching, 2.Completed, 3.Dropped, 4.Plan to Watch]: "
                                            )
                                        )
                                        status1 = statuses[status - 1]
                                    except (ValueError, IndexError):
                                        print("Enter Valid Input")
                                        continue
                                    else:
                                        added = add_list(
                                            user_table,
                                            animes[id1 - 1],
                                            user_rate,
                                            status1,
                                        )
                                        print(added)
                                        break
                        break
            case "D":
                data = list()
                cursor = conn.execute(f"SELECT * FROM {user_table}")
                for i in cursor:
                    data.append(
                        {
                            "id": int(i[0]),
                            "title": str(i[1]),
                            "user_rate": int(i[2]),
                            "status": str(i[3]),
                        }
                    )
                display(data)
            case "U":
                try:
                    id2 = int(input("Enter Id to Update: "))
                except ValueError:
                    print("Enter Valid Id")
                    continue
                else:
                    statuses = ["Watching", "Completed", "Dropped", "Plan to Watch"]
                    try:
                        status = int(
                            input(
                                "Enter updated Status[1.Watching, 2.Completed, 3.Dropped, 4.Plan to Watch]: "
                            )
                        )
                        status1 = statuses[status - 1]
                    except (ValueError, IndexError):
                        print("Enter Valid Input")
                        continue
                    else:
                        updated = update_status(user_table, id2, status1)
                        print(updated)
            case "E":
                sys.exit(
                    pyfiglet.figlet_format(
                        "Thanks for Using Anime-Tracker!!", font="slant"
                    )
                )
            case "R":
                row = conn.execute(
                    f"""
                    SELECT * FROM {user_table}
                    ORDER BY ID DESC
                    LIMIT 1;
                    """
                    )
                for i in row:
                    anime_name = str(i[1])
                recommendations = find_similar_animes(anime_name)
                display(recommendations)
            case _:
                print("Enter Valid Input")
                pass


# Displays the data in tabulate form
def display(data):
    print(tabulate(data, headers="keys", tablefmt="grid"))


# Returns an list of dict containing the top 50 anime
def top():
    url = "https://myanimelist.net/topanime.php"  # website from where the top shows are scraped from
    link = requests.get(url)
    soup = BeautifulSoup(link.text, "lxml")
    anime_html = soup.find_all(
        "tr", class_="ranking-list"
    )  # Finds all <tr> tags with "ranking-list" class that has information of the shows
    animes = []
    id = 1
    for anime in anime_html:
        title = (
            anime.find("h3", class_="fl-l fs14 fw-b anime_ranking_h3")
            .find_next("a")
            .text
        )  # Scraps the Title of the show from the anchor tag present in h3
        spans = anime.find_all("span")  # finds all span tags
        for span in spans:
            classes = " ".join(
                span.attrs["class"]
            )  # Collects the class names of span tags
            if re.match(
                r"text on score-label score-[0-9]", classes
            ):  # Check if it matches the regular expression
                rating = span.text
        animes.append(
            {"id": id, "title": title, "rating": rating}
        )  # appends the shows id, title, rating as dict to a list
        id += 1
    return animes


# Searches the query and returns the top 15 searches list of dict
def search(q):
    query = q.replace(" ", "+")
    url = f"https://myanimelist.net/anime.php?q={query}&cat=anime"  # Search link where the top results are scraped from
    link = requests.get(url)
    soup = BeautifulSoup(link.text, "lxml")
    div = soup.find(
        "div", class_="js-categories-seasonal js-block-list list"
    ).find_next("tr")
    anime_html = div.find_next_siblings("tr")  # Finds all the <tr> tags inside the div
    animes = []
    id = 1
    for anime in anime_html[:15]:  # Iterates only the first 15 shows
        title = anime.find(
            "a", class_="hoverinfo_trigger fw-b fl-l"
        ).text  # Scraps the title of the show from anchor tag
        rating = anime.find(
            "td", class_=f"borderClass ac bgColor{num(id)}", width="50"
        ).text.strip()  # Scraps the rating from the <td>
        animes.append(
            {"id": id, "title": title, "rating": rating}
        )  # Appends the show details as dict to the list
        id += 1
    return animes


# A func for returning 0 or 1 for changing class names of the element
def num(id):
    if id % 2 == 0:
        return 1
    else:
        return 0


# Creates a user_table with the headers and file_name as user_id and returns the filename
def create_user(user_id, password):
    conn.execute(f"INSERT INTO Users VALUES (?, ?);", (user_id, password))
    conn.commit()
    conn.execute(
        f"""CREATE TABLE {user_id}
            (ID INTEGER,
            Title VARCHAR(250),
            User_Rate INTEGER,
            Status CHAR(15))"""
    )
    conn.commit()
    return user_id


# Adds the anime to the user list with user_rating and status of anime
def add_list(user_table, anime, user_rate, status):
    count = conn.execute(f"SELECT COUNT (*) FROM {user_table};")
    for i in count:
        id = int(i[0]) + 1
    conn.execute(
        f"INSERT INTO {user_table} VALUES (?, ?, ?, ?);",
        (id, anime["title"], user_rate, status),
    )
    conn.commit()
    added = {
        "id": id,
        "title": anime["title"],
        "user_rate": user_rate,
        "status": status,
    }
    return f"Added Element: {added}"


# Changes the status of the anime in the list with querying the id of the anime
def update_status(user_table, id, status):
    conn.execute(f"UPDATE {user_table} set Status = ? WHERE ID = ?", (status, id))
    conn.commit()
    return f"Updated status of {id}ID: {status}"


def is_anime_in_table(user_table, anime):
    cursor = conn.execute(f"SELECT * FROM {user_table};")
    for x in cursor:
        if str(x[1]) == anime["title"]:
            return int(x[0])    
    return 0


if __name__ == "__main__":
    main()

conn.close()