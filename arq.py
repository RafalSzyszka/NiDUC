from __future__ import print_function
import wave
import array

rate = 32000 #rate pliku ktory testowalem

def output_wave(path, frames):
    output = wave.open(path,'w')	#tylko do zapisu
    output.setparams((2,2,rate,0,'NONE','not compressed')) #2 kanaly, szerokosc? probki, rating, kompresja
    output.writeframes(frames)
    output.close()

w = wave.open("wave.wav", "rb") #tylko do odczytu
print("Loading file...")
binary = w.readframes(w.getnframes())	#pobranie bitow w formie szesnastkowej
print("Reading file...")
w.close()
print("Closing file...")

#konwertuje hex do int i potem do binarnego
print("Converting to binary... (it may take a while)")
binary = [ord(character) for character in binary] #do calkowitych
binary = [bin(character) for character in binary]	#do binarnych

#############to wyzej to bedzie skrypt w jednym pliku a to nizej powinno byc w innym###############

#w tym momencie mozna podzielic na paczki dodac bit parzystkosci i cos tam pokombinowac dalej

#po skonczeniu wszystkiego mozna wyeksportowac znowu do wav'a
print("Converting to bytes...")
binary = [int(element ,2) for element in binary] #wrocic do calkowitych trzeba
binary = array.array('B',binary).tostring()	#bo tutaj drugi argument musi zawierac integery bo w output_wave argument frames musi byc stringiem!

#jak ktos wpadnie na cos bardziej optymalnego to smialo zmiencie tutaj! : )
print("Exporting to wav...")
output_wave("ex.wav", binary)