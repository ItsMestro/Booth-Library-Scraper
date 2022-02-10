import os
import time

import browser_cookie3
import gspread
import requests
from bs4 import BeautifulSoup

# Path to chrome cookie with booth.pm login
COOKIE_FILE_PATH = (
    ""
)

# Last part of a spreadsheets URL
GOOGLE_SHEET_ID = ""

# Set up a Google Cloud Service Account and point this to the json file
# https://docs.gspread.org/en/latest/oauth2.html
GSPREAD_KEY = ""

"""

 _   _                   _ _       _     _   
| \ | |                 | (_)     | |   | |  
|  \| | __ _ _ __   ___ | |_  __ _| |__ | |_ 
| . ` |/ _` | '_ \ / _ \| | |/ _` | '_ \| __|
| |\  | (_| | | | | (_) | | | (_| | | | | |_ 
\_| \_/\__,_|_| |_|\___/|_|_|\__, |_| |_|\__|
                              __/ |          
                             |___/           
"""

# Classes because idk
class BoothProductFile:
    def __init__(self):
        self.FileName = ""
        self.FileDownload = ""


class BoothProduct:
    def __init__(self):
        self.LibraryPage = 0
        self.ItemName = ""
        self.ItemLink = ""
        self.ItemImage = ""
        self.StoreName = ""
        self.StoreLink = ""
        self.Downloads = []


def terminalclear():
    os.system("cls" if os.name == "nt" else "clear")


# General stuff
cookie = browser_cookie3.chrome(cookie_file=COOKIE_FILE_PATH, domain_name=".booth.pm")
URL = "https://accounts.booth.pm/library"

product_list = []
url_params = {"page": 1}
product_count = 0
download_count = 0

terminalclear()
print("Booth.pm Library Scraper started")

# Stupid while loop
while True:
    page = requests.get(URL, cookies=cookie, timeout=3, params=url_params)

    products = BeautifulSoup(page.content, "html.parser").find_all(
        "div", class_="sheet sheet--outline0"
    )

    if not products:
        break

    terminalclear()
    print(f"Fetching page: {url_params['page']}")

    for product in products:
        newproduct = BoothProduct()

        newproduct.LibraryPage = url_params["page"]

        newproduct.ItemName = product.find("div", class_="u-tpg-title3").text.strip()
        newproduct.ItemLink = product.find("div", class_="l-col-auto").find("a")["href"]
        newproduct.ItemImage = product.find("img", class_="l-library-item-thumbnail")["src"]
        newproduct.StoreName = product.find(
            "div", class_="u-text-ellipsis u-text-gray-500"
        ).text.strip()
        newproduct.StoreLink = product.find(
            "div", class_="l-library-shop-info u-tpg-caption1 u-text-gray-600"
        ).find("a")["href"]

        downloads = product.find("div", class_="u-mt-300 list list--collapse").find_all(
            "div", class_="list-item"
        )

        for download in downloads:
            newfile = BoothProductFile()
            newfile.FileName = (
                download.find("div", class_="u-flex-1 u-min-w-0 u-text-wrap")
                .find("span")
                .text.strip()
            )
            newfile.FileDownload = download.find("a", class_="nav-reverse")["href"]

            newproduct.Downloads.append(newfile)
            download_count += 1

        product_list.append(newproduct)
        product_count += 1

    url_params["page"] += 1
    time.sleep(3)

product_list.reverse()

if product_list:
    sheet = gspread.service_account(filename=GSPREAD_KEY).open_by_key(GOOGLE_SHEET_ID)

    data = []

    for i in product_list:

        filename_formatted = ""
        downloads_formatted = ""
        for d in i.Downloads:
            if filename_formatted:
                filename_formatted += "\n"
                downloads_formatted += "\n"

            filename_formatted += d.FileName
            downloads_formatted += d.FileDownload

        data.append(
            [
                filename_formatted,
                downloads_formatted,
                i.ItemName,
                i.ItemLink,
                i.LibraryPage,
                i.StoreName,
                i.StoreLink,
                i.ItemImage,
            ]
        )

    sheet.sheet1.update(f"D2:K{len(data) + 1}", data)

terminalclear()
print("Library scraping finished")
print()
print(f"Products: {product_count}")
print(f"Downloads: {download_count}")
print(f"Pages: {url_params['page'] - 1}")
