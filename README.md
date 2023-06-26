# Anime-Tracker
A command-line interface Anime-tracker using python for keeping the track of the all the animes You Watch

---

## Requirements
-Use pip for installation of required modules
```
$ pip install - requirements.txt
```
-Stable Internet Connection is required

---

## Libraries Used
* ```requests```: used to sent GET request to the  [url](https://myanimelist.net/topanime.php)

* ```beautifulsoup4```: for scraping the anime data that is title, rating of the show

* ```tabulate```: for printing the data such as the top anime, search results and user_data

* ```lxml```: for HTML parser

* ```pyfiglet```: for rendering fancy text

---

## Usage
* To clone the repository
```
$ git clone git@github.com:Abhiram-044/Anime-Tracker.git
```

* Use python to run the program/application
```
$ python project.py
```

## Documentation
* ```create_user(user_id)```:
    * In this function a new user_id is passed as an argument to create a csv file of same name if there is a space in the name it is replaced with '_'.
    * While Creating the csv files the headers are writen in the .csv file.

* ```top()```:
    * In this function this a GET request is sent to this website [https://myanimelist.net/topanime.php].
    * Then all the top 50 animes details['id', 'title', 'rating'] are scraped and stored in dict using ```BeautifulSoup()``` and its different methods.
    * This list of dict is returned.

* ```search(query)```:
    * In this function a string query is passed and all the spaces are replaced with '+' and put in this url(https://myanimelist.net/anime.php?q={query}&cat=anime) where query is the search input. Then a GET request is sent to this website.
    * Then the top 15 results are scraped to get the details['id', 'title', 'rating'] using ```BeautifulSoup()```.
    * The results are stores as dict and all the results are returned in a list of dict.

* ```add_list(user_csv, anime, user_rate, status)```:
    * In this function a string user_csv, anime, user_rate, status is passes where user_csv is the file where the data needs to be added, anime is the that needs to be stored in user_csv, user_rate is the user_rating for the show, status is string that can be either if ['Watching', 'Completed', 'Dropped', 'Plan to Watch'].
    * The details as per user input are stored then a dict that has been stored in csv is returned.

* ```update_status(user_csv, id, status)```:
    * In this function the status of the given id in user_csv is changed as per input.
    * After Changing the status the Updated status of the Id is returned.

* ```is_anime_incsv(user_csv, anime)```:
    * This fuction checks if the anime is present in the users list.
    * If the anime is present in the list it returns the integer id of anime and then it is passes through ```update_status()``` and if anime not in list returns 0.

* ```display(data)```:
    * It displays the given data which is list of dictionaries in grid format using tabulate

---

## References
* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [Tabulate](https://pypi.org/project/tabulate/)
* [csv](https://docs.python.org/3/library/csv.html)
* [pyfiglet](https://www.javatpoint.com/python-pyfiglet-module)