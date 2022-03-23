import sys
import make3Dwires
import os

INPUTFILE_DIR = "/home/rickysuave/Documents/OSUClasses/VLSILab/FasterCap_main/InputFiles/3D/"

MET_START = [0, 1, 6, 12, 18]
MET_THICKNESS = [0.25, 
				 0.05, 0.35, 0.05, 0.05, 0.15, 
				 0.05, 0.2, 0.02, 0.05, 0.2, 0.05, 
				 0.05, 0.2, 0.02, 0.05, 0.2, 0.05,
				 0.05, 0.2, 0.02]
MET_CONST = ["4.1e-6", 
			 "7.0e-6", "4.3e-6", "4.3e-6", "4.9e-6", "4.1e-6", 
			 "4.9e-6", "2.9e-6", "4.4e-6", "4.9e-6", "2.9e-6", "4.4e-6", 
			 "4.9e-6", "2.9e-6", "4.4e-6", "4.9e-6", "2.9e-6", "4.4e-6",
			 "4.9e-6", "2.9e-6", "4.4e-6"]


SPACINGS = [0.14, 0.21, 0.28, 0.35, 0.42, 0.56, 0.7, 1.0, 1.4]

def parseThickness(metal, sublayer):

	index = MET_START[metal+1] - 3 + sublayer
	sub = MET_START[metal+1] - MET_START[metal] - 2 + sublayer

	return MET_THICKNESS[index], sub

def parseTotThickness(metal, sublayer):

	index = MET_START[metal+1] - 3 + sublayer

	totThickness = 0
	for i in range(index):
		totThickness += MET_THICKNESS[i]

	return totThickness

def parseDielectricConstant(metal, sublayer):

	index = MET_START[metal+1] - 3 + sublayer

	return MET_CONST[index]

def parseGndThickness(metal):

	if(metal == 0):
		sublayer = input("M0 or P1? (Answer 0 or 1, respectively): ")
		if(sublayer == 0):
			return 1.0, sublayer
		elif(sublayer == 1):
			return MET_THICKNESS[0], sublayer
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

if __name__ == "__main__":

	if(len(sys.argv) != 6):
		print("Usage: makeM1oM0.py <window width> <wire width> <wire height> <metal layer> <over/under/overunder flag>")
		print("** NOTE ** : -o, -u, and -ou are the flags for over, under, and overunder respectively")
		exit()

	windowWidth, width, height, strMetal, flag = sys.argv[1:6]

	underMet = -1
	overMet = -1
	pattern = "M{}".format(strMetal)

	metal = int(strMetal)
	if(metal < 0 or metal > 6):
		print("ERROR: Metal layer needs to be an int inbetween 0 and 6")
		exit()

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
	if(underMet == -1 and overMet == -1):
		print("ERROR: Incorrect flag")
		exit()

	parseWindowWidth = parseUM(windowWidth)
	parseWidth = parseUM(width)
	parseHeight = parseUM(height)

	intWindowWidth = float(windowWidth)
	intWidth = float(width)
	intHeight = float(height)

	midWindowWidth = intWindowWidth / 2
	midWidth = intWidth / 2

	command = 'python make3Dwires.py '
	fullcommand = ''
	fileName = "wires_{}_W{}_H{}".format(pattern, parseWidth, parseHeight)

	for i in range(len(SPACINGS)):

		wireFileNames = []

		parseSpacing = parseUM(str(SPACINGS[i]))
		newFileName = "{}_S{}_makeTest.lst".format(fileName, parseSpacing)
		fullFileName = "{}M{}/{}".format(INPUTFILE_DIR, strMetal, newFileName)

		try:
			fileObject = open(fullFileName, "x")
		except:
			print("Failed to create {}".format(fullFileName))
			continue;

		print("\n===============================================")
		print("Created file: {}".format(fullFileName))

		line = "* Dielectrics\n* =========================\n*\n*\n"
		fileObject.write(line)

		for j in range(3):

			dieFileNames = []
			
			print('Creating wire file of width: {}'.format(str(SPACINGS[i])))
			fullcommand = command + str(SPACINGS[i]) + ' '

			thickness, sublayer = parseThickness(metal, j)
			fullcommand = fullcommand + str(thickness) + ' ' + height + ' '

			commandMetal = strMetal + '_' + str(sublayer)
			fullcommand = fullcommand + commandMetal

			print("Would run this command: {}".format(fullcommand))

			wireFileNames.append(make3Dwires.make3Dwires(intWidth, thickness, intHeight, metal, sublayer, 1))
			dieFileNames.append(make3Dwires.make3Dwires(intWidth, thickness, intHeight, metal, sublayer, 0))
			dieFileNames.append(make3Dwires.make3Dwires(SPACINGS[i], thickness, intHeight, metal, sublayer, 0))

			print("midWindow: {}\tintWidth: {}\tSPACINGS[{}]: {}\tmidWidth: {}".format(midWindowWidth, intWidth, i, SPACINGS[i], midWidth))
			left_dielectric = midWindowWidth - (5*intWidth + SPACINGS[i] + midWidth)
			left_dielectric = "%0.2f" % left_dielectric
			dieFileNames.append(make3Dwires.make3Dwires(left_dielectric, thickness, intHeight, metal, sublayer, 0))

			right_dielectric = midWindowWidth - (3*intWidth + SPACINGS[i] + midWidth)
			right_dielectric = "%0.2f" % right_dielectric
			dieFileNames.append(make3Dwires.make3Dwires(right_dielectric, thickness, intHeight, metal, sublayer, 0))

			nextDielectricConst = parseDielectricConstant(metal, j+1)
			currentConst = parseDielectricConstant(metal, j)
			previousConst = parseDielectricConstant(metal, j-1)
			totThickness = parseTotThickness(metal, j)

			#if(j == 0):
			#	nextDielectricConst = M1_4_CONST
			#	currentConst = M1_3_CONST
			#	totThickness = M1_START
			#elif(j == 1):
			#	nextDielectricConst = M1_5_CONST
			#	currentConst = M1_4_CONST
			#	totThickness = totThickness+M1_3_THICKNESS
			#elif(j == 2):
			#	nextDielectricConst = M2_1_CONST
			#	currentConst = M1_5_CONST
			#	totThickness = totThickness+M1_4_THICKNESS

			line = "* M{}_{} Dielectric\n*\n".format(metal, sublayer)
			fileObject.write(line)
			origin = -1*midWidth-SPACINGS[i]
			line = "D {}_top.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[1], nextDielectricConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
			fileObject.write(line)
			for y in range(2):
				origin = origin - 2*intWidth
				line = "D {}_top.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[0], nextDielectricConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
				fileObject.write(line)
			line = "D {}_top.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[2], nextDielectricConst, currentConst, -1*midWindowWidth, totThickness, midWindowWidth, -1*midWindowWidth+0.01, totThickness+0.01, midWindowWidth+0.01)
			fileObject.write(line)

			origin = midWidth
			line = "D {}_top.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[1], nextDielectricConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
			fileObject.write(line)
			origin = origin + SPACINGS[i] + intWidth
			line = "D {}_top.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[0], nextDielectricConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
			fileObject.write(line)
			origin = origin + 2*intWidth
			line = "D {}_top.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[3], nextDielectricConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
			fileObject.write(line)

			if(j == 0):
				origin = -1*midWidth-SPACINGS[i]
				line = "D {}_bottom.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[1], previousConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
				fileObject.write(line)
				for y in range(2):
					origin = origin - 2*intWidth
					line = "D {}_bottom.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[0], previousConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
					fileObject.write(line)
				line = "D {}_bottom.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[2], previousConst, currentConst, -1*midWindowWidth, totThickness, midWindowWidth, -1*midWindowWidth+0.01, totThickness+0.01, midWindowWidth+0.01)
				fileObject.write(line)

				origin = midWidth
				line = "D {}_bottom.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[1], previousConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
				fileObject.write(line)
				origin = origin + SPACINGS[i] + intWidth
				line = "D {}_bottom.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[0], previousConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
				fileObject.write(line)
				origin = origin + 2*intWidth
				line = "D {}_bottom.txt\t\t{} {}\t\t{:0.2f} {:0.2f} {:0.2f}\t\t\t{:0.2f} {:0.2f} {:0.2f} -\n".format(dieFileNames[3], previousConst, currentConst, origin, totThickness, midWindowWidth, origin+0.01, totThickness+0.01, midWindowWidth+0.01)
				fileObject.write(line)

			line = "*\n*\n*\n"
			fileObject.write(line)

		line = "*\n*\n* Metals\n * ===========================\n*\n*\n"
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
			line = "C {}_bottom.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(wireFileNames[0], MET_CONST[startIndex], origin, parseTotThickness(metal, 0), midWindowWidth)
			fileObject.write(line)
			line = "C {}_sides.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(wireFileNames[0], MET_CONST[startIndex+1], origin, parseTotThickness(metal, 0), midWindowWidth)
			fileObject.write(line)
			line = "C {}_sides.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(wireFileNames[1], MET_CONST[startIndex+2], origin, parseTotThickness(metal, 1), midWindowWidth)
			fileObject.write(line)
			line = "C {}_sides.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(wireFileNames[2], MET_CONST[startIndex+3], origin, parseTotThickness(metal, 2), midWindowWidth)
			fileObject.write(line)
			line = "C {}_top.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f}\n".format(wireFileNames[2], MET_CONST[startIndex+4], origin, parseTotThickness(metal, 2), midWindowWidth)
			fileObject.write(line)
			line = "*\n*\n*\n"
			fileObject.write(line)

		if(underMet != -1):
			gndThickness, sublayer = parseGndThickness(int(underMet))
			underMetName = make3Dwires.make3Dwires(windowWidth, gndThickness, windowWidth, int(underMet), sublayer, 1)
			totThickness = parseTotThickness(int(underMet), 0)
			previousConst = parseDielectricConstant(int(underMet), -1)
			nextDielectricConst = parseDielectricConstant(int(underMet), 3)

			line = "* Under Metal\n*\n"
			fileObject.write(line)
			line = "C {}_bottom.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(underMetName, previousConst, -1*midWindowWidth, totThickness, -1*midWindowWidth)
			fileObject.write(line)
			line = "C {}_sides.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(underMetName, "1.0e-6", -1*midWindowWidth, totThickness, -1*midWindowWidth)
			fileObject.write(line)
			line = "C {}_top.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f}\n".format(underMetName, nextDielectricConst, -1*midWindowWidth, totThickness, -1*midWindowWidth)
			fileObject.write(line)
			line = "*\n*\n*\n"
			fileObject.write(line)

			if(overMet == -1):
				m0gndName = make3Dwires.make3Dwires(windowWidth, 1.0, windowWidth, 0, 0, 1)
				nextDielectricConst = MET_CONST[0]

				line = "* M0 GND Plane\n*\n"
				fileObject.write(line)
				line = "C {}_bottom.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(m0gndName, "1.0e-6", -1*midWindowWidth, -1.0, -1*midWindowWidth)
				fileObject.write(line)
				line = "C {}_sides.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(m0gndName, "1.0e-6", -1*midWindowWidth, -1.0, -1*midWindowWidth)
				fileObject.write(line)
				line = "C {}_top.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f}\n".format(m0gndName, nextDielectricConst, -1*midWindowWidth, -1.0, -1*midWindowWidth)
				fileObject.write(line)
				line = "*\n*\n*\n"
				fileObject.write(line)

		if(overMet != -1):
			gndThickness, sublayer = parseGndThickness(int(overMet))
			overMetName = make3Dwires.make3Dwires(windowWidth, gndThickness, windowWidth, int(overMet), sublayer, 1)
			totThickness = parseTotThickness(int(overMet), 0)
			previousConst = parseDielectricConstant(int(overMet), -1)
			nextDielectricConst = parseDielectricConstant(int(overMet), 3)

			line = "* Over Metal\n*\n"
			fileObject.write(line)
			line = "C {}_bottom.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(overMetName, previousConst, -1*midWindowWidth, totThickness, -1*midWindowWidth)
			fileObject.write(line)
			line = "C {}_sides.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f} +\n".format(overMetName, "1.0e-6", -1*midWindowWidth, totThickness, -1*midWindowWidth)
			fileObject.write(line)
			line = "C {}_top.txt\t\t{}\t\t{:0.2f} {:0.2f} {:0.2f}\n".format(overMetName, nextDielectricConst, -1*midWindowWidth, totThickness, -1*midWindowWidth)
			fileObject.write(line)
			line = "*\n*\n*\n"
			fileObject.write(line)


		fileObject.close()
		print("===============================================\n===============================================\n")