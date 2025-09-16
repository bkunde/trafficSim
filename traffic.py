import simpy
import itertools
import random


LANES = 1                # How many lanes of traffic
STOPLIGHT_DURATION = 10  # How long a green and red light are (seconds)
SIM_TIME = 120            # Simulation time (seconds)
STOPLIGHT = False        # False = Redlight; True = Greenlight


class CarObj:
    def __init__(self, env, cid):
        self.id = cid
        self.arrival_time = env.now
        self.departure_time = None

def trafficlight_control(env):
    global STOPLIGHT
    while True:
        yield env.timeout(STOPLIGHT_DURATION) #switchlight after the duration
        #change the light
        STOPLIGHT = not (STOPLIGHT)
        print('Changing light to %s' % STOPLIGHT)


def car_generator(env, traffic):
    for i in itertools.count():
        yield env.timeout(random.randint(1,5))
        car = CarObj(env, i)
        print('car %s arrived at %s' % (i, car.arrival_time))
        env.process(intersection(env, traffic, car))


def intersection(env, traffic, car):
    with traffic.request() as req:
        #queue at the front of the intersection
        yield req
        while not STOPLIGHT:
            yield env.timeout(0.1)
        car.departure_time = env.now
        wait_time = str(car.departure_time - car.arrival_time)[:4]
        print('Car %s left after waiting %s' % (car.id, wait_time))

def main():
    env = simpy.Environment()
    traffic = simpy.Resource(env, capacity=LANES)
    env.process(trafficlight_control(env))
    env.process(car_generator(env, traffic))

    env.run(until=SIM_TIME)


if __name__ == '__main__':
    main()
