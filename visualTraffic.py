import pygame, itertools, random, math
import simpy
from collections import deque


#--- SETTINGS ---
FULL_SCREEN = (1280,720)
WIDTH = FULL_SCREEN[0]//2
HEIGHT = FULL_SCREEN[1]//2
FRAME_RATE = 30

LANES = 1                    # How many lanes of traffic
STOPLIGHT_DURATION = 6       # How long a green and red light are (seconds)
SIM_TIME = 120               # Simulation time (seconds)

ROAD_Y = HEIGHT//2 +15       # centerline of road
STOP_LINE = WIDTH//2 - 20    # white line on x-axis
CAR_LEN, CAR_WID = 40, 22
CAR_GAP = 10                 # space between stopped cars
CAR_SPEED = 180              #px/s while driving
CROSS_SPEED = 220            #px/s while crossing

# --- GLOBALS ---
STOPLIGHT = False            # False = Redlight; True = Greenlight
green_event = None



class CarSim:
    """ SimPy car """
    def __init__(self, env, cid):
        self.id = cid
        self.arrival_time = env.now
        self.departure_time = None
        self.go_event = env.event()

class CarVis:
    """ Visual-side car; mirrors a CarSim """
    def __init__(self, car_sim):
        self.sim = car_sim
        self.state = "approaching"  #approaching | queued | crossing | done
        self.x = -CAR_LEN - random.randint(0, 60)
        self.y = ROAD_Y
        self.color = (220, 60, 60)
        self.target_stop_x = STOP_LINE - CAR_LEN

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y-CAR_WID//2), CAR_LEN, CAR_WID)
    


# --------------- SimPy Processesm ----------------

def trafficlight_control(env, period):
    global STOPLIGHT, green_event
    while True:
        #red light
        STOPLIGHT = False
        green_event = env.event()
        yield env.timeout(period) #switchlight after the duration

        #green light
        STOPLIGHT = True
        if not green_event.succeed():
            green_event.succeed()
        yield env.timeout(period)


def car_generator(env, traffic, on_car_spawn):
    for i in itertools.count():
        yield env.timeout(random.randint(1,5))
        car = CarSim(env, i)
        on_car_spawn(car)   #create vis car
        env.process(intersection(env, traffic, car))


def intersection(env, traffic, car, cross_time=1.2):
    if not STOPLIGHT:
        yield green_event

    with traffic.request() as req:
        yield req
        
        if not STOPLIGHT:
            yield green_event

        if not car.go_event.triggered:
            car.go_event.succeed()

        yield env.timeout(cross_time)
        car.depature_time = env.now


def main():
    #--- SIM SETUP ---
    env = simpy.Environment()
    traffic = simpy.Resource(env, capacity=LANES)

    #vis containers
    active_cars = []            #CarVis list, any state except done
    queue = deque()             #carVis objs stopped at stopline

    def on_car_spawn(car_sim):
        cv = CarVis(car_sim)
        active_cars.append(cv)
        print(f"[spawn] car {car_sim.id} at sim t={env.now:.2f}, will start x={cv.x}")
    test_car_rect = pygame.Rect(20, ROAD_Y - CAR_WID//2, CAR_LEN, CAR_WID)
    
    env.process(trafficlight_control(env, STOPLIGHT_DURATION))
    env.process(car_generator(env, traffic, on_car_spawn))

    #--- pygame setup ---
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    
    sim_limit = SIM_TIME

    def update_visual(dt):
        nonlocal queue, active_cars

        """Move Cars and manage queue targets"""
        #Queue = Cars that have reached their stop target and are waitnig
        #Refresh queue membership based on positions/states
        #Maintaing exisiting queue; then add new eligible cars in arrival order
        #

        #helper func to compute front-most occupied stopping pos
        def stop_pos_for_index(idx): # 0 = STOPLINE
            return STOP_LINE - CAR_LEN - idx * (CAR_LEN + CAR_GAP)


        # --- STEP A: advance approaching cars ---
        for car in active_cars:
            if car.state == "approaching":        
                if STOPLIGHT and len(queue) == 0:
                    car.x += CAR_SPEED *dt
                else:
                    front_limit = STOP_LINE - CAR_LEN
                    next_x = car.x + CAR_SPEED * dt
                    car.x = min(next_x, front_limit)

        # --- STEP B: refresh queue memebership, only keeping queued
        queue = deque([c for c in queue if c.state == "queued"])


        # --- STEP C: form queue when needed(red or somone already queued) ---
        q_len = len(queue)
        if (not STOPLIGHT) or q_len > 0:
            #order cars left->right
            approaching = [c for c in active_cars if c.state == "approaching"]
            approaching.sort(key=lambda c: c.x)

            for car in approaching:
                target = stop_pos_for_index(q_len)
                if car.x + CAR_LEN >= target:
                    car.state = "queued"
                    car.target_stop_x = target
                    queue.append(car)
                    q_len += 1

        # --- STEP D: queued cars ease to their assigned slot
        k = 6
        for car in active_cars:
            if car.state == "queued":
                if car.x < car.target_stop_x:
                    #linear ease approach
                    #car.x += (car.target_stop_x - car.x) * min(1,k*dt)
                    car.x = min(car.x + CAR_SPEED * dt, car.target_stop_x)
                else:
                    car.x = car.target_stop_x 


        # --- STEP E: crossing(front of q goes when allowed by sim)---
        if queue:
            front = queue[0]
            if front.sim.go_event.triggered:
                front.state = "crossing"
                queue.popleft()

        for car in active_cars:
            if car.state == "queued":
                car.x += CROSS_SPEED * dt
                if car.x > WIDTH + 10:
                    car.state = "done"

        # --- cleanup ---
        active_cars[:] = [c for c in active_cars if c.state != "done"]
        

    def draw():
        #background

        #road
        pygame.draw.rect(screen,(62, 68, 77), pygame.Rect(0,(HEIGHT//4)+50,WIDTH,100))
        #center dashed line
        for i in range(0, WIDTH, 50):
            pygame.draw.rect(screen, (242, 233, 48), pygame.Rect(i,(HEIGHT//2),25, 5))

        #stop line
        pygame.draw.rect(screen, 'white', pygame.Rect(STOP_LINE, HEIGHT//4+50, 5, 100))

        # light indicator
        light_color = (60,210,60) if STOPLIGHT else (210,50,50)
        pygame.draw.circle(screen, light_color, (STOP_LINE+60, HEIGHT//4+75), 10)
        
        #draw cars
        for car in active_cars:
            pygame.draw.rect(screen, car.color, car.rect)


        #simple HUD
        font = pygame.font.SysFont(None, 18)
        txt = font.render(f"Light: {'GREEN' if STOPLIGHT else 'RED'}    Cars: {len(active_cars)}", True, (220, 220, 220)) 
        screen.blit(txt, (8,8))

    # --- Main Loop --- 
    while running:
        dt = clock.tick(FRAME_RATE) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("black")

        #step through sim in real time
        if env.now < sim_limit:
            env.run(until=min(env.now + dt, sim_limit))

        update_visual(dt)
        draw()
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
