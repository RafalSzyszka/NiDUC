from __future__ import print_function
from arqmodel import ARQModel
from noise import NoiseGenerator
import threading
import Queue
import time


# PROTOKOL: SEND AND WAIT!
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
    bufferSize = 0 # wielkosc buforow
    channelSpeed = 0    # szybkosc kanalu
    windowSize = 0  # szerokosc okna

    def __init__(self, sARQ, dARQ, nGen, n, bufSize, wSize, chSpd):  # inicjalizacja protokolu
        self.bufor = Bufor()
        self.sourceARQ = sARQ
        self.destARQ = dARQ
        self.noiseGenerator = nGen
        self.bytes = n
        self.errors = 0
        self.bufferSize = bufSize
        self.channelSpeed = chSpd
        self.windowSize = wSize

    def prepareDecoders(self, file):
        print("<ARQ>\t\tPreparing decoders:\n\n\t\t\tSynchronizing...")
        self.synchronize()

        print("\n\t\t\tLoading file...")
        self.loadFile(file)

        print("\n\t\t\tPreparing source ARQ module...")
        self.prepareSourceARQ()

    def transmit(self):
        print("\n<sourceARQ>\t\tStarting transmition:\n\n\t\t\t\tSending packages...")
        sBuf = []   # przechowuje paczki wyslane przez sourceARQ
        allPacks = len(self.sourceARQ.packages) # liczba paczek do wyslania
        lastReceived = -1   # ostatnia dobrze odebrana paczka
        lastSended = 0      # ostatnia wyslana paczka

        send = 0
        while(lastSended < allPacks):   # zapelnia bufor wielkoscia okna
            for i in range(0, self.windowSize):
                if(send < self.bufferSize and lastSended < allPacks):     # zapelnianie bufora
                    sBuf.append(self.noiseGenerator.addNoise(self.sourceARQ.packages[lastSended]))
                    send += 1
                    lastSended += 1

            for i in range(0, int(self.bufferSize/self.channelSpeed)):  # odbieranie okreslonej ilosci paczek
                if(send > 0 and send < self.bufferSize):       # proba odebrania paczki jesl bufor nie zostal zapelniony
                    ack = self.destARQ.receivepacks(sBuf[0])
                    sBuf = sBuf[1:]
                    send -= 1
                    if(ack == 'ack'):    # pomyslnie odebrano paczke
                        lastReceived += 1
                    else:
                        lastSended = lastReceived + 1   # powrot do miejsca bledu
                        sBuf = []   # wyczyszczenie bufora
                        send = 0
                        self.errors += 1

            if(send == self.bufferSize):    # proba odebrania wszystkiego w buforze jesli ten jest pelny
                for i in range(0, self.bufferSize):
                    ack = self.destARQ.receivepacks(sBuf[0])    # proba odebrania pakietu
                    sBuf = sBuf[1:]     # zmniejszenie bufora
                    send -= 1
                    if (ack == 'ack'):  # pomyslnie odebrano paczke
                        lastReceived += 1
                    else:
                        lastSended = lastReceived + 1  # powrot do miejsca bledu
                        sBuf = []  # wyczyszczenie bufora
                        send = 0
                        self.errors += 1
                        break   # przerwanie transmisji

            if(lastSended >= allPacks and len(sBuf) > 0):     # wyslano juz wszystkie paczki do bufora
                                                    # ale jeszcze wszystkich nie odebrano
                for i in range(0, len(sBuf)):
                    ack = self.destARQ.receivepacks(sBuf[0])  # proba odebrania pakietu
                    sBuf = sBuf[1:]  # zmniejszenie bufora
                    send -= 1
                    if (ack == 'ack'):  # pomyslnie odebrano paczke
                        lastReceived += 1
                    else:
                        lastSended = lastReceived + 1  # powrot do miejsca bledu
                        sBuf = []  # wyczyszczenie bufora
                        send = 0
                        self.errors += 1
                        break  # przerwanie transmisji

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
    bufferSize = 0  # wielkosc buforow
    channelSpeed = 0    # predkosc kanalu im mniejsza tym lepsza

    def __init__(self, sARQ, dARQ, nGen, n, buffSize, chs):
        self.bufor = []
        self.sourceARQ = sARQ
        self.destARQ = dARQ
        self.noiseGenerator = nGen
        self.bytes = n
        self.errors = 0
        self.bufferSize = buffSize
        self.channelSpeed = chs + 1

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
        erBufor = []   # drugi bufor na zle odebrane paczki
        erIndexes = []  # indeksy blednych paczek
        indexes = []    # indeksy wyslanych paczek
        sended = 0
        allPacks = len(self.sourceARQ.packages)

        while(sended < allPacks):   # dopoki nie wysle wszystkich paczek
            while(len(bufor) < self.bufferSize-len(erBufor) and sended < allPacks):  # wyslij okreslona ilosc paczek do bufora
                bufor.append(self.noiseGenerator.addNoise(self.sourceARQ.packages[sended]))
                indexes.append(sended)
                sended += 1

            # okreslona ilosc paczek mamy w buforze, teraz nalezy odebrac pewna ich ilosc
            # ilosc jest proporcjonalna do szybkosci kanalu
            rBufor = bufor[:int(self.bufferSize/self.channelSpeed)]
            rIndexes = indexes[:int(self.bufferSize/self.channelSpeed)]

            bufor = bufor[int(self.bufferSize/self.channelSpeed):]   # zachowanie reszty bufora
            indexes = indexes[int(self.bufferSize/self.channelSpeed):]

            # proba odebrania okreslonej ilosci paczek
            errs = []
            while(len(rBufor) > 0):
                pack = rBufor.pop()
                index = rIndexes.pop()
                if(self.destARQ.checkPack(pack) == 'ack'):
                    self.destARQ.packages[index] = pack     # zapisanie paczki
                else:
                    errs.append(index)     # zadanie przyslania paczki jeszcze raz
                    self.errors += 1
                while(len(erBufor) > 0):    # jesli w buforze bledow sa paczki odbierz je
                    pack = erBufor.pop()
                    index = erIndexes.pop()
                    if (self.destARQ.checkPack(pack) == 'ack'):
                        self.destARQ.packages[index] = pack  # zapisanie paczki
                    else:
                        errs.append(index)  # zadanie przyslania paczki jeszcze raz
                        self.errors += 1

            while(len(errs) > 0):  # odeslanie jeszcze raz paczek blednie odebranych
                index = errs.pop()
                erBufor.append(self.noiseGenerator.addNoise(self.sourceARQ.packages[index]))
                erIndexes.append(index)

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
