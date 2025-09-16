import simpy
#import car

def car(env, name, bcs, driving_time, charge_duration):
    #simulate driving to BCS
    yield env.timeout(driving_time)
    
    #request one of the charging spots
    print('%s arriving at %d' % (name, env.now))
    with bcs.request() as req:
        yield req

        #charge the battery
        print('%s starting to carge at %s' % (name, env.now))
        yield env.timeout(charge_duration)
        print('%s leaving the bcs at %s' % (name, env.now))


def main():
    env = simpy.Environment()
    bcs = simpy.Resource(env, capacity=2)
    
    for i in range(4):
        env.process(car(env, 'Car %d' % i, bcs, i*2, 5))
    
    env.run()
    
    return

if __name__ == '__main__':
    main()
