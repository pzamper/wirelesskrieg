#! /usr/bin/python
# Written by Paulo Zamperlini - May 2019
 
import os
from gps import *
from time import *
import time
import threading
import math
import subprocess
import numpy
 
#DECLARACAO
Coordenadas = numpy.zeros((27, 4))
linha = 0
Raio = 6371000 #raio da terra
gateway = "172.19.82.254"
server = "172.19.82.253"
testesfeitos = 0

#LEITURA DA MATRIZ DE COORDENADAS

with open ('coordenadas.txt') as f:
	for line in f:
		data = line.split()
		Coordenadas[linha][0] = float(data[0])
		Coordenadas[linha][1] = float(data[1])
		Coordenadas[linha][2] = float(data[2])
		Coordenadas[linha][3] = float(data[3])

		linha = linha+1

f.close()

#INICIALIZACAO DO GPS
gpsd = None
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd
    gpsd = gps(mode=WATCH_ENABLE)
    self.current_value = None
    self.running = True
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next()
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start()


#LOOP PRINCIPAL DO GPS
  
    while (testesfeitos <= linha):
 
      os.system('clear')

      print ' GPS reading'
      print '----------------------------------------'
      print 'latitude    ' , gpsd.fix.latitude
      print 'longitude   ' , gpsd.fix.longitude
      print 'time utc    ' , gpsd.utc
      print 'altitude (m)' , gpsd.fix.altitude
      #print 'eps         ' , gpsd.fix.eps
      #print 'epx         ' , gpsd.fix.epx
      #print 'epv         ' , gpsd.fix.epv
      #print 'ept         ' , gpsd.fix.ept
      print 'speed (m/s) ' , gpsd.fix.speed
      #print 'climb       ' , gpsd.fix.climb
      #print 'track       ' , gpsd.fix.track
      #print 'mode        ' , gpsd.fix.mode
      #print
      #print 'sats        ' , gpsd.satellites
      print '----------------------------------------'
 
      latatual = gpsd.fix.latitude
      lonatual = gpsd.fix.longitude	    

      for x in range(0, 27):

         lat2 = Coordenadas[x][1]
         lon2 = Coordenadas[x][2]

         lat1rad = latatual*(math.pi/180)
         lat2rad = lat2*(math.pi/180)

         deltalatrad = (lat2-latatual)*(math.pi/180)
         deltalonrad = (lon2-lonatual)*(math.pi/180)

         a = (math.sin(deltalatrad/2)*math.sin(deltalatrad/2)) + (math.cos(lat1rad)*math.cos(lat2rad)*math.sin(deltalonrad/2)*math.sin(deltalonrad/2))
         c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a));
         d = Raio*c
    
         print ("d" + str(x) + " = " + str(d))

         if ( (d <= 10) and (Coordenadas[x][3]==0) ):
           
           print '----------------------------------------'
           print("Testando Ponto #" + str(x))

           #Aqui lancamos todos os testes

	   #TESTE DE LATENCIA
           p1 = subprocess.Popen(['ping', '-i 0.5', '-c 10', gateway], stdout=subprocess.PIPE)

           output1 = p1.communicate()[0]

	   arquivo1 = "ping" + str(int(Coordenadas[x][0])) + ".txt"	
           f1= open(arquivo1,"w+")
           f1.write(output1)
           f1.close()

	   #ESCANEAMENTO DE REDES AO ALCANCE
           p2 = subprocess.Popen(['sudo', 'iwlist', 'wlan1', 'scan'], stdout=subprocess.PIPE)

           output2 = p2.communicate()[0]

           arquivo2 = "scan" + str(int(Coordenadas[x][0])) + ".txt"
           f2= open(arquivo2,"w+")
           f2.write(output2)
           f2.close()
         
	   #TESTE DE THROUGHPUT (UPLOAD + DOWNLOAD)
		
           p3 = subprocess.Popen(['iperf', '-c', server], stdout=subprocess.PIPE)

           output3 = p3.communicate()[0]

           p4 = subprocess.Popen(['iperf', '-c', server, '-R'], stdout=subprocess.PIPE)

           output4 = p4.communicate()[0]

           arquivo3 = "iperf" + str(int(Coordenadas[x][0])) + ".txt"

           f3= open(arquivo3,"w+")
           f3.write(output3)
           f3.write(output4)
           f3.close()
		
	   #TESTE DE JITTER

	   p5 = subprocess.Popen(['iperf', '-c', server, '-u'], stdout=subprocess.PIPE)
           output5 = p5.communicate()[0]
           arquivo5 = "jitter" + str(int(Coordenadas[x][0])) + ".txt"
           f5= open(arquivo5,"w+")
           f5.write(output5)
           f5.close()

	   #EXPORTAR INFORMACOES DO GPS	

	   arquivo4 = "gps" + str(int(Coordenadas[x][0])) + ".txt"
           f4= open(arquivo4,"w+")

	   f4.write(' GPS reading')
	   f4.write('\n')
           f4.write('----------------------------------------')
           f4.write('\n')
           f4.write(str(gpsd.fix.latitude))
           f4.write('\n')
           f4.write(str(gpsd.fix.longitude))
           f4.write('\n')         
           f4.write(str(gpsd.utc))
           f4.write('\n')
           f4.write(str(gpsd.fix.altitude))
           f4.write('\n')
           f4.write(str(gpsd.fix.speed))	 

	   f4.close()
	 

           #MARCAR A FINALIZACAO DE LEITURA DO PONTO
           Coordenadas[x][3] = 1
	   testesfeitos = testesfeitos+1

	   #EXPORTAR OS RESULTADOS PARCIAIS
         
           with open ("resultados.txt","w") as f:

            for y in range(0, 27):
	      f.write(str(int(Coordenadas[y][0])))
	      f.write(" ")
	      f.write(str(Coordenadas[y][1]))
	      f.write(" ")
              f.write(str(Coordenadas[y][2]))
	      f.write(" ")
	      f.write(str(int(Coordenadas[y][3])))
	      f.write("\n")

            f.close()

      print '----------------------------------------'
      print("Pontos Capturados: " + str(testesfeitos) + " de " + str(linha))	
        

  except (KeyboardInterrupt, SystemExit): 
    print "\nKilling Thread..."
    gpsp.running = False
    gpsp.join()
  print "Done.\nExiting."