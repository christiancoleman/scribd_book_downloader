import os
from subprocess import call

for book_dir in os.listdir('./books/'):
    print "##############################################################################################"
    print book_dir
    #call(["python", "../main.py " + book_dir])
    os.system("python main.py " + book_dir)
    print "##############################################################################################"
