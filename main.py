import json
import os
import sys
import urllib2

SCRIBD_BASE_URL = "https://www.scribd.com/scepub/{resource_id}"
SCRIBD_CHAPTERS_URL = "/{chapter_path}"
SCRIBD_TOC_URL = "/toc.json?token={token}"
SCRIBD_CONTENT_URL = "/contents.json?token={token}"
SCRIBD_IMAGE_URL = "/{filename}?token={token}"
TAB_CHAR = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
PATH_FOR_BOOKS = "books"
HTML_TOP_ALL_PAGES = """
<!doctype html>
<html lang="en">
    <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css" integrity="sha384-WskhaSGFgHYWDcbwN70/dfYBj47jz9qbsMId/iRN3ewGhXQFZCSftd1LZCfmhktB" crossorigin="anonymous">
    </head>
    <body>
        <div class="container">
"""
HTML_BOTTOM_ALL_PAGES = """
        </div>
        <!-- Optional JavaScript -->
        <!-- jQuery first, then Popper.js, then Bootstrap JS -->
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/js/bootstrap.min.js" integrity="sha384-smHYKdLADwkXOn1EmN1qk/HfnUcbVRZyYmZ4qpPea6sjB/pTJ0euyQp0Mk8ck+5T" crossorigin="anonymous"></script>
    </body>
</html>
"""


def main():
    global local_name_of_book_directory
    global resource_id
    global token
    if len(sys.argv) == 2:
        local_name_of_book_directory = sys.argv[1]
        print "Creating book from already downloaded json data..."
        create_book('y', 'y')
    elif len(sys.argv) == 4:
        local_name_of_book_directory = sys.argv[1]
        resource_id = sys.argv[2]
        token = sys.argv[3]
        print "Creating book from already downloaded json data BUT downloading image data..."
        create_book('y', 'n')
    else:
        prompt()


#######################################################################################################################


def prompt():
    print "###########################################"
    print "Welcome to the scribd BOOK downloading utility..."
    print "###########################################"
    print "Use: python main.py"
    print "You will need the answers to the following:"
    print "\tHave you downloaded the json files (text content of book) locally yet?"
    print "\tHave you downloaded the images locally yet?"
    print "\tWhat directory should we use?"
    print "\tWhat is the book's resource id?"
    print "\tWhat is your scribd token? (this expires fast, but should last long enough to download a single book)"
    print
    print "Other uses:"
    print "python main.py {name_of_books_folder}"
    print "\t Uses local data only. Need to have run the program once before. Uses json already on PC."
    print
    print "python main.py {name_of_books_folder} {resource_id} {token}"
    print "\t Used to download images only while relying on already downloaded JSON data describing where everything is"

    global resource_id
    global token

    use_local_json = raw_input("Use local json files? (y or n): ")
    if use_local_json != "y" and use_local_json != "n":
        print "Only y or n is accepted..."
        return -1

    images_downloaded = raw_input("Images already downloaded? (y or n): ")
    if images_downloaded != "y" and images_downloaded != "n":
        print "Only y or n is accepted..."
        return -1

    global local_name_of_book_directory
    local_name_of_book_directory = raw_input("What directory should we download the book? (Ex: potato_book): ")

    if use_local_json == "n" or images_downloaded == "n":
        resource_id = raw_input("Enter resource id: ")
        token = raw_input("Enter your token: ")

    print "Creating book..."
    create_book(use_local_json, images_downloaded)


def create_book(use_local_json, images_downloaded):
    global resource_id
    global token

    html_all_content = HTML_TOP_ALL_PAGES
    html_toc_content = HTML_TOP_ALL_PAGES + '<h1>Table of Contents</h1>'

    if use_local_json == "y":
        toc_json_string = read_json_from_disk("{PATH_FOR_BOOKS}/{dir}/toc.json".format(PATH_FOR_BOOKS=PATH_FOR_BOOKS, dir=local_name_of_book_directory))
    else:
        toc_json_string = download_toc_from_scribd()
        
    toc_list = create_toc_from_json(toc_json_string)

    for toc_item in toc_list:
        if use_local_json == "y":
            chapter_raw = read_json_from_disk("{PATH_FOR_BOOKS}/{dir}/{toc_item}.json".format(PATH_FOR_BOOKS=PATH_FOR_BOOKS, dir=local_name_of_book_directory, toc_item=toc_item))
        else:
            chapter_raw = download_chapter_from_scribd(toc_item)
            save_file(toc_item, chapter_raw, "json")

        html_toc_content += create_toc_from_item("{toc_item}.html".format(toc_item=toc_item))
        html_chapter_content = create_chapter_from_json(chapter_raw, toc_item, images_downloaded)
        html_all_content += html_chapter_content
        html_chapter_content = HTML_TOP_ALL_PAGES + html_chapter_content + HTML_BOTTOM_ALL_PAGES
        save_file(toc_item, html_chapter_content, "html")

    html_toc_content += HTML_BOTTOM_ALL_PAGES
    html_all_content += HTML_BOTTOM_ALL_PAGES
    html_all_content = html_all_content.replace('../images/', 'images/')

    save_file("toc", html_toc_content, "html")
    save_file("all", html_all_content, "html")

#######################################################################################################################


def download_toc_from_scribd():
    print "Downloading the table of contents..."
    global resource_id
    global token
    download_url = SCRIBD_BASE_URL.format(resource_id=resource_id)
    download_url += SCRIBD_TOC_URL.format(token=token)
    return urllib2.urlopen(download_url).read()


def download_chapter_from_scribd(chapter_path):
    print "Downloading " + chapter_path + "..."
    global resource_id
    global token
    download_url = SCRIBD_BASE_URL.format(resource_id=resource_id)
    download_url += SCRIBD_CHAPTERS_URL.format(chapter_path=chapter_path)
    download_url += SCRIBD_CONTENT_URL.format(token=token)
    return urllib2.urlopen(download_url).read()


def download_image_from_scribd(chapter_path, filename):
    print "Downloading " + chapter_path + "/" + filename + "..."
    global resource_id
    global token
    download_url = SCRIBD_BASE_URL.format(resource_id=resource_id)
    download_url += SCRIBD_CHAPTERS_URL.format(chapter_path=chapter_path)
    download_url += SCRIBD_IMAGE_URL.format(filename=filename, token=token)
    return urllib2.urlopen(download_url)


#####################################################################


def create_toc_from_json(json_string):
    save_file("toc", json_string, "json")

    parsed_json = json.loads(json_string)
    # parsed json is a <list>

    toc_list = []

    for item in parsed_json:
        path = item['filepath']
        toc_list.append(path)

    return toc_list


def create_toc_from_item(chapter_path):
    return "<p><a href=\"" + chapter_path + "\">" + chapter_path + "</a></p>"


def create_chapter_from_json(json_string, chapter_path, images_downloaded):
    html_chapter_content = ''

    save_file(chapter_path, json_string, "json")

    parsed_json = json.loads(json_string)
    # parsed_jason is a <dict> with 'blocks' and 'title' (parsed_json.keys())

    blocks = parsed_json['blocks']
    # blocks is a <list>;

    for block in blocks:
        # each item is a <dict>

        block_type = ''

        try:
            block_type = block['type']
        except KeyError:
            print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
            print 'Failed to get type of block: ' + block
            print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
            pass

        if block_type == 'image':
            image_filename = block['src']
            height = block['height']
            width = block['width']
            if height > 750 or width > 1000:
                height = height / 2
                width = width / 2
            if images_downloaded == "n":
                img_raw = download_image_from_scribd(chapter_path, image_filename)
                save_image(image_filename, img_raw)

            html_chapter_content += "<img src=\"../{img_path}\" height=\"{height}\" width=\"{width}\"/>".format(img_path=image_filename, height=height, width=width)

        elif block_type == 'spacer':

            html_chapter_content += "<p></p>"

        elif block_type == 'page_break':

            html_chapter_content += "<hr>"

        elif block_type == 'row':

            # TODO: what should we do with this?
            html_chapter_content += "<h3>Found 'row' but not sure what to do with this yet</h3>"

        elif block_type == 'border':

            # TODO: what should we do with this?
            html_chapter_content += "<h3>Found 'border' but not sure what to do with this yet</h3>"

        elif block_type == 'text':
            paragraph = ''
            words = block['words']
            # each word in words is a <dict> with individual word along with attributes associated with each word
            for word in words:
                found_word = False
                found_composite = False
                try:
                    paragraph += word['text'] + " "
                    found_word = True
                except KeyError:
                    pass

                if not found_word:
                    try:
                        composite_list = word['words']
                        for composite in composite_list:
                            paragraph += composite['text']
                        found_composite = True
                    except KeyError:
                        pass

                if not found_composite and not found_word:
                    print 'Unexpected type found in block_type = \'text\'' + json.dumps(word)

            html_chapter_content += "<p>" + TAB_CHAR + paragraph + "</p>"

        elif block_type == 'raw':
            html_chapter_content += block['data']

        else:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print 'An unexpected type occurred! Type = ' + block_type
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'

            html_chapter_content += "<h1>UNEXPECTED TYPE (" + block_type + ")</h1>"

    return html_chapter_content


def save_image(image_filename, image_raw):
    full_path_of_file = "{PATH_FOR_BOOKS}/{dir}/".format(PATH_FOR_BOOKS=PATH_FOR_BOOKS, dir=local_name_of_book_directory) + image_filename
    create_path_if_doesnt_exist(cut_off_end_of_directory_string(full_path_of_file))
    i = open(full_path_of_file, "wb")
    i.write(image_raw.read())
    i.close()


def save_file(filename, content, file_extension):
    full_path_of_file = "{PATH_FOR_BOOKS}/{dir}/{filename}.{file_extension}".format(PATH_FOR_BOOKS=PATH_FOR_BOOKS, dir=local_name_of_book_directory, filename=filename, file_extension=file_extension)
    create_path_if_doesnt_exist(cut_off_end_of_directory_string(full_path_of_file))
    j = open(full_path_of_file, "w")
    j.write(content.encode('utf-8'))
    j.close()


def create_path_if_doesnt_exist(directory):
    if not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError:
            print '0000000000000000000000000000000000000000000000000000000'
            print 'Failed to create directory: ' + directory
            print '0000000000000000000000000000000000000000000000000000000'
            pass


def read_json_from_disk(content):
    # the open keyword opens a file in read-only mode by default
    f = open(content)

    # read all the lines in the file and return them in a list
    lines = f.readlines()

    result = ''
    for line in lines:
        result += line

    f.close()

    return result


def cut_off_end_of_directory_string(path):
    result = ""
    path_list = path.split("/")
    for i in range(0, len(path_list)):
        if i == len(path_list) - 1:
            return result
        if i == 0:
            if path_list[i] == "":
                pass
            else:
                result += path_list[i] + "/"
        else:
            result += path_list[i] + "/"


main()
