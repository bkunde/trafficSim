import matplotlib.pyplot as plt
import trafficVis


def main():
    #how many times does user want to run sim
    simRuns = 0
    simRuns = int(input("How many times would you like to run the simulation? "))
    while (simRuns <= 0 or simRuns > 10):
        simRuns = int(input("Out of range of allowed simulations, Enter again: "))

    #how long is the traffic light
    lightDuration = int(input("How long before the light switches? "))
    #run sim
    x = []
    y = []
    for i in range(simRuns):
        avgWait = trafficVis.trafficVisual(30, lightDuration+i)
        x.append(i+1)
        y.append(avgWait)


    fig, ax = plt.subplots()
    ax.plot(x,y)
    plt.show()
    return



if __name__ == '__main__':
    main()
