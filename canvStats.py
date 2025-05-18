import json
import os
import numpy as np
from canvasapi import Canvas
import copy

ruleSet = {}
myScore = {}
classScore = {}
storeName = "policy.json"
alias = {}

def __init__(aliasNew):
    global alias
    alias = aliasNew

def loadRuleSet(course, folderPath):
    global ruleSet, myScore, classScore
    storePath = f"{folderPath}/{storeName}"
    if (os.path.exists(storePath)):
        with open(storePath, "r", encoding="utf-8") as f:
            ruleSet = json.load(f)
    else:
        groups = course.get_assignment_groups(include=['rules'])
        ruleSet = {}
        for g in groups:
            data = (g.__dict__)
            rules = data.get('rules', {})
            gname = data['name']
            setArr = {
                'name'         : gname,
                'weight'       : data.get('group_weight'),
                'drop_lowest'  : rules.get('drop_lowest', 0),
                'drop_highest' : rules.get('drop_highest', 0),
                'never_drop'   : rules.get('never_drop', []),
            }
            if ('ec' in gname.lower() or ('extra' in gname.lower() and 'credit' in gname.lower())):
                setArr['ec'] = True
            ruleSet[str(g.id)] = setArr
        ruleSet["Overrides"] = {
            "Homework": {},
            "Participation": {},
            "Quiz": {},
            "Exam": {},
            "Final": {},
            "EC": {}
        }
        for name in (ruleSet['Overrides']):
            setArr = {
                'name': name,
                'active': False,
                'weight': 0,
                'drop_lowest': 0,
                'drop_highest': 0,
                'never_drop': [],
            }
            if (name == 'EC'):
                setArr['ec'] = True
            ruleSet["Overrides"][name] = setArr
        with open(storePath, "w", encoding="utf-8") as f:
            json.dump(ruleSet, f, indent=4)
    myScore = copy.deepcopy(ruleSet)
    classScore = copy.deepcopy(ruleSet)

    for curTbl in [myScore, classScore]:
        for name in (ruleSet['Overrides']):
            curTbl["Overrides"][name]["scores"] = []
            curTbl["Overrides"][name]["noDropScores"] = []
        for name in (ruleSet):
            if (name != "Overrides"):
                curTbl[name]["scores"] = []
                curTbl[name]["noDropScores"] = []
    return

def identifyAssignment(curRuleSet, name, id):
    global alias
    idStr = str(id)
    assert(curRuleSet[idStr])
    selRuleSet = None
    for override in (curRuleSet["Overrides"]):
        cur_alias = alias[override]
        data = curRuleSet["Overrides"][override]
        if not data["active"]:
            continue
        for val in cur_alias:
            if (val.lower() in name.lower() and (val != 'exam' or not "final" in name)):
                assert(not selRuleSet) # Make sure that it doesn't fit into 2+ categories
                selRuleSet = data
    if (not selRuleSet):
        selRuleSet = curRuleSet[idStr]
    return selRuleSet

def addStat(assignment, score, forMe):
    if (assignment.omit_from_final_grade):
        return # we don't care if it doesn't count for final grade!
    assert(len(ruleSet) > 0)
    totPoints = getattr(assignment, "points_possible", 0)
    selRuleSet = identifyAssignment(myScore if forMe else classScore, assignment.name, assignment.assignment_group_id)
    if assignment.name in selRuleSet["never_drop"]:
        selRuleSet["never_drop"].remove(assignment.name)
        selRuleSet["noDropScores"].append([score, totPoints])
    else:
        selRuleSet["scores"].append([score, totPoints])
    return

def calculateScore(forMe):
    global ruleSet, myScore, classScore
    selRuleSet = (myScore if forMe else classScore)
    results = {}

    categories = selRuleSet.copy()
    del categories["Overrides"]
    for idx, val in selRuleSet["Overrides"].items():
        if val["active"]:
            categories[idx] = val.copy()
    
    curScore = 0
    totScore = 0
    for catName, val in categories.items():
        if (val["weight"] > 0 and (len(val["scores"]) > 0 or len(val["noDropScores"]) > 0) and not val.get("ec", False)):
            totScore+=val["weight"]

    totPointsOnly = totScore <= 0
    for catName, val in (categories.items()):
        for idx2, name in enumerate(val["never_drop"]):
            print(f"[WARNING]: Name does not exist to avoid dropping: {val} (check spelling?); ignoring")
        if (val["weight"] <= 0 and not totPointsOnly):
            continue
        catScores = np.array(val["scores"], dtype='float', ndmin=2)
        for i in range(val["drop_lowest"]):
            if (len(catScores) <= 1):
                break
            idx_min = np.argmin(catScores[:,0]/catScores[:,1])
            catScores = np.delete(catScores, idx_min, axis=0)
        for i in range(val["drop_highest"]):
            if (len(catScores) <= 1):
                break
            idx_max = np.argmax(catScores[:,0]/catScores[:,1])
            catScores = np.delete(catScores, idx_max, axis=0)
        undroppableScores = np.array(val["noDropScores"], dtype='float', ndmin=2)
        if undroppableScores.size > 0:
            catScores = np.append(catScores, undroppableScores, axis=0)
        totPoints = np.sum(catScores[:,1]) if catScores.size > 0 else 0
        sumPoints = np.sum(catScores[:,0]) if totPoints > 0 else 0
        subScore = (sumPoints / totPoints) if totPoints else 0
        # if (not val["name"] in results or totPoints > 0):
        idx = 1
        putName = val["name"]
        while putName in results:
            idx += 1
            putName = f"{val["name"]}{idx}"
        results[putName] = ({"points": round(sumPoints, 2), "total": round(totPoints, 2), "percentage": round(subScore * 100, 2)})
        if (totPointsOnly):
            curScore += sumPoints
            totScore += (totPoints if not val.get("ec", False) else 0)
        else:
            curScore += val["weight"] * subScore
    # print(forMe, curScore, totScore)
    if totScore > 0:
        results["grade"] = round((curScore / totScore) * 100, 2)
    results["points"] = round(curScore, 2)
    results["total"] = totScore
    if forMe:
        myScore = {}
    else:
        classScore = {}
    ruleSet = {}
    # print("My Score:" if forMe else "Class Score:", results)
    return results

def main():
    print("MAIN")
if __name__ == "__main__":
    main()