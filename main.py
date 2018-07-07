from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import random
import re
import json
import os
import sys
import urllib2

SCRIBD_BASE_URL = "https://www.scribd.com/scepub/{resource_id}"
SCRIBD_CHAPTERS_URL = "/{chapter_path}"
SCRIBD_TOC_URL = "/toc.json?token={token}"
SCRIBD_CONTENT_URL = "/contents.json?token={token}"
SCRIBD_IMAGE_URL = "/{filename}?token={token}"
SCRIBD_STYLES_URL = "/styles.json?token={token}"
SCRIBD_METADATA_URL = "/metadata.json?token={token}"
SCRIBD_PAGE_REFS_URL = "/page_refs.json?token={token}"
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
LIST_OF_BOOK_URLS = [
    "https://www.scribd.com/book/282496355/",
    "https://www.scribd.com/book/253052099/",
    "https://www.scribd.com/book/239467568/",
    "https://www.scribd.com/book/358031167/",
    "https://www.scribd.com/book/358031166/",
    "https://www.scribd.com/book/282538161/",
    "https://www.scribd.com/book/239465986/",
    "https://www.scribd.com/book/239467888/",
    "https://www.scribd.com/book/282496455/",
    "https://www.scribd.com/book/287523516/",
    "https://www.scribd.com/book/298574302/",
    "https://www.scribd.com/book/287529182/",
    "https://www.scribd.com/book/282495159/",
    "https://www.scribd.com/book/239465548/",
    "https://www.scribd.com/book/255443250/",
    "https://www.scribd.com/book/253049325/",
    "https://www.scribd.com/book/287523437/",
    "https://www.scribd.com/book/358572397/",
    "https://www.scribd.com/book/287528768/",
    "https://www.scribd.com/book/282494944/",
    "https://www.scribd.com/book/353532808/"
]


def main():
    global local_name_of_book_directory
    global resource_id
    global token
    global use_local_json
    global images_downloaded
    global driver_url
    global driver_session_id
    if len(sys.argv) == 2:
        local_name_of_book_directory = sys.argv[1]
        use_local_json = 'y'
        images_downloaded = 'y'
        print "Creating book from already downloaded json data..."
        create_book()
    elif len(sys.argv) == 4:
        local_name_of_book_directory = sys.argv[1]
        resource_id = sys.argv[2]
        token = sys.argv[3]
        use_local_json = 'y'
        images_downloaded = 'n'
        print "Creating book from already downloaded json data BUT downloading image data..."
        create_book()
    else:
        driver_url = ""
        driver_session_id = ""
        prompt()


#######################################################################################################################


def prompt():
    print "###########################################################################################################"
    print "Welcome to the scribd BOOK downloading utility..."
    print "###########################################################################################################"
    print
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
    print

    global resource_id
    global token
    global use_local_json
    global images_downloaded
    global using_selenium

    using_selenium = False  # setting this pre-emptively as a default value

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
        token = raw_input("Enter your token (leave blank if you'd like to automate it with Selenium (not working ATM)): ")
        if token == "":
            print
            print "Getting token..."
            using_selenium = True
            get_token_with_selenium()

    print
    print "Creating book..."
    create_book()


def create_book():
    global resource_id
    global token
    global use_local_json
    global images_downloaded

    html_all_content = HTML_TOP_ALL_PAGES
    html_toc_content = HTML_TOP_ALL_PAGES + '\t\t\t<h1>Table of Contents</h1>\n'

    if use_local_json == "y":
        toc_json_string = read_json_from_disk("{PATH_FOR_BOOKS}/{dir}/toc.json".format(PATH_FOR_BOOKS=PATH_FOR_BOOKS, dir=local_name_of_book_directory))
    else:
        toc_json_string = download_toc_from_scribd()
        style_json_string = download_styles_from_scribd()
        metadata_json_string = download_metadata_from_scribd()
        page_refs_json_string = download_page_refs_from_scribd()
        save_file("toc", toc_json_string, "json")
        save_file("styles", style_json_string, "json")
        save_file("metadata", metadata_json_string, "json")
        save_file("page_refs", page_refs_json_string, "json")

    toc_list = create_toc_from_json(toc_json_string)

    for toc_item in toc_list:
        if use_local_json == "y":
            chapter_raw = read_json_from_disk("{PATH_FOR_BOOKS}/{dir}/{toc_item}.json".format(PATH_FOR_BOOKS=PATH_FOR_BOOKS, dir=local_name_of_book_directory, toc_item=toc_item))
        else:
            chapter_raw = download_chapter_from_scribd(toc_item)
            save_file(toc_item, chapter_raw, "json")

        html_toc_content += create_toc_from_item("{toc_item}.html".format(toc_item=toc_item))
        html_chapter_content = create_chapter_from_json(chapter_raw, toc_item)
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
    return download_and_handle_expired_token(download_url, False)


def download_chapter_from_scribd(chapter_path):
    print "Downloading " + chapter_path + "..."
    global resource_id
    global token
    download_url = SCRIBD_BASE_URL.format(resource_id=resource_id)
    download_url += SCRIBD_CHAPTERS_URL.format(chapter_path=chapter_path)
    download_url += SCRIBD_CONTENT_URL.format(token=token)
    return download_and_handle_expired_token(download_url, False)


def download_image_from_scribd(chapter_path, filename):
    print "Downloading " + chapter_path + "/" + filename + "..."
    global resource_id
    global token
    download_url = SCRIBD_BASE_URL.format(resource_id=resource_id)
    download_url += SCRIBD_CHAPTERS_URL.format(chapter_path=chapter_path)
    download_url += SCRIBD_IMAGE_URL.format(filename=filename, token=token)
    return download_and_handle_expired_token(download_url, True)


def download_styles_from_scribd():
    print "Downloading styles..."
    global resource_id
    global token
    download_url = SCRIBD_BASE_URL.format(resource_id=resource_id)
    download_url += SCRIBD_STYLES_URL.format(token=token)
    return download_and_handle_expired_token(download_url, False)


def download_metadata_from_scribd():
    print "Downloading metadata..."
    global resource_id
    global token
    download_url = SCRIBD_BASE_URL.format(resource_id=resource_id)
    download_url += SCRIBD_METADATA_URL.format(token=token)
    return download_and_handle_expired_token(download_url, False)


def download_page_refs_from_scribd():
    print "Downloading page references..."
    global resource_id
    global token
    download_url = SCRIBD_BASE_URL.format(resource_id=resource_id)
    download_url += SCRIBD_PAGE_REFS_URL.format(token=token)
    return download_and_handle_expired_token(download_url, False)


def download_and_handle_expired_token(download_url, is_image):
    global using_selenium
    global token

    try:
        if is_image:
            content = urllib2.urlopen(download_url)
        else:
            content = urllib2.urlopen(download_url).read()
        return content

    except urllib2.HTTPError:
        print_error_message('Item returned an HTTPError: ' + download_url)
        if using_selenium:
            get_token_with_selenium()
        else:
            token = raw_input("Token has expired. Re-enter a valid token: ")

        try:
            if is_image:
                content = urllib2.urlopen(download_url)
            else:
                content = urllib2.urlopen(download_url).read()
            return content
        except urllib2.HTTPError:
            print_error_message('Failed trying to recover from an expired token')


#######################################################################################################################


def create_toc_from_json(json_string):
    parsed_json = json.loads(json_string)
    # parsed json is a <list>

    toc_list = []

    for item in parsed_json:
        path = item['filepath']
        toc_list.append(path)

    return toc_list


def create_toc_from_item(chapter_path):
    return "\t\t\t<div><a href=\"" + chapter_path + "\">" + chapter_path + "</a></div>\n"


def create_chapter_from_json(json_string, chapter_path):
    global images_downloaded

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
            print_error_message('Block - Failed to get type of block: ' + block)
            pass

        if block_type == 'image':
            image_filename = return_image_from_node(block, chapter_path)
            html_chapter_content += "\t\t\t<img src=\"../{img_path}\"/>\n".format(img_path=image_filename)

        elif block_type == 'spacer':
            height = block['size']
            html_chapter_content += "\t\t\t<span style=\"display:block; height: {size};\">&nbsp;</span>\n".format(size=height)

        elif block_type == 'page_break':
            html_chapter_content += "\t\t\t<hr>\n"

        elif block_type == 'row':
            cells = block['cells']
            for cell in cells:
                style = cell['style']
                nodes = cell['nodes']
                html_chapter_content += "\t\t\t<div style=\"{style}\">\n".format(style=style)
                for node in nodes:
                    node_type = ''
                    try:
                        node_type = node['type']
                    except KeyError:
                        print_error_message('Node - Failed to get type of node: ' + node)
                        pass

                    if node_type == 'image':
                        image_filename = return_image_from_node(node, chapter_path)
                        html_chapter_content += "\t\t\t\t<img src=\"../{img_path}\"/>\n".format(img_path=image_filename)

                    elif node_type == 'text':
                        paragraph = return_text_from_node(node)
                        html_chapter_content += "\t\t\t\t<div>" + TAB_CHAR + paragraph + "</div>\n"

                html_chapter_content += "\t\t\t</div>\n"

        elif block_type == 'border':
            # TODO: what should we do with this?
            html_chapter_content += "\t\t\t<h3>Found 'border' but not sure what to do with this yet</h3>\n"

        elif block_type == 'text':
            paragraph = return_text_from_node(block)
            html_chapter_content += "\t\t\t<div>" + TAB_CHAR + paragraph + "</div>\n"

        elif block_type == 'raw':
            html_chapter_content += block['data']

        else:
            print_error_message('An unexpected type occurred! Type = ' + block_type)
            html_chapter_content += "\t\t\t<h1>UNEXPECTED TYPE (" + block_type + ")</h1>\n"

    return html_chapter_content


#######################################################################################################################


def return_image_from_node(block, chapter_path):
    image_filename = block['src']
    if images_downloaded == "n":
        img_raw = download_image_from_scribd(chapter_path, image_filename)
        if img_raw is not None:
            save_image(image_filename, img_raw)
        else:
            print "Skipped: " + image_filename
    return image_filename


def return_text_from_node(block):
    paragraph = ''

    try:
        words = block['words']
    except KeyError:
        print "!Found " + str(block)
        return

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
            print_error_message('Unexpected type found in block_type = \'text\'' + json.dumps(word))
    return paragraph


#######################################################################################################################


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
            print_error_message('Failed to create directory: ' + directory)
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


def print_error_message(msg):
    print '00000000000000000000000000000000000000000000000000000000'
    print msg
    print '00000000000000000000000000000000000000000000000000000000'
    print


#######################################################################################################################


# not ready yet...
def get_token_with_selenium():
    global token
    global driver_url
    global driver_session_id

    browser = webdriver.Chrome()
    if driver_url == "" or driver_session_id == "":
        driver_url = browser.command_executor._url
        driver_session_id = browser.session_id
    else:
        browser.webdriver.Remote(command_executor=driver_url, desired_capabilities={})
        browser.session_id = driver_session_id

    browser.get("https://www.scribd.com/login")

    if browser.find_element_by_id("login_or_email") is not None:
        username_element = browser.find_element_by_id("login_or_email")
        username_element.clear()
        username_element.send_keys("ENTER USERNAME")
        password_element = browser.find_element_by_id("login_password")
        password_element.clear()
        password_element.send_keys("ENTER PASSWORD")
        password_element.send_keys(Keys.RETURN)
        WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "sign_out_btn")))

    browser.get(LIST_OF_BOOK_URLS[random.randint(1, len(LIST_OF_BOOK_URLS) + 1)])

    if browser.find_element_by_class_name("start_reading_btn") is not None:
        reading_button = browser.find_element_by_class_name("start_reading_btn")
        reading_button.click()
        WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "icon-ic_displaysettings")))

    source = browser.page_source.encode("utf-8")
    # token_raw = re.search("\"access_token\":\".*?\"", source)
    # ^ doesn't return a token that can be used to grab content
    token_raw = re.search("\?token=\".*?\"", source)

    page_number_counter_old = browser.find_element_by_class_name("page_counter")

    if token_raw is None:
        left_click_button = browser.find_element_by_class_name("icon-ic_back_arrow")
        left_click_button.click()
        WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, "page_counter")))

    print token_raw
    print token_raw.group()
    split_results = token_raw.group().split("\"")
    print split_results
    # ^ returns ['', 'access_token', ':', '1530935337_3I2UU77KBTEP2EYTQHC6KWCWIWLFVWPBH5GBQ4FYEMZK3ELE5BVUZYATSF2A2===_b7984fc7035c420005762681965bbd394b9ea9c8', '']
    token = split_results[3]
    print token


#######################################################################################################################


main()
