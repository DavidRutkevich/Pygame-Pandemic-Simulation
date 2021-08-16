import pygame, sys
import numpy as np
import math
import random

"""
IDEE = https://www.youtube.com/watch?v=gxAaO2rsdIs&ab_channel=3Blue1Brown
       https://www.washingtonpost.com/graphics/2020/world/corona-simulator/ 

Motivation:  Ich wollte die interaktive Simulation aus der washingtonpost schon lange in Python
implementieren hatte nur nie die Motivation dazu. Hier hat die Einsteigeraufgabe gut geholfen :)

Das Fenster ist nicht dynamisch, deshalb würde ich emfehlen die Simulation nur auf großen Bildschirmen 
zu nutzen. Sonst kann das Fenster in l.107 verändert werden. Falls ich den Graphen noch schaffe, muss man 
in l.150 die größen auch noch verändern, oder bei Objektdekleration. 

"""


SCHWARZ = (18, 18, 18) 
GESUND_FARBE = (55, 0, 179) 
KRANK_FARBE = (144, 12, 63)
GENESEN_FARBE = (3, 218, 186) 
TOD_FARBE = (128,0,128)
STATISTICS_BG = SCHWARZ 

FPS = 45 
GUY_SPEED = 2 

HINTERGRUND = SCHWARZ

class Person(pygame.sprite.Sprite):
    def __init__(self,
                 x,
                 y,
                 breite,
                 hoehe,
                 farbe=SCHWARZ,
                 radius=3,
                 velocity =[0,0],
                 chaos=False
                 ):
        super().__init__()
        self.image = pygame.Surface([radius *2, radius*2])
        self.image.fill(HINTERGRUND)
        pygame.draw.circle(self.image, farbe, (radius, radius), radius)

        self.rect = self.image.get_rect() #Hitbox
        self.pos = np.array([x,y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.entscheidung = False
        self.genesen = False
        self.chaos = chaos

        self.BREITE = breite
        self.HOEHE = hoehe

    def update(self):

        self.pos += self.vel #Distanz pro Frame

        x, y = self.pos

       
        if x < 0:
            self.pos[0] = self.BREITE
            x = self.BREITE
        if x > self.BREITE:
            self.pos[0] = 0
            x = 0
        if y < 0:
            self.pos[1] = self.HOEHE
            y = self.HOEHE
        if y > self.HOEHE:
            self.pos[1] = 0
            y = 0


        self.rect.x = x
        self.rect.y = y

        vel_normale  = np.linalg.norm(self.vel)
        if vel_normale > GUY_SPEED:
            self.vel /= vel_normale

        if self.chaos:
            self.vel += np.random.rand(GUY_SPEED) * GUY_SPEED - GUY_SPEED / 2


        #Jedes mal wenn Person aktualisiert wird
        if self.entscheidung:
            self. updates_bis_Entscheidung -= 1
            if self.updates_bis_Entscheidung <= 0:
                self.entscheidung = False #man kann leider nur einmal leben :(
                x_zufaellig = np.random.rand() #Eine Zahl zwischen 0 und 1 wird gewählt sterberate chance, dass Statement ll Wahr ist
                if self.sterberate >= x_zufaellig:
                    self.kill()
                else:
                    self.genesen = True

    def respawn(self, farbe, radius=3):
        return Person( #Erstellt Kopie von Person, nur farbe wird geändert
            self.rect.x,
            self.rect.y,
            self.BREITE,
            self.HOEHE,
            farbe=farbe,
            velocity=self.vel, #TODO evtl. schneller machen
        )
    def tod_oder_genesen(self, updates_bis_Entscheidung=200, sterberate=0.2):
        self.entscheidung = True
        self.updates_bis_Entscheidung = updates_bis_Entscheidung
        self.sterberate = sterberate

class Simulation:
    def __init__(self, breite= 1300, hoehe = 650):
        self.BREITE = breite
        self.HOEHE = hoehe


        self.gesund_container = pygame.sprite.Group()
        self.infiziert_container = pygame.sprite.Group()
        self.genesen_container = pygame.sprite.Group()
        self.alle_container = pygame.sprite.Group() #Um alle aufeinamal zu aktualisieren

        self.x_gesund = 69 #Manchmal bin ich einfach zu lustig
        self.x_infiziert = 1
        self.x_still = 0
        self.inf_vel = 2
        self.T = 10000
        self.zeit_bis_Entscheidung = 200
        self.sterberate = 0.2

    def start(self, chaos=False):

        self.ALLE = self.x_gesund + self.x_infiziert + self.x_still
        pygame.init()


        for i in range (self.x_gesund):
            x = np.random.randint(0, self.BREITE)
            y = np.random.randint(0, self.HOEHE)

            vel = np.random.rand(2) * GUY_SPEED - GUY_SPEED /2
            guy = Person(x, y, self.BREITE, self.HOEHE, farbe=GESUND_FARBE, velocity=vel, chaos = chaos)
            self.alle_container.add(guy)
            self.gesund_container.add(guy)

            for i in range(self.x_still):
                x = np.random.randint(0, self.BREITE)
                y = np.random.randint(0, self.HOEHE)

                vel = [0, 0]
                guy = Person(x, y, self.BREITE, self.HOEHE, farbe=GESUND_FARBE, velocity=vel)
                self.alle_container.add(guy)
                self.gesund_container.add(guy)


        #erstellen von Infizierten
        for i in range(self.x_infiziert):
            x = np.random.randint(0, self.BREITE + 1)
            y = np.random.randint(0, self.HOEHE + 1)

            vel = np.random.rand(2) * self.inf_vel - GUY_SPEED/2
            guy = Person(x, y, self.BREITE, self.HOEHE, farbe=KRANK_FARBE, velocity=vel, chaos=chaos)
            self.alle_container.add(guy)
            self.infiziert_container.add(guy)

        screen = pygame.display.set_mode([self.BREITE, self.HOEHE])

        statistics = pygame.Surface((self.BREITE // 4, self.HOEHE // 4))

        #Initialisierung von Fläche Graph
        statistics.fill(STATISTICS_BG)
        statistics.set_alpha(130) #Durchsichtigkeit kann evtl. nicht funktionieren ist 50 / 50 bei mir
        statistics_position = (self.BREITE // 40, self.HOEHE //40)

        clock = pygame.time.Clock() #Um Frames zu bestimmen

        for i in range(self.T):
            for event in pygame.event.get(): #Schaut ob X geklickt wurde
                if event.type == pygame.QUIT:
                    sys.exit()#Besser als exit() aus standard

            self.alle_container.update()#Alle Personen werden aktualisiert

            screen.fill(HINTERGRUND)
            

            #Aktualisierung von Statistiken

            statistics_hoehe = statistics.get_height()
            statistics_breite = statistics.get_width()
            x_Infiziert_t = len(self.infiziert_container) #Anzahl Personen, die jetzt infiziert werden
            x_sprites_t = len(self.alle_container) #Anzahl alle Personen -> leider sterben personen hier
            x_genesen_t = len(self.genesen_container)

            #Hier kein Plot, sondern Array
            t = int((i/self.T) * statistics_breite) #t ist x-Wert des graphen self.T/i = Wie weit sind wir in der Sim?
            # wir gehen von unten nach oben, um zu wissen wie hoch man gehen muss, muss man die infizierten abziehen. Es ist ja keine Gerade
            #Tipp: Einfach Live-Ansehen. Zufällige Gedanken bringen einem immer die besten Ideen
            y_infiziert = int(statistics_hoehe-(x_Infiziert_t / x_sprites_t)* statistics_hoehe)
            #Von oben nach unten, also muss man nichts von hoehe abziehen
            y_tod = int(((self.ALLE - x_sprites_t) / self.ALLE) * statistics_hoehe ) #(...) Alle die Tod sind
            y_genesen = int((x_genesen_t / x_sprites_t) * statistics_hoehe)
            statistics_Funktion = pygame.PixelArray(statistics)

            #Tod ganz oben, dann Genesen und dan Infiziert
            statistics_Funktion[t, y_infiziert:] = pygame.Color(*KRANK_FARBE)
            statistics_Funktion[t, :y_tod] = pygame.Color(*TOD_FARBE)
            statistics_Funktion[t, y_tod:y_tod + y_genesen] = pygame.Color(GENESEN_FARBE)




            #Neue Infektionen
            kollisions_gruppe = pygame.sprite.groupcollide(
                self.gesund_container,#Hat ein Gesunder einen Infizierten berührt?
                self.infiziert_container,
                True, #Die aus dem gesund_container werden entfernt
                False #Die aus dem infiziert_contaienr bleiben
            )
            for guy in kollisions_gruppe:
                neu_guy = guy.respawn(KRANK_FARBE)
                neu_guy.vel *= -1 #Eigentlich egal, aber so kann man kollisionen besser erkennen.
                neu_guy.tod_oder_genesen(self.zeit_bis_Entscheidung, self.sterberate)
                self.infiziert_container.add(neu_guy)
                self.alle_container.add(neu_guy)

            #Genesungen? else bei update
            genesen_list = []
            for guy in self.infiziert_container:
                if guy.genesen:
                    neu_guy =  guy.respawn(GENESEN_FARBE)
                    self.genesen_container.add(neu_guy)
                    self.alle_container.add(neu_guy)
                    genesen_list.append(guy) #So kann man sie aus der Grupper der Infizierten entfernen

                if len(genesen_list) > 0:
                    self.infiziert_container.remove(*genesen_list)
                    self.alle_container.remove(*genesen_list) #Die alten werden ja ersetzt




            self.alle_container.draw(screen)
            del statistics_Funktion #pygame.pyxel verankert das Fenster des Graphen
            statistics.unlock()
            screen.blit(statistics, statistics_position) #An der Statistikposition wird gezeichnet
            pygame.display.set_caption("""                                                                                                             
                                          Epidemie Simulation""")
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()


if __name__ == '__main__':
    #name vom Virus + Attribute ist echt praktisch
    covid = Simulation()
    covid.x_gesund = 400
    covid.x_infiziert = 600
    covid.zeit_bis_Entscheidung = random.randint(0, 150)
    covid.sterberate = 0.2
    covid.x_still = 0
    covid.inf_vel = 40
    covid.T = 600
    covid.start(chaos=False)
