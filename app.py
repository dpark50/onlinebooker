from webbot import Browser
from datetime import datetime
import stdiomask
import sched
import time
import pytz
import sys

def get_booking_time(id):
    time = None

    if id == 1:
        time = '6:00AM - 7:00AM'
    elif id == 2:
        time = '7:30AM - 8:30AM'
    elif id == 3:
        time = '9:00AM - 10:00AM'
    elif id == 4:
        time = '10:30AM - 11:30AM'
    elif id == 5:
        time = '12:00PM - 1:00PM'
    elif id == 6:
        time = '1:30PM - 2:30PM'
    elif id == 7:
        time = '3:00PM - 4:00PM'
    elif id == 8:
        time = '4:30PM - 5:30PM'
    elif id == 9:
        time = '6:00PM - 7:00PM'
    elif id == 10:
        time = '7:30PM - 8:30PM'
    elif id == 11:
        time = '9:00PM - 10:00PM'
    else:
        time = '10:30PM - 11:30PM'

    return '[data-display="' + time + '"]'

    driver = Browser()
    # Fill url
    driver.go_to('')
    print('>>> Logging in')
    driver.type(id, into = 'Email/Member #')
    driver.type(pw, into = 'Password')
    driver.click(text = 'Login', id = 'btn-login')
    time.sleep(4)
    # Fill location
    driver.click(text = '')

    if driver.errors:
        print('Error')
        sys.exit(driver.errors)

    # Select the newest date
    driver.click(tag = 'div', classname = 'date-tile', number = 8)
    driver.click(id = 'coedStudio')
    time.sleep(3)
    driver.scrolly(400)
    # TODO: Selectable time
    driver.click(tag = 'button', css_selector = '[data-display="6:00AM - 7:00AM"]')
    print('>>> Date and time selected')

    if driver.errors:
        print('Error')
        sys.exit(driver.errors)

    time.sleep(4)
    # Scroll to bottom of dialog
    driver.execute_script('var modal = document.getElementById("codeOfConductModal"); ' \
    'modal.scrollTop = modal.scrollHeight;')
    driver.click(tag = 'button', id = 'codeOfConductAgree', text = 'I Agree')
    print('>>> Agree to code of conduct')
    driver.click('Confirm', tag = 'button', id = 'confirmBookingButton')
    print('>>> Confirm booking')
    time.sleep(3)
    # Close registered booking dialog
    driver.click(xpath = '/html/body/form/div[4]/div[4]/div/div/button')
    time.sleep(2)

    # Check if hamburger button exists. This contains the logout button.
    if driver.exists(id = 'gl-mobile-nav'):
        driver.click(tag = 'span', text = 'Menu', number = 1)
        time.sleep(2)
        driver.scrolly(700)

    driver.click(id = 'logout')
    print('>>> Logging out')
    print('>>> Finished')

def main():
    id = input('Enter id:\n')
    # TODO: re-prompt
    pw = stdiomask.getpass(prompt='Enter password:\n')
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
    scheduler.enterabs(target.timestamp(), 0, action, argument = (id, pw))
    scheduler.run()

if __name__ == "__main__":
    main()
