#NOISE GENERATOR
#Pobiera pakiet i z okreslonym modyfikowalnym prawdopodobienstwem dodaje do niego szum
#-----Parametry:
#	rangeForPack
#	rangeForBit
#	rangeForSecure
#	probForPack
#	probForBit
#	probForSecure

import random

class NoiseGenerator:
	
	#Parametry determinujace prawdopodobienstwo wystapienia przeklamania
	rangeForPack = 0
	rangeForBit = 0
	rangeForSecure = 0
	probForPack = 0
	probForBit = 0
	probForSecure = 0
	
	def __init__(self, rfp, rfb, rfs, pfp, pfb, pfs):
		self.rangeForPack = rfp
		self.rangeForBit = rfb
		self.rangeForSecure = rfs
		self.probForPack = pfp
		self.probForBit = pfb
		self.probForSecure = pfs
	
	def addNoise(self, pack):		#prymitywne zaszumienie pakietu
		grain = random.randint(0, self.rangeForPack)		#wylosowanie liczby z przedzialu [0;rangeForPack)
		
		#istnieje prawdopodobienstwo, ze pakiet zostanie zaklocony
		#jest ono determinowane przez parametr 'probForPack'
		if(grain % self.probForPack == 0):
		
			damagedPack = [byte for byte in pack]	#przekopiowanie pakietu
		
			ones = damagedPack.pop()		#pozbywamy sie bitow kontrolnych
			even = damagedPack.pop()		
			
			#konwersja przeklamanego ciagu bitow na pakiet mozliwy do transmisji
			damagedPack = self.convertBitStringToPack(self.changeBits(damagedPack))
			
			#przeklamanie bitow kontrolnych i zworcenie zakloconego pakietu
			return self.changeSecureBits(damagedPack, even, ones)
			
		#istnieje duze prawdopodobienstwo ze pakiet nie zostanie zaklocony
		else:
			return pack
			
	def convertBitStringToPack(self, string):		#konwertuje napis na pakiet
		pack = []			#miejsce na pakiet
		tmp = ''				#miejsce na pojedyncze bajty
		for i in range(0, len(string)):		#proces wydzielania bajtow
			if(i % 8 == 0 and i != 0):
				pack.append(tmp)
				tmp = ''
			tmp += string[i]
			
			if(i == len(string)-1):
				pack.append(tmp)
		
		return pack
		
	def changeBits(self, damagedPack):
		string = ''		#przygotowanie miejsca na zaklocony pakiet
		
		for byte in damagedPack:		#wybieramy poszczegolne bajty z paczki
			for bit in byte:					#wybieramy poszczegolne bity z kazdego bajtu
				#istnieje prawdopodobienstwo, ze bit zostanie zmieniony
				#dereminuja to parametry 'probForBit' oraz 'rangeForBit'
				if(random.randint(0, self.rangeForBit) % self.probForBit == 0):
					if(bit == '0'):
						string += '1'		#zamiana 0->1
					else:
						string += '0'		#zamiana 1->0
				else:
					string += bit			#bez zmian
		
		return string	
		
	def changeSecureBits(self, damagedPack, even, ones):
		#istnieje prawdopodobienstwo, ze bity kontrolne zostana zmienione
		#dereminuja to parametry 'probForSecure' oraz 'rangeForSecure'
		if(random.randint(0, self.rangeForSecure) % self.probForSecure == 0):
			even = random.randint(0,1)
			ones = random.randint(0, 65536)
				
		damagedPack.append(even)
		damagedPack.append(ones)
		return damagedPack		#zwrocenie zakloconego pakietu