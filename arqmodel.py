
#Klasa ARQModel ma na celu wczytanie pliku wejsciowego .wav
#nastepnie wczytanie kolejnych jego bajtow i przedstawienie ich w formie 0 i 1 
#zamiast '\xXX' np.: '\xaa' = '10101010'
#model dzieli na paczki po n=1,2,4,8,16,32,64,128 bajtów 
#(najczytelniej jest n=8, n=32 powinno byc optymalne do testow)
#model dodaje rowniez bit parzystosci jako n+1 element paczki 
#i bajt ktory zawiera informacje o ilosci jedynek w pakiecie
#bajt ilosci jedynek jest w paczce jako n+2 element
#przykladowa paczka dla n=8: 
#['10110101', '10111111', '00000000', '10010001', '10100101', '10010100', '11111111', '10110001', 1, 34]
#indeksy 	[0:n-1] 	to miejsce danych
#indeks 	n 			to bit parzystosci
#indeks 	n + 1 		to ilosc jedynek w pakiecie danych
#rozmiar paczki to n+2
#
#rozmiar pliku wave.wav z gita to dokladnie 6 000 000(+- 1) bajtow! 
#wiec mozna dzielic na paczki po 1,2,4,8,16,32,64,128 bajtow (choc 128 jest ryzykowne)



from __future__ import print_function
import wave
import array

class ARQModel:
	
	bin_file = []	#bajty pliku .wav
	rate = 32000	#rating pliku .wav
	packages = []	#bin_file podzielony na paczki
	bytesinpack = 0	#po ile bajtow dany byly pakowane
	
	def __init__(self, filepath):		#konstruktor modulu arq, wczytuje plik i konwertuje go na ciag bajtow!
		print("Reading file...")
		tmpw = wave.open(filepath, "rb")	
		bytes = tmpw.readframes(tmpw.getnframes())
		tmpw.close()
		print("Converting to bytes...")
		self.bin_file = [ord(char) for char in bytes]
		self.bin_file = [bin(char)[2:].zfill(8) for char in self.bin_file]	#wynikowa lista bajtow w reprezentacji zer i jedynek
		
	def printnbytes(self, begin, end):	#wypisuje bajty z podanego zakresu
		for i in range(begin, end):
			print(self.bin_file[i], end= " ")
			
	def converttowave(self, output):	#tworzy plik wav z ciagu bajtow
		print("Converting to wav...")
		self.bin_file = [int(bit, 2) for bit in self.bin_file]	#do integerow
		self.bin_file = array.array('B', self.bin_file).tostring() #do bajtow w postaci '\xdd'
		self.output_wave(output, self.bin_file)
	
	def output_wave(self, path, frames):
		output = wave.open(path,'w')	#tylko do zapisu
		output.setparams((2,2,self.rate,0,'NONE','not compressed'))		#2 kanaly, szerokosc? probki, rating, kompresja
		print("Saving file...")
		output.writeframes(frames)
		output.close()
		
	def packsofn(self, bytesinpack):	#dzielenie zaladowanego pliku na paczki po zadanej ilosci bajtow
		begin = 0
		end = bytesinpack
		self.bytesinpack = bytesinpack
		for i in range(0, (len(self.bin_file)/bytesinpack)):
			pack = self.bin_file[begin:end]
			self.packages.append(pack)
			begin += bytesinpack
			end += bytesinpack
	
	def addevenbyte(self):	#dodawanie bitu parzystosci i ilosci jedynek do kazdej paczki
		onesinpackage = 0	#dodanie 1 jesli ilosc jedynek w paczce jest parzysta, 0 wpp
		for pack in self.packages:
			for byte in pack:
				for char in byte:
					if(char == '1'):
						onesinpackage += 1
			if(onesinpackage % 2 == 0):
				pack.append(1)
				pack.append(onesinpackage)
			else:
				pack.append(0)
				pack.append(onesinpackage)
			onesinpackage = 0
			
			
arq = ARQModel("wave.wav")
arq.packsofn(8)
arq.addevenbyte()
print(arq.packages[512:612])