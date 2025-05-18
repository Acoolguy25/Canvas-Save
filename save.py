import json
import os
from canvasapi import Canvas
import canvStats
import re

with open("settings.json") as f:
    settings = json.load(f)

canvasSettings = settings["canvas"]
canvasSave = canvasSettings["save"]
assert("canvas" in canvasSettings["canvas_url"].lower())
canvas = Canvas(canvasSettings["canvas_url"], canvasSettings["access_token"])
meUser = canvas.get_current_user()
rootPath = "./courses"

termAndYear = f"{settings["term"]} {settings["year"]}"

def getCourseName(name):
    # name = name.replace("-", "")
    name = name.removeprefix(termAndYear.capitalize()).removeprefix(" ").removeprefix("-")
    splits = re.split(r"[\s-]+", name)
    print(name, splits)
    return f"{splits[0]} {splits[1]}"

def round_floats(obj):
    if isinstance(obj, float):
        return round(obj, 3)
    elif isinstance(obj, dict):
        return {k: round_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v) for v in obj]
    else:
        return obj

def deleteInvalidPathNames(name):
    return name.replace(":", "")[0:30].removesuffix(" ")

os.makedirs(rootPath, exist_ok=True)
canvStats.__init__(canvasSettings["override_alias"])
    
# courses: Iterator[Course] = canvas.get_courses()
for idx, course in enumerate(canvas.get_courses()):
    if ("name" in dir(course) and course.name.lower().startswith(termAndYear)):
        if ("ECE 391" in course.name):
            course_name = getCourseName(course.name)
            course_path = f"{rootPath}/{course_name.replace(' ','')}"
            os.makedirs(course_path, exist_ok=True)
            if (canvasSave["overall"]["myScore"] or canvasSave["overall"]["classScore"]):
                canvStats.loadRuleSet(course, course_path)
            for idx, assignment in enumerate(course.get_assignments(include=["attachments", "submission", "score_statistics"])):
                assignment_path = f"{course_path}/{deleteInvalidPathNames(assignment.name)}"
                submission = assignment.get_submission(meUser, include=["submission_comments"])
                if canvasSave["assignments"]["file"]:
                    for num, file in enumerate(submission.attachments or []):
                        fileType = file.filename.split(".")[-1]
                        local_path = os.path.join(assignment_path, deleteInvalidPathNames(assignment.name) + "." + fileType)
                        os.makedirs(assignment_path, exist_ok=True)
                        file.download(local_path)
                score_stats = getattr(assignment, "score_statistics", None)
                myScore = getattr(submission, 'score', None)
                if (score_stats or myScore):
                    storeJson = {
                        "score": myScore,
                        "total": getattr(assignment, "points_possible", 0),
                    }
                    if (score_stats):
                        standard_deviation = (score_stats['upper_q'] - score_stats['lower_q']) / 1.35
                        score_stats["estDeviation"] = standard_deviation
                        if (myScore and standard_deviation != 0):
                            storeJson["deviationMultiples"] = (myScore - score_stats["mean"]) / standard_deviation
                        if (canvasSave["assignments"]["stats"]):
                            os.makedirs(assignment_path, exist_ok=True)
                            with open(f"{assignment_path}/statistics.json", "w", encoding="utf-8") as f:
                                json.dump(round_floats(score_stats), f, ensure_ascii=False, indent=4)
                        if canvasSave["overall"]["classScore"]:
                            canvStats.addStat(assignment, score_stats[canvasSave["overall"]["classScoreType"]], False)
                    if (canvasSave["assignments"]["grade"]):
                        os.makedirs(assignment_path, exist_ok=True)
                        with open(f"{assignment_path}/grade.json", "w", encoding="utf-8") as f:
                            json.dump(round_floats(storeJson), f, ensure_ascii=False, indent=4)
                        if canvasSave["overall"]["myScore"]:
                            canvStats.addStat(assignment, myScore, True)
                if canvasSave["assignments"]["feedback"]:
                    comments = []
                    for idx, comment in enumerate(getattr(submission, "submission_comments", [])):
                        comments.append({
                            'message': comment.get("comment"),
                            'author': comment.get("author_name"),
                            'created_at': comment.get('created_at'),
                            'author_id': comment.get("author_id")
                        })
                    if len(comments) > 0:
                        os.makedirs(assignment_path, exist_ok=True)
                        with open(f"{assignment_path}/feedback.json", "w", encoding="utf-8") as f:
                            json.dump(comments, f, ensure_ascii=False, indent=4)
            
            if (canvasSave["overall"]["myScore"]):
                results = canvStats.calculateScore(True)
                if (canvasSave["overall"]["toConsole"]):
                    print("Your Score:", json.dumps(results, indent=4))
                if (canvasSave["overall"]["toFile"]):
                    with open(f"{course_path}/student_grades.json", "w", encoding="utf-8") as f:
                            json.dump(results, f, ensure_ascii=False, indent=4)
            if (canvasSave["overall"]["classScore"]):
                results2 = canvStats.calculateScore(False)
                if (canvasSave["overall"]["toConsole"]):
                    print("Class Score:", json.dumps(results2, indent=4))
                if (canvasSave["overall"]["toFile"]):
                    with open(f"{course_path}/class_grades.json", "w", encoding="utf-8") as f:
                            json.dump(results2, f, ensure_ascii=False, indent=4)
