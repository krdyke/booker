#!/usr/bin/env python

import sys
import urllib2
import json
import re
import csv
import argparse
import time
import os

#config.py should contain API_KEY
import config

BASE_GBOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes?q="

#all this does now is extract only numbers (no letters, dashes, spaces, etc)
ISBN_PATTERN = "[0-9]*"


def request_json(request_url):
    try:
        response = urllib2.urlopen(request_url)
    except urllib2.HTTPError as e:
        print "Error: {mess}".format(mess=e)
        return "Error: {mess}".format(mess=e)
    return json.load(response)
    
#just for sake of having a more abstract option
def get_book(query):
    url = BASE_GBOOKS_API_URL + query
    request_json(url)

#in case there are any dashes, spaces, or other non-numeric funny business...
def clean_isbn(raw_isbn):
    return "".join(re.findall(ISBN_PATTERN, raw_isbn))

def get_book_by_isbn(isbn):
    url = BASE_GBOOKS_API_URL + isbn + "&key={key}".format(key=config.API_KEY)
    book_json = request_json(url)
    return book_json

def get_thumbnail_url_for_isbn(raw_isbn):
    isbn = clean_isbn(raw_isbn)
    if _thumb_exists(isbn):
        print "thumbnail already exists for isbn: {isbn}, so skipping.\n".format(isbn=isbn)
        return "{isbn}.png already exists".format(isbn=isbn)
    isbn_formatted = "isbn:" + isbn
    response_json = get_book_by_isbn(isbn_formatted)
    if response_json and response_json["totalItems"] > 0:
        try:
            if response_json["items"][0]["volumeInfo"].has_key("imageLinks"):
                thumbnail_url = response_json["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
            else:
                print "No thumbnail url available for ISBN: {isbn}\n".format(isbn=isbn)
                return "No thumbnail url available for ISBN: {isbn}".format(isbn=isbn)
        except KeyError as e:
            print "Error: {mess}".format(mess=e)
            return None
        return thumbnail_url
    else:
        print "ISBN: {isbn} not in Google Books.".format(isbn=isbn)
        return "Not in Google Books.\n".format(isbn=isbn)

def _thumb_exists(isbn):
    path = os.path.join(PATH_TO_THUMBS, isbn + ".png")
    return os.path.isfile(path)


def get_thumbnail(url, isbn):
    """
    Downloads the thumbnail using the provided url, which
    should have been derived from a Google Books API call.
    """
    thumb_req = urllib2.urlopen(url)
    thumb_file = open(os.path.join(PATH_TO_THUMBS, isbn + ".png"), "wb")
    thumb_file.write(thumb_req.read())
    thumb_file.close()

def get_thumbnails_for_list(list_of_isbns, output_csv_writer=None):
    """
    For each isbn in a provided list, fetches the thumbnail url if
    there is one, and then uses it to download the thumbnail.
    """
    for isbn in list_of_isbns:
        print "Now on ISBN: " + isbn
        url = get_thumbnail_url_for_isbn(isbn)
        if url and url.startswith("http"):
            time.sleep(1)
            get_thumbnail(url, isbn)
        if output_csv_writer:
            row = {"isbn":isbn, "thumbnail_url":url}
            output_csv_writer.writerow(row)


def read_csv(csv_file, isbn_column):
    """
    Reads an inputted csv containing a field with ISBNs. Also writes
    out a new CSV with the ISBN and thumbnail URLs for future reference.
    Relies on isbn_column argument to identify which column to read for ISBNs.
    """

    reader = csv.DictReader(csv_file)
    out_csv = open(os.path.join(PATH_TO_THUMBS, "isbns_thumbnails.csv"),"w")
    writer = csv.DictWriter(out_csv, ["isbn","thumbnail_url"])
    isbns = []
    for row in reader:
        isbns.append(row[isbn_column])
    get_thumbnails_for_list(isbns, output_csv_writer=writer)
    out_csv.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="Path to the csv file containing ISBNs")
    parser.add_argument("-i", "--isbn-column", default="isbn", help="Name of column containing ISBNs. Defaults to 'isbn'")
    parser.add_argument("-o", "--output-path", default="thumbs", help="Where to write the thumbnails. Defaults to 'thumbs'")
    args = parser.parse_args()
    global PATH_TO_THUMBS 
    PATH_TO_THUMBS = args.output_path
    if not os.path.exists(PATH_TO_THUMBS):
        os.mkdir(PATH_TO_THUMBS)
    isbn_column = args.isbn_column
    csv_file = open(args.input_csv, "rU")
    read_csv(csv_file, isbn_column)

if __name__ == "__main__":
    sys.exit(main())
