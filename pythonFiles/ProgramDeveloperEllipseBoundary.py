import random

import openai
import os
from OpenAI_ProgramDetails import LLMProgramDetails
from EllipseAgent import Agent

# ─────────────────────────────────────────────────────────────────
# CORE REDUCTION RULE
# Mirrors getActiveCores() in 53w53-program-diagram.html.
#
#   level < 0          → all 3 cores (basement: full BOH service)
#   t ≤ 0.55           → all 3 cores (public + lower residential)
#   0.55 < t ≤ 0.85    → drop freight elevator (mid-rise transfer)
#   t > 0.85           → single main elevator only (upper zone)
#
# Returns a set of raw type-string prefixes that are active.
# Comparison uses substring ('in') to tolerate minor naming variants.
# ─────────────────────────────────────────────────────────────────
ALL_CORE_PREFIXES = [
    'fire stair and freight elevator',
    'fire stair and elevator 1',
    'fire stair and elevator 2',
    'fire stair and elevator',   # legacy / LLM-generated fallback
]

def is_core_type(type_str):
    """Return True if type_str is any kind of fire-stair / elevator core."""
    return ('fire stair and freight elevator' in type_str or
            'fire stair and elevator' in type_str)

def get_active_cores(level, max_level):
    """Return the set of core-prefix strings active on this floor."""
    if level < 0:
        return set(ALL_CORE_PREFIXES)
    t = level / max(1, max_level)
    if t <= 0.55:
        return set(ALL_CORE_PREFIXES)
    elif t <= 0.85:
        # Freight elevator terminates at mid-rise transfer floor
        return {'fire stair and elevator 1',
                'fire stair and elevator 2',
                'fire stair and elevator'}
    else:
        # Only main stair + elevator continues to the upper zone
        return {'fire stair and elevator 1',
                'fire stair and elevator'}

def main():
    curDIR =os.getcwd()
    DIRpath = os.path.join(curDIR, 'fileTransfer')
    modeSwitch = 1
    minCorner = [10, 1]
    maxCorner = [26, 31]
    if modeSwitch == 0:
        myDetails = LLMProgramDetails(DIRpath)
        myLines = myDetails.refineProgram('RoughProgram.txt')
        outFile = "output.txt"
        outPath = os.path.join(DIRpath, outFile)
        with open(outPath, 'w') as f:
            f.write(myLines)

    elif modeSwitch == 1:
        #   import core list 在RHINO中設定好樓梯的位置，把點座標放入txt
        #import core list
        coreFile = "cores.txt"
        corePath = os.path.join(DIRpath, coreFile)
        cf = open(corePath, 'r')
        clines = cf.readlines()
        corePts = []
        for line in clines:
            if len(line) > 0:
                vals = line.split(',')
                x = float(vals[0])
                y = float(vals[1])
                vert = (x,y)
                corePts.append(vert)

        #import site boundary
        boundFIle = "border.txt"
        boundPath = os.path.join(DIRpath, boundFIle)
        bf = open(boundPath, 'r')
        bLines = bf.readlines()
        boundaryVerts = []
        for line in bLines:
            if len(line) > 3:
                vals = line.split(',')
                x = float(vals[0])
                y = float(vals[1])
                vert = (x,y)
                boundaryVerts.append(vert)

        inFile = "output.txt"
        inPath = os.path.join(DIRpath, inFile)
        f = open(inPath, 'r')
        myLines = f.readlines()
        newLines = []
        agentList = []
        floorLevels = []
        for i in range(len(myLines)):
            if len(myLines[i])>3:
                myLine = myLines[i]
                myLine = myLine.replace('{','')
                myLine = myLine.replace('}','')
                vals = myLine.split('/')
                floorLevel = int(vals[2])
                floorLevels.append(floorLevel)
                temp = [vals[0],float(vals[1]),floorLevel,vals[3],vals[4]]
                newLines.append(temp)

        floorLevels = list(set(floorLevels))
        floorLevels.sort()
        minLevel    = -1 * floorLevels[0]
        maxFloorLevel = floorLevels[-1]   # used for proportional core-reduction threshold

        for i in range(len(floorLevels)):
            temp = []
            agentList.append(temp)

        for line in newLines:
            floorLevel = line[2]
            z    = floorLevel + minLevel
            type = line[0]

            # ── Core reduction: skip cores inactive on this floor ──────
            if is_core_type(type):
                active = get_active_cores(floorLevel, maxFloorLevel)
                # Check if any active prefix matches this type string
                if not any(prefix in type for prefix in active):
                    continue   # core shaft does not extend to this floor

            x = random.random() * (maxCorner[0] - minCorner[0]) + minCorner[0]
            y = random.random() * (maxCorner[1] - minCorner[1]) + minCorner[1]
            area = line[1]
            rads = line[4].split(',')
            w = float(rads[0])
            h = float(rads[1])

            # ── Pin cores to their designated anchor points ───────────
            # corePts[0] = freight elevator  (service / loading side)
            # corePts[1] = elevator 1        (main passenger)
            # corePts[2] = elevator 2        (secondary passenger, optional)
            if 'fire stair and freight elevator' in type:
                x, y = corePts[0]
            elif 'fire stair and elevator 1' in type:
                x, y = corePts[1] if len(corePts) > 1 else corePts[0]
            elif 'fire stair and elevator 2' in type:
                x, y = corePts[2] if len(corePts) > 2 else corePts[min(1, len(corePts) - 1)]
            elif 'fire stair and elevator' in type:
                # Legacy / LLM-generated single elevator name
                x, y = corePts[1] if len(corePts) > 1 else corePts[0]

            myAgent = Agent(x, y, z, area, w, h, type, line[3], boundaryVerts)
            agentList[z].append(myAgent)

        ##run our simulation
        for level in agentList:
            for g in range(5000):
                for myAgent in level:
                    myAgent.update(agentList)



        ##output agent values to Rhino
        fName = 'outAgent.txt'
        fPath = os.path.join(DIRpath, fName)
        outFile = open(fPath, 'w')
        for i in range(len(agentList)):
            for j in range(len(agentList[i])):
                tempString = agentList[i][j].outputValues() +'\n'
                outFile.write(tempString)









if __name__ == "__main__":
    main()





