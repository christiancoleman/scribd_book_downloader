# Disclaimer #
** *This utility can be used to download the contents of books from scribd. This tool is not to be used to download books in which you don't already own a phyiscal copy. Any illegal use of this tool will not hold the developer responsible.
Also, *this tool requires that you have an active scribd subscription (it asks you for a token upon each use and scribd does not allow you to download the content without one). Free trials can be used, but I recommend everyone subscribe to this service as it's a great tool that provides an interesting way to digest the contents of your library in a completely DRM-free way - whether this be intentional or not.* **

# What is it? #
Tool to download the text content of books from scribd. From what I understand only documents can be downloaded *easily* with an available download button, but books can not be read offline (on your PC at least). This tool grabs the contents and makes a local copy using HTML syntax.

# How does it work? #
Scribd stores the content of books in a .json format and passes it to the client as you progress through the different pages. For example, if you open a book on scribd it will download the first chapter from /resource_id/

# How do I use it? #

# TODO #
* The content of the books are still very, very ugly in terms of how they are presented via HTML. Clean this up. Make it beautiful and easy to browse the content. Consider using a different book viewing syntax like LaTeX.
* Find a way to automate the promt() part of the program by scanning the contents of the dir with the book name.
* Find a way to generate a token without having to grab it manually.
