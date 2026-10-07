import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import csv 
import os
import time


#get products.json with pathlib

project_dir = Path(__file__).parent.parent
products_file = project_dir / "products.json"

# get data out of products.json 

with open(products_file) as file:
    data = json.load(file)

i = 0

# identify the script and never wait forever for a response
HEADERS = {"User-Agent": "price-alert-hobby-project"}
REQUEST_TIMEOUT = 10 # seconds


def print_products(data, i):    
    print("Product Name:" ,data["products"][i]["name"]) 
    print("Target Price: ",data["products"][i]["target_price"])# get data from products.json and print it to the console
        

def discord_message(data, i, text_price, timestamp):
    project_dir = Path(__file__).parent.parent
    webhook_file = project_dir / "webhookurl.txt"


    with open(webhook_file, "r") as f:
        webhook_url = f.read().strip()

    product = data["products"][i] # get the data from the list data 
    target_price_value = product["target_price"] # get target price ourt the variable "product"

    message = (
        f"Product: {product['name']}\n" # get with product['name'] the name out of the product data
        f"Target Price: {target_price_value}\n"
        f"Current Price: {text_price}\n"
        f"Date: {timestamp}"
    )

    try:
        response = requests.post(
            webhook_url,
            json ={
                "content" : message
            },
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as error:
        print("Could not send Discord message:", error)


def complete_scrape_alternate(data, i):
    url = data["products"][i]["url"] # get the url of the first product in the list 

    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT) # get the response from the urls
    except requests.RequestException as error:
        print("Request failed for product:", data["products"][i]["name"], "-", error)
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    price_element = soup.find("span", class_="price") # find the price element in the html code

    if price_element is None:
     print("Price element not found for product:", data["products"][i]["name"])
     return None # no price found, the caller skips this product

    text_price = price_element.text
    text_price = text_price.replace(".", "").replace("€", "").replace(",", ".").strip() # remove the euro sign and replace the comma with a do

    try:
        text_price = float(text_price) # convert the price to a float
    except ValueError:
        print("Could not read price for product:", data["products"][i]["name"])
        return None

    return text_price


def compare_scrape_alternate(data, i, text_price):
    time_sleep_boolean = False # becomes True if at least one product is at or below its target price

    while i < len(data["products"]):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S") # get the current timestamp
        text_price = complete_scrape_alternate(data, i) # get the price of the product

        if text_price is None:
            i += 1 # skip this product, otherwise the loop would repeat forever
            time.sleep(5) # short pause between requests
            continue

        if text_price <= data["products"][i]["target_price"]:
            print("Price is lower than target Price! Sending message...")
            discord_message(data, i, text_price, timestamp) # send discord message
            time_sleep_boolean = True
        else: 
            print("price is higher than target Price! no message sent.")
        i += 1
        time.sleep(5) # short pause between requests

    return time_sleep_boolean  # boolean to change time.sleep()