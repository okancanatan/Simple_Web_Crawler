# Simple Web Crawler
Simple web crawler that creates a database of common words 

How it works:
It parses an websites HTML code and looks for HREF links to other websites. It cleans those up and visits them, finding more links, and so on.
When it visits them, it looks at the most common words, unique words, common bigrams and trigrams (2 letter and 3 letter phrases) and adds them all to sql database.

You can toggle the file saving into the Websites folder, default is off

Future Plans:
- Multithreading
- Self Hosted Search Enging (it'd probably be kinda eh but could be cool)

