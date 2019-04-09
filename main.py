import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

url1 = 'https://better.legendonlineservices.co.uk/Tower_Ham_-_Mile_End/account/login' #a redirect to a login page occurs
url2 = 'https://better.legendonlineservices.co.uk/Tower_Ham_-_Mile_End/account/home' #a redirect to a login page occurs
url3 = 'https://better.legendonlineservices.co.uk/tower_ham_-_mile_end/BookingsCentre/Index'
url4 = 'https://better.legendonlineservices.co.uk/tower_ham_-_mile_end/BookingsCentre/Timetable?KeepThis=true&'
url6 = 'https://better.legendonlineservices.co.uk/tower_ham_-_mile_end/Basket/Index'
url7 = 'https://better.legendonlineservices.co.uk/tower_ham_-_mile_end/Basket/Pay'

print('Pinging login page to fetch cookies')
driver.get(url1)
time.sleep(2)

# storing the cookies generated by the browser
request_cookies_browser = driver.get_cookies()

# making a persistent connection using the requests library
params = {
    'login.Email': 'your_username',
    'login.Password': 'your_password'
}

s = requests.Session()

# passing the cookies generated from the browser to the session
c = [s.cookies.set(c['name'], c['value']) for c in request_cookies_browser]

print('Logging in with cookies')
resp = s.post(url1, params) #I get a 200 status_code
time.sleep(2)

# passing the cookie of the response to the browser
dict_resp_cookies = resp.cookies.get_dict()
response_cookies_browser = [{'name':name, 'value':value} for name, value in dict_resp_cookies.items()]
c = [driver.add_cookie(c) for c in response_cookies_browser]

# # the browser now contains the cookies generated from the authentication
# driver.get(url2)

print('Moving to booking page')
# move to the booking page
driver.get(url3)
time.sleep(2)

print('Tick badminton 40 mins checkbox')
# tick the badminton checkbox (40 mins or 60 mins)
driver.find_element_by_xpath(
    ".//*[contains(text(), 'Badminton Court - 60')]"
).click()

# # view timetable
# driver.execute_script('viewTimetable()')

# open a request session to fetch slot id and court id
s = requests.Session()

# passing the cookies generated from the browser to the session
c = [s.cookies.set(c['name'], c['value']) for c in driver.get_cookies()]

print('Getting timetable information')
# get request
rr = s.get(url4)
time.sleep(2)

# extract slots and choose a particular one
soup = BeautifulSoup(rr.text, features="html5lib")
soup.findAll("a", {"class": "sporthallSlotAddLink"})
chosen_slot = soup.findAll("a", {"class": "sporthallSlotAddLink"})[-7]
slot = ''.join([i for i in chosen_slot.get('id') if not i.isalpha()])

url5 = f'https://better.legendonlineservices.co.uk/tower_ham_-_mile_end//BookingsCentre/SelectResourceLocation?slotId={slot}&KeepThis=true&'

print('Choose a time slot and get courts availability')
# extract courts and choose a particular one
rr = s.get(url5)
time.sleep((2))
soup = BeautifulSoup(rr.text)
values = [f.get('value') for f in soup.findAll("option") if f.get('value') != '-1']
v = values[0]

print('Confirming court selection')
# confirm court selection
driver.execute_script(f'confirmCourtSelect({slot}, {v})')
time.sleep(2)

print('Transition the my baskets')
# move to baskets page
driver.get(url6)
time.sleep(2)

print('Applying voucher')
# use voucher
driver.find_element_by_xpath(
    ".//*[contains(text(), 'Use Voucher')]"
).click()
time.sleep(2)

print('Finishing transaction')
# finally finish transaction; this should send you an email from better
driver.get(url7)
time.sleep(2)

print('Done.')
