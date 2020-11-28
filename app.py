from webbot import Browser
from datetime import datetime
import stdiomask
import sched
import time
import pytz
import sys
import constants

def action(id, pw, booking_id):
    driver = Browser()
    driver.go_to(constants.URL)
    time.sleep(3)
    driver.click(tag = 'a', text = 'Log in')
    print('>>> Logging in')
    time.sleep(3)
    driver.type(id, into = 'Enter Member ID, barcode or email address')
    driver.type(pw, into = 'Enter password')
    driver.click(xpath = constants.LOGIN_BUTTON_PATH)
    time.sleep(10)

    if driver.exists(tag = 'span', text = 'Email address or Barcode or Member ID not recognized'):
        print('ERROR: Unable to login (Email address or Barcode or Member ID not recognized)')
        return

    location = driver.find_elements(id = 'js-search-location-default-club')[0].get_attribute('innerText')
    time.sleep(3)

    # Switch location
    if location != constants.LOCATION:
        print('>>> Switching locations')
        driver.click(tag = 'a', id = 'js-search-filter-change')
        driver.click(tag = 'section', id = 'section_clubs')
        # Switch to correct location
        driver.execute_script('document.querySelector(\'[data-clubnumber="243"]\').click()')
        driver.click(id = 'js-filter-location-button-apply')
        time.sleep(3)

    print('>>> Booking...')
    driver.click(tag = 'label', classname = 'c-filter__label', text = 'Co-ed')
    time.sleep(3)
    driver.click(classname = 'js-unordered-list-button-mobile')
    # Select the newest day
    driver.click(tag = 'li', css_selector = '[data-day="day-number-7"]')
    optionsCount = len(driver.find_elements(xpath = constants.LAST_BOOKING_OPTIONS))
    print('>>> # of options: ' + optionsCount)
    driver.click(xpath = constants.LAST_BOOKING_OPTIONS.replace('li', 'li[' + str(booking_id) + ']'))

    if driver.errors:
        print('ERROR: Fully booked')
        return

    time.sleep(2)
    # Scroll to bottom of modal
    driver.execute_script('var element = document.getElementById("js-workout-booking-agreement-input"); ' \
            'element.scrollIntoView()')
    # Agreement
    driver.execute_script('document.getElementById("js-workout-booking-agreement-input").click();')
    time.sleep(2)
    driver.click(text = 'Confirm')
    print('>>> Booking confirmed')
    time.sleep(2)
    # Close confirmation dialog
    driver.click(xpath = constants.CLOSE_DIALOG_PATH)
    print('>>> Logging out')
    driver.click(tag = 'a', text = 'logout')
    print('>>> Finished')

def main():
    id = input('Enter id:\n')

    while True:
        pw1 = stdiomask.getpass(prompt='Enter password:\n')
        pw2 = stdiomask.getpass(prompt='Confirm password:\n')

        if pw1 == pw2:
            break

        print('\nPasswords do not match\n')

    print('[1] 6:00AM - 7:00AM\n' \
          '[2] 7:15AM - 8:15AM\n' \
          '[3] 8:30AM - 9:30AM\n' \
          '[4] 9:45AM - 10:45AM\n' \
          '[5] 11:00AM - 12:00PM\n' \
          '[6] 12:15PM - 1:15PM\n' \
          '[7] 1:30PM - 2:30PM\n' \
          '[8] 2:45PM - 3:45PM\n' \
          '[9] 4:00PM - 5:00PM\n' \
          '[10] 5:15PM - 6:15PM\n' \
          '[11] 6:30PM - 7:30PM\n' \
          '[12] 7:45PM - 8:45PM\n' \
          '[13] 9:00PM - 10:00PM\n' \
          '[14] 10:15PM - 11:15PM\n')
    booking_id = None

    while True:
        try:
            booking_id = int(input('Please select a time to book (displayed times are for weekdays):\n'))
            if booking_id >= 1 and booking_id <= 14:
                break
        except ValueError:
            pass

        print('\nInvalid input\n')

    dt = datetime.now()
    pst_tz = pytz.timezone('US/Pacific')
    local_dt = pst_tz.normalize(dt.astimezone(pst_tz))
    print('Current time: ', local_dt)
    # For testing
    # target = local_dt.replace(day = local_dt.day, hour = local_dt.hour, minute = local_dt.minute, second = local_dt.second + 2)
    target = local_dt.replace(day = local_dt.day + 1, hour = 0, minute = 2)
    print('Scheduled for ', pst_tz.normalize(target.astimezone(pst_tz)))
    print('...')

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enterabs(target.timestamp(), 0, action, argument = (id, pw1, booking_id))
    scheduler.run()

if __name__ == "__main__":
    main()
