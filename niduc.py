from __future__ import print_function
from arqmodel import ARQModel
from protocols import *
from noise import NoiseGenerator


def printProgramParams():
    print("\n\t###################-PARAMETRY PROGRAMU-###################")
    print("\t#--rfp = " + str(rfp) + "\tZakres losowania liczb dla pakietu-------#")
    print("\t#--rfb = " + str(rfb) + "\tZakres losowania liczb dla bitu----------#")
    print("\t#--rfs = " + str(rfs) + "\tZakres losowania liczb dla bitow CRC-----#")
    print("\t#--pfp = " + str(pfp) + "\tDeterminuje P(zaklocenie pakietu)--------#")
    print("\t#--pfb = " + str(pfb) + "\tDeterminuje P(zaklocenie bitu)-----------#")
    print("\t#--pfs = " + str(pfs) + "\tDeterminuje P(zaklocenie bitu CRC)-------#")
    print("\t#--bytes = " + str(bytes) + "\tIlosc bajtow w pakietach-----------------#")
    print("\t#--buffer = " + str(buffSize) + "\tWielkosc buforow w pakietach-------------#")
    print("\t#--chSpd = " + str(int(100/(channelSpeed+1))) + "%\tSzybkosc kanalu--------------------------#")
    print("\t#--window = " + str(windowSize) + "\tSzerokosc okna dla GBN-------------------#")
    print("\t##########################################################\n\n")


# --------------------------------PARAMETRY PROGRAMU--------------------------------#
# -------------------------PARAMETRY GENERATORA SZUMOW-------------------------#
rfp = 1000  # if rand(0, rfp) % pfp == 0														#
rfb = 100  # if rand(0, rfb) % pfb == 0														#
rfs = 100  # if rand(0, rfs) % pfs == 0															#
pfp = 100  # ~10% na paczke																		#
pfb = 10  # ~10% na bit																				#
pfs = 10  # ~10% na bity kontrolne
rgw = 1000  # if rand(0, rgw) % pgw == 0
rgg = 100  # if rand(0, rgg) % pgg == 0
pgw = 10  # ~1% na rozpoczecie serii bledow
pgg = 10  # ~10% na zakonczenie serii bledow
toc = 0  # typ wykorzystywanego kanalu 0 -BSC, 1-Gilberta, 2-BEC
# -------------------------------------POZOSTALE-----------------------------------------#																														#
bytes = 160  # ilosc bajtow w paczce																#
errors = 0  # ilosc bledow podczas transmisji													#
packages = 0  # ilosc przesylanych pakietow														#
percent = 0  # procent bledow
buffSize = 100     # wielkosc bufora
channelSpeed = 0.3  # szybkosc kanalu transmityjnego [0;99]
# 0 = maksymalna predkosc, 1 = 50% predkosci, 2 = 33%, 3 = 25%, 4 = 20%, 5 = ~16%, ..., 99 = 0%
# im wieksza liczba tym wolniejszy kanal

windowSize = 5  # szerokosc okna dla GBN
protocolType = 'SR'    # SAW - Send And Wait, GBN - Go Back N, SR - Selective Repeat
# 																		#
# --------------------------------PARAMETRY PROGRAMU--------------------------------#

print("\n#-----------------------SYMULACJA-----------------------#\n")
print("\t\tPROTOKOL:\t" + protocolType)
printProgramParams()

# inicjalizacja dekoderow ARQ
sourceARQ = ARQModel()  # zrodlowy ARQ
destARQ = ARQModel()  # docelowy ARQ
noiseGenerator = NoiseGenerator(rfp, rfb, rfs, pfp, pfb, pfs, rgw, rgg, pgw, pgg, toc)
if(protocolType == 'SAW'):
    protocol = SAWProtocol(sourceARQ, destARQ, noiseGenerator, bytes)
elif(protocolType == 'GBN'):
    protocol = GoBackProtocol(sourceARQ, destARQ, noiseGenerator, bytes, buffSize, windowSize, channelSpeed)
elif(protocolType == 'SR'):
    protocol = SelectiveRepeatProtocol(sourceARQ, destARQ, noiseGenerator, bytes, buffSize, channelSpeed)


protocol.prepareDecoders('wave.wav')
protocol.transmit()

errors = protocol.errors  # pobranie ilosci bledow
packages = len(protocol.sourceARQ.packages) + 0.0  # pobranie liczby wyslanych pakietow
percent = str((errors / packages) * 100) + '%'  # wyliczenie procentu bledow
errors = str(errors) + '/' + str(len(protocol.sourceARQ.packages))

print("\n<ARQ>\t\tFile sended.\n\t\t\tErrors: ", errors, "\t" + percent)
print("\t\tTotal errors: ", protocol.getTotalErrors())

print("\n\n#--------------------KONIEC SYMULACJI-------------------#\n")
