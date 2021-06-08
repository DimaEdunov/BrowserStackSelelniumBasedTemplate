import datetime
import os
import shutil
import subprocess
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from pathlib import Path
from datetime import *
import time
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.chrome.options import Options
import pytest
from selenium import webdriver
import smtplib

from page_objects.main_screen import main_screen




def pytest_addoption(parser):
    parser.addoption(
        "--driver", action="store", default="chrome", help="Returning name of browser")

    parser.addoption(
        "--url", action="store", default=None, help="Returning name of the brand")

    parser.addoption(
        "--headless", action="store", default="True", help="Returning Headless status")

    parser.addoption(
        "--developer", action="store", default="production", help="Returning Headless status")


# This method receives brand name from cmd, and returns the brand name to a test class
@pytest.fixture(scope="session")
def url_fixture(request):
    if request.config.getoption("--url") == None:
        return print("conftest.url(): url variable was not received")

    else:
        return request.config.getoption("--url")


# This method receives driver type from cmd (Default value = 'chrome'), and returns the driver to a test class
# THIS DRIVER IS FOR CRM TESTS ONLY
@pytest.fixture(scope="session")
def driver(request):

    global desired_cap
    global driver

    user_name = 'xxxxx'
    automated_key = 'yyyyy'
    BROWSERSTACK_URL = 'https://%s:%s@hub-cloud.browserstack.com/wd/hub'  % (user_name, automated_key)

    if request.config.getoption("--driver") == "safari":
        desired_cap = {

            'os': 'OS X',
            'os_version': 'Mojave',
            'browser': 'Safari',
            'browser_version': '12.1',
            'name': "pandats1's First Test",
            "browserstack.idleTimeout": "300"
        }


    elif request.config.getoption("--driver") == "chrome":
        desired_cap = {

            'os': 'Windows',
            'os_version': '10',
            'browser': 'Chrome',
            'browser_version': '90.0',
            'name': "pandats1's First Test"
        }


    driver = webdriver.Remote(
        command_executor=BROWSERSTACK_URL,
        desired_capabilities=desired_cap
    )

    target_url = request.config.getoption("--url")

    urls = get_url(target_url)

    main_screen_po = main_screen(driver, urls.get("main"))

    # Step 1: Go to crm main screen
    main_screen_po.go_to()

    yield driver

    time.sleep(1)

    # Quit driver
    driver.quit()

    # All in the following method will happen AFTER the session is ended - DO NOT change this method's name
    # This method contains : Sending Email, Invoking allure report on the screen
    # See additional documentation in here: https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_unconfigure
    try:

        pytest_unconfigure(config=None)

    except AttributeError:
        print("Ignore this error")


# Brand URL's
def get_url(url):
    if url == "google":
        return {"main": "https://www.google.com", "additional": "https://drive.google.com/drive/"}

    if url == "amazon":
        return {"main": "https://www.amazon.com", "additional": "https://www.primevideo.com/"}




# POST SESSION actions - HTML report sending by email, Allure report auto open
def pytest_unconfigure(config) -> None:
    import os.path

    print("URL : " + str(config.getoption('url')))
    print("DEVELOPER NAME : " + str(config.getoption("--developer")))

    """ Open Allure report """
    report_fire_up = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    print("Allure is opening up")
    os.popen("allure serve C:\AllureReports\Data")
    time.sleep(2)

    try:

        """ Time Calculation For HTML Report """
        # Path of report.html file within src/tests path
        base_path = Path(__file__).parent
        file_path = (base_path / "../tests/report.html").resolve()

        # Calculates raw timestamp of html report creation
        raw_value_of_report_creation_timestamp = os.path.getmtime(file_path)
        email_report_creation_time = datetime.fromtimestamp(raw_value_of_report_creation_timestamp)
        delta_time = datetime.now() - email_report_creation_time

        # Log of HTML report creation time
        print("Time passed since report was created in seconds - " + str(delta_time.seconds))

        if delta_time.seconds < 10:

            """ Subscription distribution for HTML report : 'Local' run vs 'Production' run """

            developer_list = {"dima": "dima.e@pandats.com",
                              "anastasiia": "anastasiia.vintrovich@pandats.com",
                              "natalie": "natalie.l@pandats.com"}

            # Helper variables for loop
            developer_list_length = len(developer_list)
            loop_counter = 0
            cc = None

            # Local run
            for list_developer_name, list_developer_email in developer_list.items():
                print("LOOP COUNTER - " + str(loop_counter))
                if config.getoption("--developer") == list_developer_name:
                    cc = list_developer_email
                    print("1 HTML Report Subscription sent to : " + str(cc))
                    break

                # Production
                if config.getoption("--developer") == "production":
                    cc = "dima.e+1@pandats.com,anastasiia.vintrovich@pandats.com"
                    print("2 HTML Report Subscription sent to :" + str(cc))
                    break
                loop_counter += 1

            """ Creation and sending of HTML report """
            # Building an email + HTML report attachment
            fromaddr = "pandaautomation.report@gmail.com"
            to = "dima.e@pandats.com"

            rcpt = cc.split(",") + [to]

            # instance of MIMEMultipart
            msg = MIMEMultipart()

            # storing the senders email address
            msg['From'] = fromaddr

            # storing the receivers email address
            msg['To'] = to

            msg['Cc'] = cc

            # storing the subject
            msg['Subject'] = "Automation %s suite run completed for the url : %s | %s " % (
            config.getoption('-m').title(),
            config.getoption('url').title(),
            str(datetime.today().strftime('%d-%m-%Y , %H:%M')))

            # string to store the body of the mail
            body = "Automation run has been completed. \n\n" \
                   "Time : " + str(datetime.today().strftime('%d-%m-%Y , %H:%M')) + "\n" \
                                                                                    "Brand : " + config.getoption(
                'url').title() + "\n" \
                                   "Suite : " + config.getoption('-m').title() + "\n\n\n" \
                                                                                 "To review the report - please download the file and open it locally on your device. \n\n" \
                                                                                 "- QA & Automation Team -"

            # attach the body with the msg instance
            msg.attach(MIMEText(body, 'plain'))

            # open the file to be sent
            filename = file_path
            attachment = open(filename, "rb")

            # instance of MIMEBase and named as p
            p = MIMEBase('application', 'octet-stream')

            # To change the payload into encoded form
            p.set_payload((attachment).read())

            # encode into base64
            encoders.encode_base64(p)

            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            # attach the instance 'p' to instance 'msg'
            msg.attach(p)

            # creates SMTP session
            s = smtplib.SMTP('smtp.gmail.com', 587)

            # start TLS for security
            s.starttls()

            # Authentication
            s.login("pandaautomation.report@gmail.com", "p4Mq4EEhUyEQ")

            # Converts the Multipart msg into a string
            text = msg.as_string()

            # sending the mail
            s.sendmail(fromaddr, rcpt, text)

            print("EMAIL SENT")

            # The temporary download directory removal
            shutil.rmtree("c:\\web-automation-downloads")

            # terminating the session
            s.quit()
    except OSError as e:
        pass