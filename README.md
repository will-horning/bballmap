This app is designed to graph a rough probability distribution of a basketball player's local shooting percentage (i.e. their shooting percentage from a 1-foot x 1-foot location on the court).

![Kobe Bryant example](/kobe_example.gif "Example (Kobe Bryant):")

All the data is stored in shots.db, it was scraped from cbssports.com and contains every shot taken in an NBA game from 2011 - 2013. 

An older version is available [here](http://willhorning.pythonanywhere.com). 

How to Run:
===========

		virtualenv .env
		. .env/bin/activate
		pip install -r requirements.txt
		python main.py

Then just point your browser to http://localhost:5000
