# visual for traffic sim
# Brevin Kunde 9/15/25

#car objects are spawned in random intervals and approach a stoplight
#if the light is red the car stops at the light or if their is a car
#already in front they stop with a small gap between the car in front
#when the light turns green the car in front goes
#the next car pulls up to the line and repeats the same action
#if the light is green the car goes

import random
import time
import itertools
import pygame


# --- Settings ---
FULL_SCREEN = (1280,720)
WIDTH = FULL_SCREEN[0]//2
HEIGHT = FULL_SCREEN[1]//2
FRAMERATE = 30

STOPLINE = WIDTH//2 -20
CARLEN = 40
DISTANCEBUFFER = 5

# --- GLOBALS ---
GREEN = 6       # How long light is green
RED = 6         # How long light is red


class CarObj:
    def __init__(self, cid, arrivalTime, color, x):
        self.id = cid
        self.arrivalTime = arrivalTime 
        self.departureTime = None
        self.color = color
        self.x = x
        self.y = HEIGHT//2+15
        self.speed = 120
        
    def draw(self, screen):
        pygame.draw.rect(screen, 'black', pygame.Rect(self.x, self.y, CARLEN+1,21),1)
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, CARLEN,20))

    def move(self, dt, trafficLight, start):
        newX = dt*self.speed #Move the car by updating x
        

        #check light
        if trafficLight.getStatus():        #GREEN
            self.x += newX 
            trafficLight.dequeue()
            self.departureTime = time.time() - start
            whereToStop = STOPLINE
            return

        else:                               #RED
            #check if near stopline or other car
            waitingCars = trafficLight.queueLen()
            stopPoint = STOPLINE-(((CARLEN+5)*(waitingCars+1)))

            if self.x < stopPoint-5:
                #car is before the line and should drive up to the line
                self.x += newX 
                return
            elif self.x >= STOPLINE:
                #car is past the line and should keep driving
                self.x += newX
                return
            else:
                #car is stopped at line
                if not (self in trafficLight.trafficQueue):
                    trafficLight.enqueue(self)
    
    def getWaitTime(self):
        return self.departureTime - self.arrivalTime

        
           

class TrafficLightObj:
    def __init__(self, lightDuration):
        #status: Red = False, Green = True
        self.status = False
        #how long before light switches
        self.lightDuration = lightDuration
   
        #FIFO queue for cars at light
        self.trafficQueue = []

    def getStatus(self):
        return self.status

    def enqueue(self, car):
        self.trafficQueue.append(car)

    def dequeue(self):
        if len(self.trafficQueue) > 0:
            return self.trafficQueue.pop(0)

    def queueLen(self):
        return len(self.trafficQueue)

    def flip(self):
        self.status = not self.status
            

def spawnCar(start):
    x = random.randint(-120, -CARLEN)
    arrivalTime = time.time() - start
    car = CarObj(0, arrivalTime, 'red', x)
    return car

        

def trafficVisual(runtime=30, lightDuration=6):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    start = time.time()
    totalWait = 0
    totalCar = 0

    #create trafficLight
    trafficLight = TrafficLightObj(lightDuration)
    #cars list for all cars in scene
    cars = []

    #pygame setup   
    clock = pygame.time.Clock()
    running = True

    count = 0 
    carCount = 0
    runcount = 0

    
    while running:
        if runcount >= (runtime*FRAMERATE):
            break
    
        dt = clock.tick(FRAMERATE) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill('black')

        #--- SIM LOGIC & VISUAL ---
        #check light signal
        if count >= (trafficLight.lightDuration*FRAMERATE):
            count = 0
            trafficLight.flip()    

        #Draw Road and Traffic light

        #Road
        pygame.draw.rect(screen, (62,88,77), pygame.Rect(0,HEIGHT//4+50,WIDTH,100))
        #Center Dashed Line
        for i in range(0, WIDTH, 50):
            pygame.draw.rect(screen, (242,233,48), pygame.Rect(i,(HEIGHT//2),25,5))
        #StopLine
        pygame.draw.rect(screen,'white',pygame.Rect(STOPLINE, HEIGHT//4+50,5,100))
        #Light Indicator
        lightColor = (60,210,60) if trafficLight.getStatus() else (210,50,50)
        pygame.draw.circle(screen,lightColor, (STOPLINE+60, HEIGHT//4+75),10)
        

        #SPAWN CARS       
        carSpawn = random.randint(1,5)
        if carCount >= (carSpawn*FRAMERATE):
            carCount = 0
            cars.append(spawnCar(start))
        
        
        for i, car in enumerate(cars):
            car.move(dt, trafficLight, start)
            car.draw(screen)

            if car.x >= WIDTH:
                cars.remove(car)
                totalWait += car.getWaitTime()
                totalCar += 1

        


        currentTime = round((pygame.time.get_ticks()/1000),1)
        #draw HUD
        font = pygame.font.SysFont(None, 18)
        txtTime = font.render(f"Time: {currentTime}", True, (220,220,220))
        txt = font.render(f"Cars Waiting: {trafficLight.queueLen()}   Cars: {totalCar} ", True, (220,220,220))
        screen.blit(txtTime, (8,8))
        screen.blit(txt, (100,8))
        pygame.display.flip()

        count+=1
        carCount+=1
        runcount+=1
    
    if totalCar == 0:
        avgWait = 0
    else:
        avgWait = round(totalWait/totalCar, 2)
    print(f"{totalCar} cars waited an average of {avgWait} seconds for the light to turn green")
    pygame.quit()
    return avgWait





if __name__ == '__main__':
    trafficVisual()
