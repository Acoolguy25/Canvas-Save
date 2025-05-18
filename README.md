# Abstract
This module saves all documents, feedback, and grading statistics (i.e. class averages) from the Canvas website using the [canvasapi](https://github.com/ucfopen/canvasapi) module to nested folders in the working directory.
# Getting Started
1) Install [canvasapi](https://github.com/ucfopen/canvasapi) module: ```pip install canvasapi```
2) Enter your canvas url in the ```canvas_url``` field. This should be the top level url of canvas url. For example, Illinois has [https://canvas.illinois.edu/](url). Do not include anything else.
3) Get your API key from the canvas website and copy it to the ```access_token```. Profile -> Settings -> New Access Token. Enter in an expiration date, but keep in mind the program will no longer work with an expired API key. ![image](https://github.com/user-attachments/assets/4d4b5f9a-db8c-4e21-b9f1-0e1897c0e7cc)
4) Run ```python save.py```
# Configuration
Below is an explaination of all the settings fields.
```json
{
    "canvas": {
        "canvas_url": "", # Insert your school's canvas url here
        "access_token": "", # Insert your personal access token
        "save": {
            "assignments": { # For individual assignments
                "stats": true, # Saves class stats for every individual assignments
                "feedback": false, # Saves your feedback for every individual assigments (only comments)
                "grade": true, # Saves your grade for every individual assignments
                "file": false # Saves your latest submitted file for every individual assigments
            },
            "overall": {
                "myScore": true, # Calculates  your individual final score
                "classScore": true, # Calculates class final score
                "classScoreType": "mean", # What metric is used for calculating class scores (i.e. mean, median, upper_q, lower_q, max, min)
                "toFile": true, # Enable to save all calculated scores to file
                "toConsole": false # Enable to print all calculate scores to console
            }
        },
        "override_alias": { # If course is poorly configured, and you enabled overrides for each category, names will take this grouping
            "Homework": ["homework", "hw"], # if homework or hw is in the name, assignments are classified as homework
            "Exam": ["exam", "midterm"], # if exam or midterm is in the name, assignments are classified as exam
            "Final": ["final"], # if final is in the name, assignments are classified as a final
            "Quiz": ["quiz", "quizlet"], # if quiz or quizlet is in the name, assignments are classified as quiz
            "Participation": ["participation", "attendance", "iClicker"], # if attendance, participation, or iclicker is in the name, assignments are classified as participation
            "EC": ["extra credit", "ec"] # if ec or extra credit is in the name, assignments are classified as extra credit
        }
    },
    "gradescope": { # Gradescope not yet supported. Maybe in the future?

    },
    "year": 2025, # Only saves classes from this year (4 digits, i.e. 2025)
    "term": "spring" # Only saves classes from this term (fall/spring)
}
```
Below is an explaination of all the policy under courses/[class name]/policy.json, which only appears after running ```save.py``` once:
```json
{
    "169206": { # automatically generated groupings show up here
        "name": "Assignments",
        "weight": 0.0, # if weight is zero, everything will be weighted equally
        "drop_lowest": 0,
        "drop_highest": 0,
        "never_drop": []
    },
    "Overrides": {
        "Homework": {
            "name": "Homework",
            "active": true, # whether this override is enabled
            "weight": 20, # if weight is zero, everything will be weighted equally
            "drop_lowest": 0,
            "drop_highest": 0,
            "never_drop": [] # assignment names to never drop
        },
        "Participation": {
            "name": "Participation",
            "active": true, # whether this override is enabled
            "weight": 20, # if weight is zero, everything will be weighted equally
            "drop_lowest": 0,
            "drop_highest": 0,
            "never_drop": [] # assignment names to never drop
        },
        "Quiz": {
            "name": "Quiz",
            "active": false, # whether this override is enabled
            "weight": 0, # if weight is zero, everything will be weighted equally
            "drop_lowest": 0,
            "drop_highest": 0,
            "never_drop": [] # assignment names to never drop
        },
        "Exam": {
            "name": "Exam",
            "active": true, # whether this override is enabled
            "weight": 15, # if weight is zero, everything will be weighted equally
            "drop_lowest": 0,
            "drop_highest": 0,
            "never_drop": [] # assignment names to never drop
        },
        "Final": {
            "name": "Final",
            "active": true, # whether this override is enabled
            "weight": 30, # if weight is zero, everything will be weighted equally
            "drop_lowest": 0,
            "drop_highest": 0,
            "never_drop": [] # assignment names to never drop
        }
    }
}```
