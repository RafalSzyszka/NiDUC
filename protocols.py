from __future__ import print_function
from arqmodel import ARQModel
from noise import NoiseGenerator
import threading
import Queue
import time


# PROTOKOL: SEND AND WAIT!
# Symulacja transmisji za pomoca protokolu SAW
# Mozliwosc konfiguracji parametrow transmisji
#
# -----Parametry:
#			bytes	-	ilosc bajtow na pakiet
#			

class SAWProtocol:
    # potrzebne obiekty do wykonania symulacji!
    sourceARQ = ARQModel()  # zrodlowy dekoder ARQ
    destARQ = ARQModel()  # docelowy dekoder ARQ
    noiseGenerator = None  # generator szumu
    bytes = 0  # ilosc bajtow na pakiet
    errors = 0  # wykryte bledy w transmisji

    def __init__(self, sARQ, dARQ, noiseGen,
                 n):  # konstruktor (siebie, sourceARQ, destARQ, generator szumu ,ilosc bajtow na pakiet):
        self.sourceARQ = sARQ
        self.destARQ = dARQ
        self.noiseGenerator = noiseGen
        self.bytes = n
        self.errors = 0

    def prepareDecoders(self, file):
        print("<ARQ>\t\tPreparing decoders:\n\n\t\t\tSynchronizing...")
        self.synchronize()

        print("\n\t\t\tLoading file...")
        self.loadFile(file)

        print("\n\t\t\tPreparing source ARQ module...")
        self.prepareSourceARQ()

    def synchronize(self):  # synchronizuje moduly arq
        self.destARQ.bytesinpack = bytes
        self.sourceARQ.bytesinpack = bytes

    def loadFile(self, file):  # wczytanie pliku do zrodlowego modulu arq
        self.sourceARQ.loadfile(file)

    def prepareSourceARQ(self):  # przygotowanie zrodlowego modulu arq do transmisji
        print("\n\t\t\t\tCreating packages...")
        self.sourceARQ.packsofn(self.bytes)  # dzielenie pliku na paczki

        print("\n\t\t\t\tAdding secure bytes...")
        self.sourceARQ.addevenbyte()  # dodanie bitow kontrolnych

    def transmit(self):
        print("\n<sourceARQ>\t\tStarting transmition:\n\n\t\t\t\tSending packages...")
        for pack in self.sourceARQ.packages:  # wyciaganie pojedynczych pakietow z pamieci modulu arq
            ack = self.destARQ.receivepacks(self.noiseGenerator.addNoise(pack))  # proba odebrania pakietu
            while (ack == 'nack'):
                ack = self.destARQ.receivepacks(self.noiseGenerator.addNoise(pack))
                self.errors += 1

        print("\n<destARQ>\t\tFinishing transmition:")
        self.afterTransmition()  # zakonczenie transmisji

    def afterTransmition(self):
        print("\n\t\t\t\tUnpacking...")
        self.destARQ.unpack()  # rozpakowanie odebranych pakietow
        print("\n\t\t\t\tExporting to .wav...")
        self.destARQ.converttowave('receivedViaSAWProtocol.wav')

    def getTotalErrors(self):
        return self.noiseGenerator.totalErrors

class GoBackProtocol:
    # potrzebne obiekty do wykonania symulacji!
    sourceARQ = None  # zrodlowy dekoder ARQ
    destARQ = None  # docelowy dekoder ARQ
    bufor = None  # bufor
    noiseGenerator = None  # generator szumu
    bytes = 0  # ilosc bajtow na pakiet
    errors = 0  # wykryte bledy w transmisji

    def __init__(self, sARQ, dARQ, nGen, n):  # inicjalizacja protokolu
        self.bufor = Bufor()
        self.sourceARQ = sARQ
        self.destARQ = dARQ
        self.noiseGenerator = nGen
        self.bytes = n
        self.errors = 0

    def prepareDecoders(self, file):
        print("<ARQ>\t\tPreparing decoders:\n\n\t\t\tSynchronizing...")
        self.synchronize()

        print("\n\t\t\tLoading file...")
        self.loadFile(file)

        print("\n\t\t\tPreparing source ARQ module...")
        self.prepareSourceARQ()

    def transmit(self):
        print("\n<sourceARQ>\t\tStarting transmition:\n\n\t\t\t\tSending packages...")

        allPacks = len(self.sourceARQ.packages)  # ilosc wszystkich paczek
        lastSended = 0  # numer ostatniej dobrze odebranej paczki
        lastReceived = 0  # ostatnia dobrze odebrana paczka
        totalReceivedPacks = 0  # calkowita ilosc odebranych paczek
        failed = 0  # flaga bledu przy probie odebrania

        # Symuluje zachowanie protokolu go back n
        while (lastSended < allPacks):
            tmp = 5
            sended = 0
            while (sended < tmp):  # wczytaj 5 paczek do bufora
                if (lastSended + sended < allPacks):
                    self.bufor.givePack(self.noiseGenerator.addNoise(
                        self.sourceARQ.packages[lastSended + sended]))  # zaklocenie paczki i dodanie jej do bufora
                sended += 1  # zwiekszenie licznika

            received = 1
            while (received < 5):  # odbierz 4 paczki // generowanie opoznienia
                ack = self.destARQ.receivepacks(self.bufor.getPack())  # proba odebrania paczki
                if (ack == 'nack'):
                    lastSended = lastReceived  # ostatnia dobrze odebrana paczka to paczka poprzednia
                    failed = 1
                    self.bufor.clear()
                    self.errors += 1
                    break
                else:
                    lastReceived += 1  # zapamietanie ostaniej dobrze odebranej paczki
                    received += 1
                    totalReceivedPacks += 1
                    failed = 0

            if (failed != 1):
                lastSended += 5

        self.afterTransmition()

    def afterTransmition(self):
        print("\n\t\t\t\tUnpacking...")
        self.destARQ.unpack()  # rozpakowanie odebranych pakietow
        print("\n\t\t\t\tExporting to .wav...")
        self.destARQ.converttowave('receivedViaGoBackProtocol.wav')

    def synchronize(self):  # synchronizuje moduly arq
        self.destARQ.bytesinpack = bytes
        self.sourceARQ.bytesinpack = bytes

    def loadFile(self, file):  # wczytanie pliku do zrodlowego modulu arq
        self.sourceARQ.loadfile(file)

    def prepareSourceARQ(self):  # przygotowanie zrodlowego modulu arq do transmisji
        print("\n\t\t\t\tCreating packages...")
        self.sourceARQ.packsofn(self.bytes)  # dzielenie pliku na paczki

        print("\n\t\t\t\tAdding secure bytes...")
        self.sourceARQ.addevenbyte()  # dodanie bitow kontrolnych

    def getTotalErrors(self):
        return self.noiseGenerator.totalErrors

class SelectiveRepeatProtocol:
    # potrzebne obiekty do wykonania symulacji!
    sourceARQ = None  # zrodlowy dekoder ARQ
    destARQ = None  # docelowy dekoder ARQ
    bufor = None  # bufor
    noiseGenerator = None  # generator szumu
    bytes = 0  # ilosc bajtow na pakiet
    errors = 0  # wykryte bledy w transmisji

    def __init__(self, sARQ, dARQ, nGen, n):
        self.bufor = []
        self.sourceARQ = sARQ
        self.destARQ = dARQ
        self.noiseGenerator = nGen
        self.bytes = n
        self.errors = 0

    def prepareDecoders(self, file):
        print("<ARQ>\t\tPreparing decoders:\n\n\t\t\tSynchronizing...")
        self.synchronize()

        print("\n\t\t\tLoading file...")
        self.loadFile(file)

        print("\n\t\t\tPreparing source ARQ module...")
        self.prepareSourceARQ()

        print("\n\t\t\tPreparing destination ARQ module...")
        self.prepareDestARQ()

    def transmit(self):
        print("\n<sourceARQ>\t\tStarting transmition:\n\n\t\t\t\tSending packages...")

        bufor = []  # bufor dla wysylanych paczek
        indexes = []    # miejsca tych paczek

        sended = 0
        while(sended < len(self.sourceARQ.packages)):   #wyslij wszystkie paczki do bufora
            bufor.append(self.noiseGenerator.addNoise(self.sourceARQ.packages[sended]))
            indexes.append(sended)
            sended += 1

        # w tym miejscu wszystkie paczki znajduja sie w buforze, a ich indeksy w indexes
        # odwracamy listy i wyciagamy z nich paczki
        while(len(bufor) > 0):
            bufor.reverse()
            indexes.reverse()

            erIndexes = []
            while(len(bufor) > 0):  #odbieranie paczek
                pack = bufor.pop()
                index = indexes.pop()
                if(self.destARQ.checkPack(pack) == 'ack'):
                    self.destARQ.packages[index] = pack
                else:
                    erIndexes.append(index)
                    self.errors += 1

            bufor = []
            indexes = []
            while(len(erIndexes) > 0):  # ponowne wyslanie paczek ktore okazaly sie bledne
                index = erIndexes.pop()
                bufor.append(self.noiseGenerator.addNoise(self.sourceARQ.packages[index]))
                indexes.append(index)

        self.afterTransmition()

    def afterTransmition(self):
        print("\n\t\t\t\tUnpacking...")
        self.destARQ.unpack()  # rozpakowanie odebranych pakietow
        print("\n\t\t\t\tExporting to .wav...")
        self.destARQ.converttowave('receivedViaSelectiveProtocol.wav')

    def synchronize(self):  # synchronizuje moduly arq
        self.destARQ.bytesinpack = bytes
        self.sourceARQ.bytesinpack = bytes

    def loadFile(self, file):  # wczytanie pliku do zrodlowego modulu arq
        self.sourceARQ.loadfile(file)

    def prepareSourceARQ(self):  # przygotowanie zrodlowego modulu arq do transmisji
        print("\n\t\t\t\tCreating packages...")
        self.sourceARQ.packsofn(self.bytes)  # dzielenie pliku na paczki

        print("\n\t\t\t\tAdding secure bytes...")
        self.sourceARQ.addevenbyte()  # dodanie bitow kontrolnych

    def prepareDestARQ(self):  # przygotowuje docelowego ARQ do odebrania transmisji
        for i in range(0, len(self.sourceARQ.packages)):
            self.destARQ.packages.append(0)

    def getTotalErrors(self):
        return self.noiseGenerator.totalErrors

class Bufor:
    bufor = None  # kolejka

    def __init__(self):
        self.bufor = Queue.Queue()

    def givePack(self, pack):  # dodanie do kolejki
        self.bufor.put(pack)

    def getPack(self):  # pobranie z kolejki
        return self.bufor.get()

    def clear(self):
        self.bufor = Queue.Queue()
