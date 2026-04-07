# Flight Analytic Tool 

A Python application that uses Duffel Air API to analyze real-time flights based on user budgets and travel preferences. 

## Features 

* Live-time Search: Is connected to a live airline data API.
* Flitering: Sorts and groups flights by displaying the prices of all the airlines on the same routes, allowing for a comparison of all available ticket prices between marketing and operating airlines.
* Duration logic: convert ISO 8601 duration string into human readable formats
* Routing: Can handle both one-way and round-trip searches
* Class Selection: User can pick their class prefrence of Economy,Premium, Business, or First Class. 


* Language: Python
* API Integration: The requests library for RESTful communication. 
* Security: Used a .env file to secure the keys to avoid risk with API credits.
* Data Processing: datetime for ISO string and time formatting. 
