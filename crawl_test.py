from crawler import Crawler
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import argparse
from decouple import config
parser = argparse.ArgumentParser(description="-d For scroll times and -k for waiting time after each scroll")

parser.add_argument("-d", "--depth", type=int, default=2, metavar="", help="Numbers of scroll")

parser.add_argument("-k", "--keep", type=int, default=5, metavar="", help="Seconds you want to delay after scroll")

args = parser.parse_args()
fb_crawler = Crawler(args.depth, args.keep)
