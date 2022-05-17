import sys
import make2Dwires
import os

INPUTFILE_DIR = "/home/rickysuave/Documents/OSUClasses/VLSILab/FasterCap_main/InputFiles/2D/"

MET_START = [0, 1, 6, 12, 18]
MET_THICKNESS = [0.25, 
				 0.05, 0.35, 0.05, 0.05, 0.15, 
				 0.05, 0.2, 0.02, 0.05, 0.2, 0.05, 
				 0.05, 0.2, 0.02, 0.05, 0.2, 0.05,
				 0.05, 0.2, 0.02, 0.05, 0.2, 0.05]
MET_CONST = ["4.1e-6", 
			 "7.0e-6", "4.3e-6", "4.3e-6", "4.9e-6", "4.1e-6", 
			 "4.9e-6", "2.9e-6", "4.4e-6", "4.9e-6", "2.9e-6", "4.4e-6", 
			 "4.9e-6", "2.9e-6", "4.4e-6", "4.9e-6", "2.9e-6", "4.4e-6",
			 "4.9e-6", "2.9e-6", "4.4e-6", "4.9e-6", "2.9e-6", "4.4e-6"]


SPACINGS = [0.14, 0.21, 0.28, 0.35, 0.42, 0.56, 0.7, 1.0, 1.4]
DIAG_SPACINGS = [0.0, 0.056, 0.14, 0.196, 0.28, 0.56, 0.84]

def parseCurrentMet_Sub(index):

	for i in range(1, 6):
		if(index >= MET_START[i] and index < MET_START[i+1]):
			sublayer = index - (MET_START[i] - 1)
			return i, sublayer

	if(index >= MET_START[7] and index < MET_START[7]+6):
		sublayer = index - (MET_START[7] - 1)
		return 7, sublayer

	print("ERROR: Index is out of bounds of current process stack")
	return -1, -1
 
def parseThickness(metal, sublayer):

	index = MET_START[metal+1] - 3 + sublayer
	sub = MET_START[metal+1] - MET_START[metal] - 2 + sublayer

	return MET_THICKNESS[index], sub

def parseTrueTotThickness(metal, sublayer):

	if(metal == 0 and sublayer == 0):
		return -1.0

	index = MET_START[metal] + sublayer - 1

	totThickness = 0
	for i in range(index):
		totThickness += MET_THICKNESS[i]

	return totThickness

def parseTotThickness(metal, sublayer):

	if(metal == 0 and sublayer == 0):
		return -1.0

	index = MET_START[metal+1] - 3 + sublayer

	totThickness = 0
	for i in range(index):
		totThickness += MET_THICKNESS[i]

	return totThickness

def parseTrueDielectricConstant(metal, sublayer):

	index = MET_START[metal] + sublayer - 1

	return MET_CONST[index]

def parseDielectricConstant(metal, sublayer):

	if(metal == 0 and sublayer == -1):
		return "1.0e-6"

	index = MET_START[metal+1] - 3 + sublayer

	return MET_CONST[index]


def parseGndThickness(metal):

	if(metal == 0):
		sublayer = input("M0 or P1? (Answer 0 or 1, respectively): ")
		if(int(sublayer) == 0):
			return 1.0, 0
		elif(int(sublayer) == 1):
			return MET_THICKNESS[0], 1
		else:
			print("ERROR: Wrong input for sublayer")

	index = MET_START[metal+1] - 3

	totThickness = 0
	for i in range(index, index+3):
		totThickness += MET_THICKNESS[i]

	return totThickness, 101


def parseUM(measurement):

    line = ""

    index = measurement.index(".")
    if(index <= 0 or len(measurement) > 8 or len(measurement) < 3):
        printf("Error in measurement. Incorrect format")
        return -1

    for i in range(0, len(measurement)):
        if(i == index):
            continue
        line = line + measurement[i]

    return line


def writeProcessStack(fileObject, metal, underMet, sublayer, overMet, diagMet, windowWidth):

	flag = 0

	if(underMet != -1 and overMet != -1):
		start = overMet
		end = underMet
	elif(underMet != -1 and overMet == -1):
		start = 0
		end = underMet
	elif(underMet == -1 and overMet != -1):
		start = 0
		end = metal+1
		flag = 1
	else:
		start = 0
		end = diagMet+1
		flag = 1

	midWindowWidth = windowWidth / 2

	if(start == 0 and sublayer != 1):	
		filename = make2Dwires.make2Dwires(windowWidth, MET_THICKNESS[0], 0, 1, 0)
		line = "* P1 Dielectric\n*\n"
		fileObject.write(line)
		line = "D ../P1/{}_sides.txt\t\t{} {}\t\t{:0.3f} {}\t\t\t{:0.3f} {} -\n".format(filename, "1.0e-6", MET_CONST[0], -1*midWindowWidth, "0.0", -1*midWindowWidth+0.01, "0.01")
		fileObject.write(line)
		line = "D ../P1/{}_top.txt\t\t{} {}\t\t{:0.3f} {}\t\t\t{:0.3f} {} -\n".format(filename, MET_CONST[1], MET_CONST[0], -1*midWindowWidth, "0.0", -1*midWindowWidth+0.01, "0.01")
		fileObject.write(line)
		line = "*\n*\n*\n"
		fileObject.write(line)

	for i in range(MET_START[start+1], MET_START[end+1]-3):

		if(i >= (MET_START[metal+1]-3) and i < MET_START[metal+1]):
			continue
		if(diagMet != -1):
			if(i >= (MET_START[diagMet+1]-3) and i < MET_START[diagMet+1]):
				continue

		currentMet, currentSub = parseCurrentMet_Sub(i)
		totThickness = parseTrueTotThickness(currentMet, currentSub)

		if(i == (MET_START[end+1]-4) and flag == 1):
			nextDielectricConst = "1.0e-6"
		else:
			nextDielectricConst = parseTrueDielectricConstant(currentMet, currentSub+1)

		if(currentMet != metal):
			path = "../M{}/".format(currentMet)
		else:
			path = ""

		filename = make2Dwires.make2Dwires(windowWidth, MET_THICKNESS[i], currentMet, currentSub, 0)
		line = "* M{}_{} Dielectric\n*\n".format(currentMet, currentSub)
		fileObject.write(line)
		line = "D {}{}_sides.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(path, filename, "1.0e-6", MET_CONST[i], -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
		fileObject.write(line)

		if((i+1) != (MET_START[metal+1]-3)):
			if(underMet != -1):
				if((i+1) != (MET_START[underMet+1]-3)):
					line = "D {}{}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(path, filename, nextDielectricConst, MET_CONST[i], -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
					fileObject.write(line)
			elif(diagMet != -1):
				if((i+1) != (MET_START[diagMet+1]-3)):
					line = "D {}{}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(path, filename, nextDielectricConst, MET_CONST[i], -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
					fileObject.write(line)
			else:
				line = "D {}{}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(path, filename, nextDielectricConst, MET_CONST[i], -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
				fileObject.write(line)


		line = "*\n*\n*\n"
		fileObject.write(line)



def writeDiagonal(fileObject, windowWidth, wireWidth, spacing, metal, diagMet):

	wireDiagFilename = []
	wireFilename = []
	metSpacing = 0.14
	midWidth = wireWidth/2
	midWindowWidth = windowWidth/2

	for i in range(3):

		dieFileNames = []

		thickness, sublayer = parseThickness(diagMet, i)
		dieFileNames.append(make2Dwires.make2Dwires(wireWidth, thickness, diagMet, sublayer, 0))
		print('Creating wire M{}_{} of thickness {}'.format(diagMet, sublayer, thickness))
		wireDiagFilename.append(make2Dwires.make2Dwires(wireWidth, thickness, diagMet, sublayer, 1))

		metThickness, metSublayer = parseThickness(metal, i)
		print('Creating wire M{}_{} of thickness {}'.format(metal, metSublayer, metThickness))
		wireFilename.append(make2Dwires.make2Dwires(wireWidth, metThickness, metal, metSublayer, 1))

		## Calculating left and right dielectric widths
		rightDieWidth = (windowWidth/2) + (spacing - wireWidth/2)
		dieFileNames.append(make2Dwires.make2Dwires(rightDieWidth, thickness, diagMet, sublayer, 0))
		leftDieWidth = (windowWidth/2) - (spacing + 7*wireWidth - wireWidth/2)
		dieFileNames.append(make2Dwires.make2Dwires(leftDieWidth, thickness, diagMet, sublayer, 0))

		## Dielectrics of front and back of wires
		dieFileNames.append(make2Dwires.make2Dwires(windowWidth, thickness, diagMet, sublayer, 0))

		## Parameters for FasterCap Input File
		nextDielectricConst = parseDielectricConstant(diagMet, i+1)
		currentConst = parseDielectricConstant(diagMet, i)
		previousConst = parseDielectricConstant(diagMet, i-1)
		totThickness = parseTotThickness(diagMet, i)

		## Writing Dielectrics in between wires
		line = "* M{}_{} Dielectric\n*\n".format(diagMet, sublayer)
		fileObject.write(line)
		origin = -1*spacing + wireWidth/2
		line = "D ../M{}/{}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(diagMet, dieFileNames[1], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
		fileObject.write(line)
		for j in range(3):
			origin = origin - 2*wireWidth
			line = "D ../M{}/{}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(diagMet, dieFileNames[0], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
			fileObject.write(line)
		origin = -1*windowWidth/2
		line = "D ../M{}/{}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(diagMet, dieFileNames[2], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
		fileObject.write(line)
		line = "D ../M{}/{}_sides.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t\t{:0.3f} {:0.3f} -\n".format(diagMet, dieFileNames[3], "1.0e-6", currentConst, -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
		fileObject.write(line)

		if(i==0):
			origin = -1*spacing + wireWidth/2
			line = "D ../M{}/{}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(diagMet, dieFileNames[1], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
			fileObject.write(line)
			for j in range(3):
				origin = origin - 2*wireWidth
				line = "D ../M{}/{}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(diagMet, dieFileNames[0], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
				fileObject.write(line)
			origin = -1*windowWidth/2
			line = "D ../M{}/{}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(diagMet, dieFileNames[2], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
			fileObject.write(line)


		line = "*\n*\n*\n"
		fileObject.write(line)
		
		## Dielectrics for Under Metal
		dieFileNames = []
		dieFileNames.append(make2Dwires.make2Dwires(wireWidth, metThickness, metal, metSublayer, 0))
		dieFileNames.append(make2Dwires.make2Dwires(metSpacing, metThickness, metal, metSublayer, 0))

		left_dielectric = midWindowWidth - (5*wireWidth + metSpacing + midWidth)
		left_dielectric = "%0.2f" % left_dielectric
		dieFileNames.append(make2Dwires.make2Dwires(left_dielectric, metThickness, metal, metSublayer, 0))

		right_dielectric = midWindowWidth - (3*wireWidth + metSpacing + midWidth)
		right_dielectric = "%0.2f" % right_dielectric
		dieFileNames.append(make2Dwires.make2Dwires(right_dielectric, metThickness, metal, metSublayer, 0))

		dieFileNames.append(make2Dwires.make2Dwires(windowWidth, metThickness, metal, metSublayer, 0))

		nextDielectricConst = parseDielectricConstant(metal, i+1)
		currentConst = parseDielectricConstant(metal, i)
		previousConst = parseDielectricConstant(metal, i-1)
		totThickness = parseTotThickness(metal, i)


		line = "* M{}_{} Dielectric\n*\n".format(metal, metSublayer)
		fileObject.write(line)
		origin = -1*midWidth-metSpacing
		line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[1], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
		fileObject.write(line)
		for y in range(2):
			origin = origin - 2*wireWidth
			line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[0], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
			fileObject.write(line)
		line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[2], nextDielectricConst, currentConst, -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
		fileObject.write(line)

		origin = midWidth
		line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[1], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
		fileObject.write(line)
		origin = origin + metSpacing + wireWidth
		line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[0], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
		fileObject.write(line)
		origin = origin + 2*wireWidth
		line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[3], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
		fileObject.write(line)

		line = "D {}_sides.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[4], "1.0e-6", currentConst, -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
		fileObject.write(line)

		if(i == 0):
			origin = -1*midWidth-metSpacing
			line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[1], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
			fileObject.write(line)
			for y in range(2):
				origin = origin - 2*wireWidth
				line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[0], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
				fileObject.write(line)
			line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[2], previousConst, currentConst, -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
			fileObject.write(line)

			origin = midWidth
			line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[1], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
			fileObject.write(line)
			origin = origin + metSpacing + wireWidth
			line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[0], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
			fileObject.write(line)
			origin = origin + 2*wireWidth
			line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[3], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
			fileObject.write(line)

		line = "*\n*\n*\n"
		fileObject.write(line)



	## Writing Metal
	line = "*\n*\n* Metals\n* ===========================\n*\n*\n"
	fileObject.write(line)

	## Diagonal Metal Wires
	line = "* M{} Wires\n*\n".format(diagMet)
	fileObject.write(line)
	origin = -1*wireWidth/2 - spacing
	startIndex = MET_START[metal+1] - 3
	for j in range(4):
		line = "* W{}\n*\n".format(j)
		fileObject.write(line)
		for i in range(3):
			if(i == 0):
				line = "C ../M{}/{}_bottom.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(diagMet, wireDiagFilename[0], MET_CONST[startIndex-1], origin, parseTotThickness(diagMet, i))
				fileObject.write(line)
			line = "C ../M{}/{}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(diagMet, wireDiagFilename[i], MET_CONST[startIndex+i], origin, parseTotThickness(diagMet, i))
			fileObject.write(line)
			if(i == 2):
				line = "C ../M{}/{}_top.txt\t\t{}\t\t{:0.3f} {:0.3f}\n".format(diagMet, wireDiagFilename[2], MET_CONST[startIndex+3], origin, parseTotThickness(diagMet, 2))
				fileObject.write(line)
		origin = origin - 2*wireWidth
		line = "*\n*\n*\n"
		fileObject.write(line)

	## Under Metal Wires
	line = "* M{} Wires\n*\n".format(metal)
	fileObject.write(line)
	startIndex = MET_START[metal+1] - 4
	for j in range(6):
		if(j == 0):
			origin = -1*(5*wireWidth + 0.14 + wireWidth/2)
		elif(j > 0 and j < 3) or (j == 5):
			origin = origin + 2*wireWidth
		elif(j > 2 and j < 5):
			origin = origin + wireWidth + metSpacing

		line = "* W{}\n*\n".format(j)
		fileObject.write(line)
		line = "C {}_bottom.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(wireFilename[0], MET_CONST[startIndex], origin, parseTotThickness(metal, 0))
		fileObject.write(line)
		line = "C {}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(wireFilename[0], MET_CONST[startIndex+1], origin, parseTotThickness(metal, 0))
		fileObject.write(line)
		line = "C {}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(wireFilename[1], MET_CONST[startIndex+2], origin, parseTotThickness(metal, 1))
		fileObject.write(line)
		line = "C {}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(wireFilename[2], MET_CONST[startIndex+3], origin, parseTotThickness(metal, 2))
		fileObject.write(line)
		line = "C {}_top.txt\t\t{}\t\t{:0.3f} {:0.3f}\n".format(wireFilename[2], MET_CONST[startIndex+4], origin, parseTotThickness(metal, 2))
		fileObject.write(line)
		line = "*\n*\n*\n"
		fileObject.write(line)

	line = "*\n*\n*\n"
	fileObject.write(line)

	## Ground Plane
	m0gndName = make2Dwires.make2Dwires(windowWidth, 1.0, 0, 0, 1)
	nextDielectricConst = MET_CONST[0]

	line = "* M0 GND Plane\n*\n"
	fileObject.write(line)
	line = "C ../M0/{}_bottom.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(m0gndName, "1.0e-6", -1*midWindowWidth, -1.0)
	fileObject.write(line)
	line = "C ../M0/{}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(m0gndName, "1.0e-6", -1*midWindowWidth, -1.0)
	fileObject.write(line)
	line = "C ../M0/{}_top.txt\t\t{}\t\t{:0.3f} {:0.3f}\n".format(m0gndName, nextDielectricConst, -1*midWindowWidth, -1.0)
	fileObject.write(line)
	line = "*\n*\n*\n"
	fileObject.write(line)




if __name__ == "__main__":

	if(len(sys.argv) != 5):
		print("Usage: make2Dpatterns.py <window width> <wire width> <metal layer> <over/under/overunder flag>")
		print("** NOTE ** : -o, -u, and -ou are the flags for over, under, and overunder respectively")
		exit()

	windowWidth, width, strMetal, flag = sys.argv[1:5]

	underMet = -1
	overMet = -1
	diagMet = -1
	pattern = "M{}".format(strMetal)

	metal = int(strMetal)
	if(metal < 0 or metal > 6):
		print("ERROR: Metal layer needs to be an int inbetween 0 and 6")
		exit()

	if(flag.find("-du") != -1):
		diagMet = input("Metal Layer for Diagonal Under: ")
		if(int(diagMet) <= metal or int(diagMet) > 6):
			print("ERROR: Diagonal Under metal is incorrect")
			exit()
		pattern = "{}duM{}".format(pattern, diagMet)
	else:
		if(flag.find("-o") != -1):
			overMet = input("Metal Layer for Over: ")
			if(int(overMet) >= metal or int(overMet) < 0):
				print("ERROR: Over metal is less than main metal layer")
				exit()
			pattern = "{}oM{}".format(pattern, overMet)
		if(flag.find("u") != -1):
			underMet = input("Metal Layer for Under: ")
			if(int(underMet) <= metal or int(underMet) > 6):
				print("ERROR: Under metal is greater than main metal layer")
				exit()
			pattern = "{}uM{}".format(pattern, underMet)
		if(underMet == -1 and overMet == -1 and diagMet == -1):
			print("ERROR: Incorrect flag")
			exit()

	parseWindowWidth = parseUM(windowWidth)
	parseWidth = parseUM(width)

	intWindowWidth = float(windowWidth)
	intWidth = float(width)

	midWindowWidth = intWindowWidth / 2
	midWidth = intWidth / 2

	command = 'python make2Dwires.py '
	fullcommand = ''
	fileName = "wires_{}_W{}".format(pattern, parseWidth)


	if(diagMet == -1):
		for i in range(len(SPACINGS)):

			wireFileNames = []

			parseSpacing = parseUM(str(SPACINGS[i]))
			newFileName = "{}_S{}_newTest.lst".format(fileName, parseSpacing)
			fullFileName = "{}M{}/{}".format(INPUTFILE_DIR, strMetal, newFileName)

			try:
				fileObject = open(fullFileName, "x")
			except:
				print("Failed to create {}".format(fullFileName))
				continue

			print("\n===============================================")
			print("Created file: {}".format(fullFileName))

			## File Header
			line = "* 2D\n*\n*\n*\n"
			fileObject.write(line)

			line = "* Dielectrics\n*=========================\n*\n*\n"
			fileObject.write(line)

			for j in range(3):

				dieFileNames = []
				
				print('Creating wire file of width: {}'.format(str(SPACINGS[i])))
				fullcommand = command + str(SPACINGS[i]) + ' '

				thickness, sublayer = parseThickness(metal, j)
				fullcommand = fullcommand + str(thickness) + ' '

				commandMetal = strMetal + '_' + str(sublayer)
				fullcommand = fullcommand + commandMetal

				print("Would run this command: {}".format(fullcommand))

				wireFileNames.append(make2Dwires.make2Dwires(intWidth, thickness, metal, sublayer, 1))
				dieFileNames.append(make2Dwires.make2Dwires(intWidth, thickness, metal, sublayer, 0))
				dieFileNames.append(make2Dwires.make2Dwires(SPACINGS[i], thickness, metal, sublayer, 0))

				print("midWindow: {}\tintWidth: {}\tSPACINGS[{}]: {}\tmidWidth: {}".format(midWindowWidth, intWidth, i, SPACINGS[i], midWidth))
				left_dielectric = midWindowWidth - (5*intWidth + SPACINGS[i] + midWidth)
				left_dielectric = "%0.2f" % left_dielectric
				dieFileNames.append(make2Dwires.make2Dwires(left_dielectric, thickness, metal, sublayer, 0))

				right_dielectric = midWindowWidth - (3*intWidth + SPACINGS[i] + midWidth)
				right_dielectric = "%0.2f" % right_dielectric
				dieFileNames.append(make2Dwires.make2Dwires(right_dielectric, thickness, metal, sublayer, 0))

				dieFileNames.append(make2Dwires.make2Dwires(intWindowWidth, thickness, metal, sublayer, 0))

				nextDielectricConst = parseDielectricConstant(metal, j+1)
				currentConst = parseDielectricConstant(metal, j)
				previousConst = parseDielectricConstant(metal, j-1)
				totThickness = parseTotThickness(metal, j)


				line = "* M{}_{} Dielectric\n*\n".format(metal, sublayer)
				fileObject.write(line)
				origin = -1*midWidth-SPACINGS[i]
				line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[1], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
				fileObject.write(line)
				for y in range(2):
					origin = origin - 2*intWidth
					line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[0], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
					fileObject.write(line)
				line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[2], nextDielectricConst, currentConst, -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
				fileObject.write(line)

				origin = midWidth
				line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[1], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
				fileObject.write(line)
				origin = origin + SPACINGS[i] + intWidth
				line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[0], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
				fileObject.write(line)
				origin = origin + 2*intWidth
				line = "D {}_top.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[3], nextDielectricConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
				fileObject.write(line)

				line = "D {}_sides.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[4], "1.0e-6", currentConst, -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
				fileObject.write(line)

				if(j == 0):
					origin = -1*midWidth-SPACINGS[i]
					line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[1], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
					fileObject.write(line)
					for y in range(2):
						origin = origin - 2*intWidth
						line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[0], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
						fileObject.write(line)
					line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[2], previousConst, currentConst, -1*midWindowWidth, totThickness, -1*midWindowWidth+0.01, totThickness+0.01)
					fileObject.write(line)

					origin = midWidth
					line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[1], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
					fileObject.write(line)
					origin = origin + SPACINGS[i] + intWidth
					line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[0], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
					fileObject.write(line)
					origin = origin + 2*intWidth
					line = "D {}_bottom.txt\t\t{} {}\t\t{:0.3f} {:0.3f}\t\t\t{:0.3f} {:0.3f} -\n".format(dieFileNames[3], previousConst, currentConst, origin, totThickness, origin+0.01, totThickness+0.01)
					fileObject.write(line)

				line = "*\n*\n*\n"
				fileObject.write(line)


			line = "*\n*\n* Metals\n* ===========================\n*\n*\n"
			fileObject.write(line)
			for j in range(6):
				if(j == 0):
					origin = -1*(5*intWidth + SPACINGS[i] + midWidth)
				elif(j > 0 and j < 3) or (j == 5):
					origin = origin + 2*intWidth
				elif(j > 2 and j < 5):
					origin = origin + intWidth + SPACINGS[i]

				startIndex = MET_START[metal+1] - 4

				line = "* W{}\n*\n".format(j)
				fileObject.write(line)
				line = "C {}_bottom.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(wireFileNames[0], MET_CONST[startIndex], origin, parseTotThickness(metal, 0))
				fileObject.write(line)
				line = "C {}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(wireFileNames[0], MET_CONST[startIndex+1], origin, parseTotThickness(metal, 0))
				fileObject.write(line)
				line = "C {}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(wireFileNames[1], MET_CONST[startIndex+2], origin, parseTotThickness(metal, 1))
				fileObject.write(line)
				line = "C {}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(wireFileNames[2], MET_CONST[startIndex+3], origin, parseTotThickness(metal, 2))
				fileObject.write(line)
				line = "C {}_top.txt\t\t{}\t\t{:0.3f} {:0.3f}\n".format(wireFileNames[2], MET_CONST[startIndex+4], origin, parseTotThickness(metal, 2))
				fileObject.write(line)
				line = "*\n*\n*\n"
				fileObject.write(line)

			if(underMet != -1):
				gndThickness, sublayer = parseGndThickness(int(underMet))
				underMetName = make2Dwires.make2Dwires(windowWidth, gndThickness, int(underMet), sublayer, 1)
				totThickness = parseTotThickness(int(underMet), 0)
				previousConst = parseDielectricConstant(int(underMet), -1)
				nextDielectricConst = parseDielectricConstant(int(underMet), 3)

				path = "../M{}/".format(underMet)

				line = "* Under Metal\n*\n"
				fileObject.write(line)
				line = "C {}{}_bottom.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(path, underMetName, previousConst, -1*midWindowWidth, totThickness)
				fileObject.write(line)
				line = "C {}{}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(path, underMetName, "1.0e-6", -1*midWindowWidth, totThickness)
				fileObject.write(line)
				line = "C {}{}_top.txt\t\t{}\t\t{:0.3f} {:0.3f}\n".format(path, underMetName, nextDielectricConst, -1*midWindowWidth, totThickness)
				fileObject.write(line)
				line = "*\n*\n*\n"
				fileObject.write(line)

				if(overMet == -1):
					m0gndName = make2Dwires.make2Dwires(windowWidth, 1.0, 0, 0, 1)
					nextDielectricConst = MET_CONST[0]

					line = "* M0 GND Plane\n*\n"
					fileObject.write(line)
					line = "C ../M0/{}_bottom.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(m0gndName, "1.0e-6", -1*midWindowWidth, -1.0)
					fileObject.write(line)
					line = "C ../M0/{}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(m0gndName, "1.0e-6", -1*midWindowWidth, -1.0)
					fileObject.write(line)
					line = "C ../M0/{}_top.txt\t\t{}\t\t{:0.3f} {:0.3f}\n".format(m0gndName, nextDielectricConst, -1*midWindowWidth, -1.0)
					fileObject.write(line)
					line = "*\n*\n*\n"
					fileObject.write(line)

			if(overMet != -1):
				gndThickness, sublayer = parseGndThickness(int(overMet))
				overMetName = make2Dwires.make2Dwires(windowWidth, gndThickness, int(overMet), sublayer, 1)
				totThickness = parseTotThickness(int(overMet), 0)

				if(int(overMet) == 0 and sublayer == 0):
					nextDielectricConst = MET_CONST[0]
				elif(int(overMet) == 0 and sublayer == 1):
					nextDielectricConst = MET_CONST[1]
				else:
					nextDielectricConst = parseDielectricConstant(int(overMet), 3)

				if(underMet != -1):
					previousConst = "1.0e-6"
				else:
					previousConst = parseDielectricConstant(int(overMet), -1)

				if(overMet == 0 and sublayer == 1):
					path = "../P1/"
				else:
					path = "../M{}/".format(overMet)

				line = "* Over Metal\n*\n"
				fileObject.write(line)
				line = "C {}{}_bottom.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(path, overMetName, previousConst, -1*midWindowWidth, totThickness)
				fileObject.write(line)
				line = "C {}{}_sides.txt\t\t{}\t\t{:0.3f} {:0.3f} +\n".format(path, overMetName, "1.0e-6", -1*midWindowWidth, totThickness)
				fileObject.write(line)
				line = "C {}{}_top.txt\t\t{}\t\t{:0.3f} {:0.3f}\n".format(path, overMetName, nextDielectricConst, -1*midWindowWidth, totThickness)
				fileObject.write(line)
				line = "*\n*\n*\n"
				fileObject.write(line)

			line = "*\n*\n* Process Stack\n* ===========================\n*\n*\n"
			fileObject.write(line)

			## Function to write the rest of the process stack
			writeProcessStack(fileObject, metal, int(underMet), sublayer, int(overMet), int(diagMet), intWindowWidth)

			fileObject.close()
			print("===============================================\n===============================================\n")

	else:

		for i in range(len(DIAG_SPACINGS)):
			parseSpacing = parseUM(str(DIAG_SPACINGS[i]))
			newFileName = "{}_S{}_newTest.lst".format(fileName, parseSpacing)
			fullFileName = "{}M{}/{}".format(INPUTFILE_DIR, strMetal, newFileName)

			try:
				fileObject = open(fullFileName, "x")
			except:
				print("Failed to create {}".format(fullFileName))
				continue

			print("\n===============================================")
			print("Created file: {}".format(fullFileName))

			line = "* Dielectrics\n*=========================\n*\n*\n"
			fileObject.write(line)

			writeDiagonal(fileObject, intWindowWidth, intWidth, DIAG_SPACINGS[i], metal, int(diagMet))

			line = "*\n*\n* Process Stack\n* ===========================\n*\n*\n"
			fileObject.write(line)

			## Function to write the rest of the process stack
			writeProcessStack(fileObject, metal, int(underMet), -1, int(overMet), int(diagMet), intWindowWidth)

			fileObject.close()
			print("===============================================\n===============================================\n")