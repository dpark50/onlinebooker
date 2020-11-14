from webbot import Browser
from datetime import datetime
import stdiomask
import sched
import time
import pytz
import sys
import constants

def get_selected_option(count, booking_id):
    # 14 includes open workout as the first option
    if count == 14:
        return constants.LAST_BOOKING_OPTIONS.replace('li', 'li[' + str(booking_id + 1) + ']/div[2]/div/div[2]/div[1]/button')
    return constants.LAST_BOOKING_OPTIONS.replace('li', 'li[' + str(booking_id) + ']/div[2]/div/div[2]/div[1]/button')

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
    driver.click(xpath = get_selected_option(optionsCount, booking_id))

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
    # TODO: re-prompt
    pw = stdiomask.getpass(prompt='Enter password:\n')
    print('[1] 6:00AM - 7:00AM\n' \
          '[2] 7:30AM - 8:30AM\n' \
          '[3] 9:00AM - 10:00AM\n' \
          '[4] 10:30AM - 11:30AM\n' \
          '[5] 12:00PM - 1:00PM\n' \
          '[6] 1:30PM - 2:30PM\n' \
          '[7] 3:00PM - 4:00PM\n' \
          '[8] 4:30PM - 5:30PM\n' \
          '[9] 6:00PM - 7:00PM\n' \
          '[10] 7:30PM - 8:30PM\n' \
          '[11] 9:00PM - 10:00PM\n' \
          '[12] 10:30PM - 11:30PM\n')

    booking_time = 1

    while True:
        try:
            booking_id = int(input('Please select a time to book (displayed times are for weekdays):\n'))
            if booking_id >= 1 and booking_id <= 12:
                booking_time = get_booking_time(booking_id)
                break
        except ValueError:
            pass

        print('\nInvalid input\n')

    dt = datetime.now()
    pst_tz = pytz.timezone('US/Pacific')
    local_dt = pst_tz.normalize(dt.astimezone(pst_tz))
    print('Current time: ', local_dt)
    # For testing
    # target = local_dt.replace(day = local_dt.day, hour = 0, minute = local_dt.minute + 1)
    target = local_dt.replace(day = local_dt.day + 1, hour = 0, minute = 2)
    print('Scheduled for ', pst_tz.normalize(target.astimezone(pst_tz)))
    print('...')

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enterabs(target.timestamp(), 0, action, argument = (id, pw, booking_time))
    scheduler.run()

if __name__ == "__main__":
    main()
