# Simple Web Crawler
Simple web crawler that creates a database of common words 

How it works:
It parses an websites HTML code and looks for HREF links to other websites. It cleans those up and visits them, finding more links, and so on.
When it visits them, it looks at the most common words, unique words, common bigrams and trigrams (2 letter and 3 letter phrases) and adds them all to sql database.

You can toggle the file saving into the Websites folder, default is off
It deletes the db file each time, would reccomend moving it before starting it again. 

Future Plans:
- Multithreading
- Respecting Robots.txt (Really a requirement tbh... keep in mind while running that this isn't available right now)

