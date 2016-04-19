from __future__ import print_function
from arqmodel import ARQModel
from protocols import *
from noise import NoiseGenerator

def printProgramParams():
	print("\n\t###################-PARAMETRY PROGRAMU-###################")
	print("\t#--rfp = "+str(rfp)+"\tZakres losowania liczb dla pakietu-------#")
	print("\t#--rfb = "+str(rfb)+"\tZakres losowania liczb dla bitu----------#")
	print("\t#--rfs = "+str(rfs)+"\tZakres losowania liczb dla bitow CRC-----#")
	print("\t#--pfp = "+str(pfp)+"\tDeterminuje P(zaklocenie pakietu)--------#")
	print("\t#--pfb = "+str(pfb)+"\tDeterminuje P(zaklocenie bitu)-----------#")
	print("\t#--pfs = "+str(pfs)+"\tDeterminuje P(zaklocenie bitu CRC)-------#")
	print("\t#--bytes = "+str(bytes)+"\tIlosc bajtow w pakietach-----------------#")
	print("\t##########################################################\n\n")

#--------------------------------PARAMETRY PROGRAMU--------------------------------#
#-------------------------PARAMETRY GENERATORA SZUMOW-------------------------#
rfp = 1000		#if rand(0, rfp) % pfp == 0														#
rfb = 100			#if rand(0, rfb) % pfb == 0														#
rfs = 100			#if rand(0, rfs) % pfs == 0															#
pfp = 200			#~2% na paczke																		#
pfb = 10			#~10% na bit																				#
pfs = 20			#~5% na bity kontrolne																#
#-------------------------------------POZOSTALE-----------------------------------------#																														#
bytes = 64		#ilosc bajtow w paczce																#
errors = 0			#ilosc bledow podczas transmisji													#		
packages = 0		#ilosc przesylanych pakietow														#
percent = 0		#procent bledow																		#
#--------------------------------PARAMETRY PROGRAMU--------------------------------#

print("\n#-----------------------SYMULACJA SAW-----------------------#\n")

printProgramParams()

#inicjalizacja dekoderow ARQ		
sourceARQ = ARQModel()	#zrodlowy ARQ
destARQ = ARQModel()	#docelowy ARQ
noiseGenerator = NoiseGenerator(rfp, rfb, rfs, pfp, pfb, pfs)
sawProtocol = SAWProtocol(sourceARQ, destARQ, noiseGenerator, bytes)

sawProtocol.prepareDecoders('wave.wav')
sawProtocol.transmit()

errors = sawProtocol.errors		#pobranie ilosci bledow
packages = len(sawProtocol.sourceARQ.packages) + 0.0		#pobranie liczby wyslanych pakietow
percent = str( (errors/packages)*100) + '%'		#wyliczenie procentu bledow
errors = str(errors) + '/' + str(len(sawProtocol.sourceARQ.packages))

print("\n<ARQ>\t\tFile sended.\n\t\t\tErrors: ", errors, "\t" + percent)

print("\n\n#----------------------KONIEC SYMULACJI---------------------#\n")

print("\n#-----------------------SYMULACJA GBN-----------------------#\n")

printProgramParams()

#inicjalizacja dekoderow ARQ		
sourceARQ = ARQModel()	#zrodlowy ARQ
destARQ = ARQModel()	#docelowy ARQ
noiseGenerator = NoiseGenerator(rfp, rfb, rfs, pfp, pfb, pfs)
gobackProtocol = GoBackProtocol(sourceARQ, destARQ, noiseGenerator, bytes)

gobackProtocol.prepareDecoders('wave.wav')
gobackProtocol.transmit()

errors = gobackProtocol.errors		#pobranie ilosci bledow
packages = len(gobackProtocol.sourceARQ.packages) + 0.0		#pobranie liczby wyslanych pakietow
percent = str( (errors/packages)*100) + '%'		#wyliczenie procentu bledow
errors = str(errors) + '/' + str(len(gobackProtocol.sourceARQ.packages))

print("\n<ARQ>\t\tFile sended.\n\t\t\tErrors: ", errors, "\t" + percent)

print("\n\n#----------------------KONIEC SYMULACJI---------------------#\n")