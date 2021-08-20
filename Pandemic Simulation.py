import pygame, sys
import numpy as np
import math
import random

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

        self.pos += self.vel 

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


 
        if self.entscheidung:
            self. updates_bis_Entscheidung -= 1
            if self.updates_bis_Entscheidung <= 0:
                self.entscheidung = False 
                x_zufaellig = np.random.rand() 
                if self.sterberate >= x_zufaellig:
                    self.kill()
                else:
                    self.genesen = True

    def respawn(self, farbe, radius=3):
        return Person(
            self.rect.x,
            self.rect.y,
            self.BREITE,
            self.HOEHE,
            farbe=farbe,
            velocity=self.vel,
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
        self.alle_container = pygame.sprite.Group() 

        self.x_gesund = 69 
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


       
        for i in range(self.x_infiziert):
            x = np.random.randint(0, self.BREITE + 1)
            y = np.random.randint(0, self.HOEHE + 1)

            vel = np.random.rand(2) * self.inf_vel - GUY_SPEED/2
            guy = Person(x, y, self.BREITE, self.HOEHE, farbe=KRANK_FARBE, velocity=vel, chaos=chaos)
            self.alle_container.add(guy)
            self.infiziert_container.add(guy)

        screen = pygame.display.set_mode([self.BREITE, self.HOEHE])

        statistics = pygame.Surface((self.BREITE // 4, self.HOEHE // 4))

        
        statistics.fill(STATISTICS_BG)
        statistics.set_alpha(130) 
        statistics_position = (self.BREITE // 40, self.HOEHE //40)

        clock = pygame.time.Clock() 

        for i in range(self.T):
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT:
                    sys.exit()

            self.alle_container.update()

            screen.fill(HINTERGRUND)
            

            

            statistics_hoehe = statistics.get_height()
            statistics_breite = statistics.get_width()
            x_Infiziert_t = len(self.infiziert_container) 
            x_sprites_t = len(self.alle_container)
            x_genesen_t = len(self.genesen_container)

  
            t = int((i/self.T) * statistics_breite)
            y_infiziert = int(statistics_hoehe-(x_Infiziert_t / x_sprites_t)* statistics_hoehe)
            y_tod = int(((self.ALLE - x_sprites_t) / self.ALLE) * statistics_hoehe )
            y_genesen = int((x_genesen_t / x_sprites_t) * statistics_hoehe)
            statistics_Funktion = pygame.PixelArray(statistics)

            statistics_Funktion[t, y_infiziert:] = pygame.Color(*KRANK_FARBE)
            statistics_Funktion[t, :y_tod] = pygame.Color(*TOD_FARBE)
            statistics_Funktion[t, y_tod:y_tod + y_genesen] = pygame.Color(GENESEN_FARBE)




        
            kollisions_gruppe = pygame.sprite.groupcollide(
                self.gesund_container,
                self.infiziert_container,
                True,
                False 
            )
            for guy in kollisions_gruppe:
                neu_guy = guy.respawn(KRANK_FARBE)
                neu_guy.vel *= -1 
                neu_guy.tod_oder_genesen(self.zeit_bis_Entscheidung, self.sterberate)
                self.infiziert_container.add(neu_guy)
                self.alle_container.add(neu_guy)

           
            genesen_list = []
            for guy in self.infiziert_container:
                if guy.genesen:
                    neu_guy =  guy.respawn(GENESEN_FARBE)
                    self.genesen_container.add(neu_guy)
                    self.alle_container.add(neu_guy)
                    genesen_list.append(guy) 

                if len(genesen_list) > 0:
                    self.infiziert_container.remove(*genesen_list)
                    self.alle_container.remove(*genesen_list) 




            self.alle_container.draw(screen)
            del statistics_Funktion 
            statistics.unlock()
            screen.blit(statistics, statistics_position) 
            pygame.display.set_caption("""                                                                                                             
                                          Epidemie Simulation""")
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()


if __name__ == '__main__':
   
    covid = Simulation()
    covid.x_gesund = 400
    covid.x_infiziert = 600
    covid.zeit_bis_Entscheidung = random.randint(0, 150)
    covid.sterberate = 0.2
    covid.x_still = 0
    covid.inf_vel = 40
    covid.T = 600
    covid.start(chaos=False)
