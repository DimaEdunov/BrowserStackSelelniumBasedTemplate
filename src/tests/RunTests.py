# This class will make our lives easier once running test suites
import os
""" NOTICE : 
1) When you run a suite, make sure that all commands are in comment, beside 1
2) Edit the 'developer' variable value, and place your own name
3) Edit the brand you are running on = newforexstage2, analystq and so on
4) Edit Headless True/False
"""


"""Run command """
os.system("pytest -v -s --alluredir="'C:\AllureReports\BrowserStack'" --html=report.html --driver=safari --developer=dima --self-contained-html -m=regression --url=google")
