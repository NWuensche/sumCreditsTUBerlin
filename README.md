# Sum all Credits for your Fields at the Technische Universität Berlin

## Intention

Most master students at the TU Berlin have to fulfill the following criteria for their degree:

1. Have x credits in a specialization field ("Wahlpflicht vertieftes Studiengebiet")
2. Have y credits in all fields except the specialization field("Wahlpflicht Studiengebiete")
3. Have z credits in arbitrary modules ("Wahlbereich")

As modules can be part of multiple fields, it can be challenging for a student to keep overview if he or she already fulfilled all criteria.

This script helps you calculating the sum of all credits regarding these criteria. It uses the available information from "Moses".

The output is not guaranteed to be right.

## Dependencies
* Python 3
* Selenium
* Chromium/Chrome or Firefox

If you use Firefox, install `geckodriver` and change the lines

```
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)
```
to
```
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)
```

## How to Use

First off, change
```
my_degree = Degree.CS
```
to a member of `Degree` that represents your degree.

Next off, change
```
main_field = Fields.FOC
```
to a member of `Fields` that represents your specialization field.

Lastly, change
```
my_module=[
   Module("The 800-pound Gorilla in the corner: Data Integration", Semester.SS19),
...
]
```
to a list of `Module` object, where every `Module` consist of the *complete* name of the module which you can find on Moses and a `Semester` object which represents the semester you took the exam in this module.

In the end, the program calculates the possible maximum and minimum sums for the credits in all fields.

## How to Participate

If you found any mistakes, want to add more fields and degrees or have another idea to make this project better, any help will be welcome. Just create an issue or a pull request.
