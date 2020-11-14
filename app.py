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
    # For testing
    # driver.click(tag = 'button', css_selector = '[data-display="6:00AM - 7:00AM"]')
    driver.click(tag = 'button', css_selector = booking_time)

    if driver.errors:
        print('Error')
        sys.exit(driver.errors)

    print('>>> Date and time selected')
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
