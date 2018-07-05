# Disclaimer #
**This utility can be used to download the contents of books from scribd. This tool is not to be used to download books in which you don't already own a copy. Any illegal use of this tool will not hold the developer responsible. Even if you own the book in one form or another, downloading the contents directly from their API might be considered a violation of their ToS. The author of this tool has not dived into the legal ramifications and would encourage caution in using this.
Also, this tool requires that you have an active scribd subscription (it asks you for a token upon each use and scribd does not allow you to download the content without one). Free trials can be used, but I recommend everyone subscribe to this service as it's a great tool that provides an interesting way to digest the contents of your library in a completely DRM-free way - whether this be intentional or not.**

# What is it? #
Tool to download the text content of books from scribd. From what I understand only documents can be downloaded *easily* with an available download button, but books can not be read offline (on your PC at least). This tool grabs the contents and makes a local copy using HTML syntax.

# How does it work? #
Scribd stores the content of books in a .json format and passes it to the client as you progress through the different pages. For example, if you open a book on scribd it will download the first chapter from /resource_id/

# How do I use it? #
1. Open browser, browse to scribd.com, and login using a valid subscription.
2. Find a book that you want to download and 'Start Reading'
3. Identify the resource_id in the URL of the page and store it somewhere. Example: ![alt text](https://raw.githubusercontent.com/christiancoleman/scribd_book_downloader/master/resource_id_example.png "Resource id example")
4. (finding the token - there might be a better way to do this but it has worked for me so far) Find an image in the book (good place to find these is on the first page), right-click-> View image. Identify the token in the URL and store it somewhere. Example: ![alt text](https://raw.githubusercontent.com/christiancoleman/scribd_book_downloader/master/token_example.png "Token example")
5. (Using python 2.7) Run *'python main.py'* and fill out the prompt correctly
*Things to note, the token expires pretty quickly - like 5 minutes. So refresh your browser if you get a 401 Unauthorized and try again if it happens.*

# TODO #
* The content of the books are still very, very ugly in terms of how they are presented via HTML. Clean this up. Make it beautiful and easy to browse the content. Consider using a different book viewing syntax like LaTeX.
* Find a way to automate the promt() part of the program by scanning the contents of the dir with the book name.
* Find a way to generate a token without having to grab it manually.
