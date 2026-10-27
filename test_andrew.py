# By Andrew Bennett 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import random
import pytest

###  REPLACE THE BELOW WITH A VALID SESSION ID  ###
### Logged in webpage -> Inspect -> Application ###
###        -> Cookies -> OCSESSID Value         ###

from creds import VALID_SESSION_ID


def create_session(func):
    def inner():
        driver = webdriver.Chrome() # create driver object
        driver.implicitly_wait(10) # ensure all web pages fully load
        driver.get("https://opencart.abstracta.us") # navigate to home page
        driver.delete_cookie("OCSESSID") # delete then replace auth cookie
        driver.add_cookie(               # with a valid one
            {
                "name": "OCSESSID",
                "value": VALID_SESSION_ID,
                "domain": "opencart.abstracta.us",
                "path": "/",
            }
        )
        return func(driver)
    return inner

def _get_address_records(driver: webdriver.Chrome) -> list:
    ' Return a list of all address records '
    element = driver.find_element(By.ID, "content")
    content = element.find_element(By.CLASS_NAME, "table-responsive")
    table = content.find_element(By.TAG_NAME, "table")
    tb = table.find_element(By.TAG_NAME, "tbody")
    records = tb.find_elements(By.TAG_NAME, "tr")
    return records


def get_current_addr_record_num(driver: webdriver.Chrome) -> int:
    ' Return the number of address records '
    return len(_get_address_records(driver))


def get_address_records(driver: webdriver.Chrome) -> list[dict]:
    """ Return address records. List of each record. Each item is a dictionary.

    Dictionary items:
    full-name, address, city, postcode, state, country, edit-button, delete-button
    """
    records = _get_address_records(driver)
    results = []

    for record in records:
        record_dict = {}
        text_left = record.find_element(By.CLASS_NAME, "text-left")
        details = text_left.text.split("\n")
        record_dict['full-name'] = details[0]
        record_dict['address'] = details[1]
        record_dict['city'] = details[2].split(" ")[0]
        record_dict['postcode'] = details[2].split(" ")[1]
        record_dict['state'] = details[3]
        record_dict['country'] = details[4]

        text_right = record.find_element(By.CLASS_NAME, "text-right")
        record_dict['edit-button'] = text_right.find_element(By.CLASS_NAME, "btn-info")
        record_dict['delete-button'] = text_right.find_element(By.CLASS_NAME, "btn-danger")

        results.append(record_dict)

    return results


def create_prereq_address_recs(driver: webdriver.Chrome, req_num: int):
    ' Check if the required number of address records exists. If not, generate the required number. Must be on the address book page. '

    current_rec_num = get_current_addr_record_num(driver)

    if current_rec_num < req_num:
        print("Generating additional record(s) via `test_f16_s1` as required for current test...")
        while current_rec_num < req_num:
            test_f16_s1()
            driver.refresh()
            current_rec_num = get_current_addr_record_num(driver)


# pytest test_andrew.py::test_f16_s1
@create_session # create driver object, authenticate and set implicitly_wait to 10
def test_f16_s1(driver: webdriver.Chrome):
    ' Test Function 16 Scenario 1 - Create address in address book '

    driver.get("https://opencart.abstracta.us/index.php?route=account/address")

    title = driver.title

    assert title == "Address Book", f"Expected title to be 'Address Book' but got '{title}'"


    start_record_num = get_current_addr_record_num(driver)

    driver.find_element(By.CLASS_NAME, "btn-primary").click() # New address button
    assert title == "Address Book", f"Expected title to be 'Address Book' but got '{title}'"

    # Fill out form
    firstname = driver.find_element(By.ID, "input-firstname")
    firstname.send_keys("John")
    lastname = driver.find_element(By.ID, "input-lastname")
    lastname.send_keys("Smith")
    address1 = driver.find_element(By.ID, "input-address-1")
    address1.send_keys("123 Default st")
    city = driver.find_element(By.ID, "input-city")
    city.send_keys("Sydney")
    postcode = driver.find_element(By.ID, "input-postcode")
    postcode.send_keys("2345")
    country = Select(driver.find_element(By.ID, "input-country"))
    country.select_by_visible_text("Australia")
    zone = Select(driver.find_element(By.ID, "input-zone"))
    zone.select_by_visible_text("New South Wales")

    # Submit form
    driver.find_element(By.CLASS_NAME, "btn-primary").click()

    # Verify record has been created
    final_record_num = get_current_addr_record_num(driver)
    assert start_record_num + 1 == final_record_num, f"Incorrect number of records found. Expected {start_record_num+1}, Found {final_record_num})"

    driver.quit()

# pytest test_andrew.py::test_f16_s2
@create_session # create driver object, authenticate and set implicitly_wait to 10
def test_f16_s2(driver: webdriver.Chrome):
    ' Test Function 16 Scenario 2 - Delete address in address book '

    driver.get("https://opencart.abstracta.us/index.php?route=account/address")
    title = driver.title
    assert title == "Address Book", f"Expected title to be 'Address Book' but got '{title}'"

    create_prereq_address_recs(driver, 2) # If the current number of records is below 2, create more

    start_record_num = get_current_addr_record_num(driver) # Find how many records currently exist

    records = get_address_records(driver) # get all address records

    record = random.choice(records) # select a random record to be deleted

    record['delete-button'].click() # Click the delete button for the selected record

    final_record_num = get_current_addr_record_num(driver) # Check how many records now exist

    # Check if one record has been deleted
    assert start_record_num-1 == final_record_num, f"Incorrect number of records found. Expected {start_record_num-1}, Found {final_record_num})"

    driver.quit()


# pytest test_andrew.py::test_f16_s3
@create_session # create driver object, authenticate and set implicitly_wait to 10
def test_f16_s3(driver: webdriver.Chrome):
    ' Test Function 16 Scenario 3 - Edit address in address book '

    driver.get("https://opencart.abstracta.us/index.php?route=account/address")
    title = driver.title
    assert title == "Address Book", f"Expected title to be 'Address Book' but got '{title}'"

    create_prereq_address_recs(driver, 1) # If the current number of records is below 1, create more
    start_record_num = get_current_addr_record_num(driver)

    records = get_address_records(driver) # get all address records

    record_index = random.randrange(0, len(records))
    record = records[record_index] # select a random record to be edited

    record['edit-button'].click() # navigate to the edit menu
    time.sleep(1)

    # Verify title is correct
    title = driver.title
    assert title == "Address Book", f"Expected title to be 'Address Book' but got '{title}'"
    

    # Create a new value for the address
    new_address = f"{random.randrange(1,99)} {random.choice(['Example', 'Testing', 'Validation'])} {random.choice(['st', 'ln', 'dr'])}"

    # Update the address 1 input field
    address1 = driver.find_element(By.ID, "input-address-1")
    address1.clear()
    address1.send_keys(new_address)

    driver.find_element(By.CLASS_NAME, "btn-primary").click() # Submit form
    
    record = get_address_records(driver)[record_index] # Refresh the record list and grab the updated address

    found_address = record['address']

    # Check the address matches what was just submitted
    assert found_address == new_address, f"Incorrect address. Expected {new_address}. Found {found_address}"

    # Check no records were deleted or added
    final_record_num = get_current_addr_record_num(driver)
    assert start_record_num == final_record_num, f"Incorrect number of addresses. Expected {start_record_num}. Found {final_record_num}"

    driver.quit()


