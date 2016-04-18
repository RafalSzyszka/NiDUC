from __future__ import print_function
from arqmodel import ARQModel
from sawProtocol import SAWProtocol
from noise import NoiseGenerator

rfp = 1000		#if rand(0, rfp) % pfp == 0
rfb = 100			#if rand(0, rfb) % pfb == 0
rfs = 100			#if rand(0, rfs) % pfs == 0
pfp = 200			#~2% na paczke
pfb = 33			#~3% na bit
pfs = 33			#~3% na bity kontrolne

bytes = 150		#ilosc bajtow w paczce
errors = 0			#ilosc bledow podczas transmisji
packages = 0		#ilosc przesylanych pakietow
percent = 0		#procent bledow


print("\n#-----------------------SYMULACJA-----------------------#\n")
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

print("\n\n#--------------------KONIEC SYMULACJI-------------------#\n")