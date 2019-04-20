#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import time

searchURL = "https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/suchen.html"

MAX_MAIN = 0
MIN_MAIN = 0
MAX_OTHER = 0
MIN_OTHER = 0
FREE = 0

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

class Semester:
    SS19 = "SS 2019"
    WS1819 = "WS 2018/19"
    SS18 = "SS 2018"
    WS1718 = "WS 2017/18"

class Degree:
    CS = "Computer Science"
    CE = "Computer Engineering"

class Module:
    def __init__(self, name, semester):
        self.name = name
        self.semester = semester

class Fields:
    DSE = "Data and Software Engineering"
    ESCA = "Embedded Systems and Computer Architectures"
    FOC = "Foundations of Computing"
    CS = "Cognitive Systems"
    HCI = "Human-Computer Interaction"
    DSN = "Distributed Systems and Networks"


xpaths = {
           'titleT' : '//*[@id="j_idt103:headpanel"]/div[2]/div/div/div/input',
           'semesterS' : '//*[@id="j_idt103:headpanel"]/div[3]/div[1]/div/select',
           'searchB' : '//*[@id="j_idt103:j_idt121"]',
           'modules' : '//*[@id="j_idt103:ergebnisliste_data"]/tr[1]/td[2]/a',
           'modulesN' : '//*[@id="j_idt103:ergebnisliste_data"]',
           'informationVersion' : '//*[@id="j_idt103:ergebnisliste_data"]/tr',
           'columnDescriptionURL' : './td[2]/a',
           'columnName' : './td[2]',
           'columnVersion' : './td[6]',
           'credits' : '//*[@id="j_idt105:BoxKopfzeile"]/div[1]/div[2]/div/span',
           'allowedDegrees' : '//*[@id="j_idt105:j_idt941"]/ul/li',
           'degreeDropDown' : './span/span[1]',
           'StuPODropDown' : './ul/li/span/span[1]',
           'moduleLists' : './ul/li/ul/li',
           'moduleListDropDown' : './span/span[1]',
           'fieldsDropDown' : './ul/li/span/span[1]',
           'fields' : './ul/li/ul/li',
           'searchFinishedDialog': '//*[@id="j_idt103:j_idt127"]/div/ul/li/span[2]'
         }

def searchModule(driver, module):
    driver.find_element_by_xpath(xpaths['titleT']).clear()
    driver.find_element_by_xpath(xpaths['titleT']).send_keys(module.name)
    Select(driver.find_element_by_xpath(xpaths['semesterS'])).select_by_visible_text(module.semester)
    driver.find_element_by_xpath(xpaths['searchB']).click()

    while True:
        time.sleep(0.1)
        search_finished=driver.find_elements_by_xpath(xpaths['searchFinishedDialog']) #Wait for AJAX to finish -> If Dialog exists, then it is ready
        if search_finished:
            break

def clickMaxVersionModule(driver, module):
    versions = driver.find_elements_by_xpath(xpaths['informationVersion'])
    viable_versions = [version for version in versions if version.find_element_by_xpath(xpaths['columnName']).text == module.name] #Filter all rows search results which have exactly the name of the module
    if not viable_versions:
        raise ValueError("Can't find search result in Moses matching exaclty {}".format(module.name))
    max_version_url = max(viable_versions, key=lambda item:int(item.find_element_by_xpath(xpaths['columnVersion']).text)).find_element_by_xpath(xpaths['columnDescriptionURL'])
    max_version_url.click()

def openDropDownMenus(degree, moduleSemester):
    #TODO Might have to be changed for degrees other than CS
    degree.find_element_by_xpath(xpaths['degreeDropDown']).click() 

    degree.find_element_by_xpath(xpaths['StuPODropDown']).click() #StuPO
    module_lists = degree.find_elements_by_xpath(xpaths['moduleLists'])
    module_list_right_semester = [ li for li in module_lists if moduleSemester in li.text ][0] #Should be only one
    module_list_right_semester.find_element_by_xpath(xpaths['moduleListDropDown']).click()
    module_list_right_semester.find_element_by_xpath(xpaths['fieldsDropDown']).click()
    return module_list_right_semester

def getFields(driver, my_degree, module):
    allowed_degrees=driver.find_elements_by_xpath(xpaths['allowedDegrees'])

    own_degree = [ degree for degree in allowed_degrees if my_degree in degree.find_element_by_xpath('./span/span[3]/a/span').text] #Name Degree, should be only one
    if not own_degree: #Can't find my degree in allowed degrees. Therefore, module has to be part of Wahlbereich
        raise ValueError()

    degree = own_degree[0]
    module_list = openDropDownMenus(degree, module.semester)
    fields = module_list.find_elements_by_xpath(xpaths['fields'])
    field_names = [field.text for field in fields]
    return field_names

def addCredits(field_names, credits):
    global MAX_MAIN
    global MIN_MAIN
    global MAX_OTHER
    global MIN_OTHER

    if len(field_names) == 0:
        raise ValueError("No fields for {}".format(module.name))

    #Assign everything possible to main field
    if len([name for name in field_names if main_field in name]) == 1:
        MAX_MAIN += credits
    else:
        MIN_OTHER += credits

    #Assign everything possible to other fields
    if len(field_names) >= 2:
        MAX_OTHER += credits
    elif len([name for name in field_names if main_field in name]) == 1:
        MIN_MAIN += credits
    else:
        MAX_OTHER += credits



def main(driver, my_degree, main_field, my_modules):
    for module in my_modules:
        print("Compute \"{}\"".format(module.name))
        driver.get(searchURL)
        searchModule(driver, module)

        clickMaxVersionModule(driver, module)

        credits=int(driver.find_element_by_xpath(xpaths['credits']).text.split()[0])#Cut away String "LP"


        try:
            field_names = getFields(driver, my_degree, module)
        except ValueError: # my_degree not in list for module -> Has to be part of Wahlbereich
            global FREE
            FREE+=credits
            continue
        addCredits(field_names, credits)


    print()
    print("Credits in \"Wahlbereich\": ", FREE)
    print()
    print("Minimum credits in \"Wahlpflicht vertieftes Studiengebiet\" if every possible module is added to \"Wahlpflicht Studiengebiete\": ", MIN_MAIN)
    print("Maximum credits in \"Wahlpflicht Studiengebiete\" if every possible module is added to it: ", MAX_OTHER)
    print()
    print("Maximum credits in \"Wahlpflicht vertieftes Studiengebiet\" if every possible module is added to it: ", MAX_MAIN)
    print("Minimum credits in \"Wahlpflicht Studiengebiete\" if every possible module is added to \"Wahlpflicht vertiefendes Studiengebiet\": ", MIN_OTHER)

    driver.quit()

my_degree = Degree.CS
main_field = Fields.CS
my_modules = [
    Module("The 800-pound Gorilla in the corner: Data Integration", Semester.SS19),
    Module("Machine Learning 1", Semester.WS1819),
    Module("Französisch - français langue universitaire (A1)", Semester.SS18)
]

main(driver, my_degree, main_field, my_modules)
