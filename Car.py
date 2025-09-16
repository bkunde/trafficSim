#car agent has two actions:
    # 0: car drives through green light
    # 1: car stops and queues at red light

class Car(object):
    def __init__(self, env, number):
        self.env = env
        self.number = number
        self.arrival_time = env.now
        self.departure_time = 0

    
    def drive(self):
        self.departure_time = self.env.now
        wait_time = str(self.departure_time - self.arrival_time)[:4]
        print('Car %s left after waiting %s' % (self.number, wait_time))


    def __repr__(self):
        return f"<Car {self.number}>"
    

