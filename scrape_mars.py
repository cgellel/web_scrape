# coding: utf-8

# Import Dependencies
# use BeautifulSoup for parsing and splinter for site navigation
from bs4 import BeautifulSoup as bs
from splinter import Browser
import os
import pandas as pd
import time
import pymongo


def init_browser():
    #NOTE: For executable path replace with your PC path to chromedriver
    executable_path = {"executable_path": "/Users/chr/Desktop/Working Directory/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

def scrape():
    browser = init_browser()

    # Create a dictionary for all of the scraped data
    mars_data = {}

# ### NASA Mars News

    # Visit the NASA news URL
    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)

    # Scrape page into soup
    html = browser.html
    soup = bs(html, 'html.parser')

    #collect the latest News Title and Paragraph Text
    article = soup.find("div", class_="list_text")
    news_p = article.find("div", class_="article_teaser_body").text
    news_title = article.find("div", class_="content_title").text
    news_date = article.find("div", class_="list_date").text

    # Save most recent article, title, date and summary to dictionary
    mars_data["news_date"] = news_date
    mars_data["news_title"] = news_title
    mars_data["summary"] = news_p

# ### JPL Mars Space Images - Featured Image

    # With chromedriver open Visit JPL Featured Space Image url
    images_url = "https://jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(images_url)

    # Use splinter to navigate site and find the image url for the current Featured Mars Image
    # assign the url string to a variable called `featured_image_url`.
    # Scrape browser into soup and use soup to find the image of mars
    # Save image url to a variable called `img_url`

    html = browser.html
    soup = bs(html, 'html.parser')
    image = soup.find('li',class_='slide').a['data-fancybox-href']
    img_url = "https://jpl.nasa.gov"+image
    featured_image_url = img_url

    # Add featured image url to dictionary
    mars_data["featured_image_url"] = featured_image_url

# ### Mars Weather

    #* Visit the Mars Weather twitter account
    #*Scrape the latest Mars weather tweet from the Twitter page
    twitter_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(twitter_url)

    # Wait for page to load
    time.sleep(2)

    # Pass the HTML object from the splinter session
    html = browser.html  
    soup = bs(html, 'html.parser')

    # Find all elements that contain tweets <div container
    latest_tweets = soup.find_all('div', class_='js-tweet-text-container')

    for tweet_html in latest_tweets:
        tweet = tweet_html.text.strip()
        if tweet.strip().startswith('Sol'): 
            mars_weather = tweet
            break

    # Add the weather to the dictionary
    mars_data["mars_weather"] = mars_weather

# ### Mars Facts

    facts_url = "https://space-facts.com/mars/"
    browser.visit(facts_url)

    table = pd.read_html(facts_url)
    mars_info = pd.DataFrame(table[0])
    mars_info.columns = ['Mars','Data']
    mars_table = mars_info.set_index("Mars")
    marsinformation = mars_table.to_html(classes='marsinformation')
    marsinformation =marsinformation.replace('\n', ' ')

    # Add the Mars facts table to the dictionary
    mars_data["mars_table"] = marsinformation

# ### Mars Hemispheres

    # Visit the USGS Astogeology site and scrape pictures of the hemispheres
    astr_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    base="https://astrogeology.usgs.gov/"
    browser.visit(astr_url)
    html = browser.html
    soup = bs(html, 'html.parser')
    mars_hemis_urls=[]

    # Loop through the four tags and load the data to the dictionary
    for i in range(4):
        time.sleep(5)
        images = browser.find_by_tag('h3')
        images[i].click()
        html = browser.html
        # Parse HTML with Beautiful Soup for every individual hemisphere information website 
        soup = bs(html, 'html.parser')
        partial = soup.find("img", class_="wide-image")["src"]
        img_title = soup.find("h2",class_="title").text
        img_url = base + partial
        dictionary={"title":img_title,"img_url":img_url}
        mars_hemis_urls.append(dictionary)
        browser.back()
        
    mars_data["mars_hemis_urls"] = mars_hemis_urls
    # Return the dictionary
    return mars_data