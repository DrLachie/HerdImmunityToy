# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 14:51:05 2015

@author: whitehead
"""

import numpy as np
import time
from matplotlib import pyplot as plt    
    

def main():
    
    tStore = []
    healthSurvStore = []
    freeSurvStore = []
    valRange = np.arange(.0 ,1,.1)    
    
    for immunity in valRange:
        t,h,f = repeatSimAndAverage(20,immunity)  
        tStore.append(t)
        healthSurvStore.append(h)
        freeSurvStore.append(f)
    
    with plt.xkcd():
        fig,ax = plt.subplots(1,2,figsize=(10,4))
        #fig.tight_layout()
        ax[0].scatter(valRange,healthSurvStore,color='r')
        ax[0].set_title('% Susceptible Survival')
        ax[0].set_xlabel('% immunised')
        ax[0].set_xlim(-.10,1)
        ax[0].set_ylim(-10,100)
        ax[0].set_ylabel('% survival')
        
    
        
        ax[1].scatter(valRange,tStore)
        ax[1].set_title('Virus perpetuated for n rounds')
        ax[1].set_xlabel('% immunised')
        ax[1].set_xlim(0,1)        
        ax[1].set_ylabel('Time')
    
def repeatSimAndAverage(repeats,valueToAlter):
    ''' Runs a loop of the simulation 
        Pass a value to allow changing a simulation parameter
        Parameter to change set in runSim()'''
        
    tStore = []
    healthSurvStore = []
    freeSurvStore = []
    for repeat in range(0,repeats):
        t,h,f = runSim(True,valueToAlter)
        tStore.append(t)
        healthSurvStore.append(h)
        freeSurvStore.append(f)
    return np.mean(tStore), np.mean(healthSurvStore), np.mean(freeSurvStore)
    

def runSim(doBatch,value):
    '''Sets up and runs the simulation
        value passed by repeatSimAndAverage()
        Will change depending on setupAndGetPeople()'''   
    
    tic = time.time()
    imsize = 32
    people,im = setupAndGetPeople(imsize,
                                  fraction = 4, #density of people
                                  n_infect = 1, #number of initial infections
                                  fraction_immune = value,
                                  fraction_freeloader = 0.0,   #fraction of immune who choose note to
                                  deathRate = 1.0, #chance of death from infection
                                  batch = doBatch)                          
    if not doBatch:
        time.sleep(1)                                                           
        
    t,healthySurvivePercent,freeSurvivePercent = runLoop(people,
                                                         im,
                                                         imsize,
                                                         maxTime = 1000,
                                                         batch = doBatch
                                                         )
         
    elapsed = time.time() - tic
    print '%f seconds to run' % elapsed
    return t,healthySurvivePercent,freeSurvivePercent
  
def runLoop(people,
            im,
            imsize,
            maxTime = 500,
            liveUpdate = True,
            mortalityGraph = True,
            batch = False):
    '''Loops the simulation in time 
        Needs to be passed a list of people, the image reference (im)
        and the image size'''

    if batch:
        #batch over-rides other options
        liveUpdate = False
        mortalityGraph = False 
                
    healthyStart = len([x for x in people if x.status == 'healthy'])
    freeloadStart = len([x for x in people if x.status == 'freeloader'])    
       
    t=0
    infectedPeople = getInfectedPositions(people) 
    mort = [(t,len(infectedPeople),1)]
    while len(infectedPeople)>0 and t<maxTime:
        n_dead = 0
        
        t+=1  
        if liveUpdate:
            time.sleep(.001)
        
        for person in people:   
            person.move(infectedPeople)
        
        infectedPeople = getInfectedPositions(people) 
            
        
        for person in people:
            if person.status == 'healthy' or person.status == 'freeloader':
                NN = person.getNeighbours()
                if len(set(NN).intersection(infectedPeople)) > 0:
                    person.infect()
            else:
                if person.status == 'dead':
                    #people.pop(idx)
                    n_dead += 1
                    
        
        mort.append((t,n_dead,len(infectedPeople)))
                
        if liveUpdate: 
            plt.title('Infected people: %i\nPeople killed %i' % 
                        (len(infectedPeople),n_dead))
        
            image = makeImage(people,imsize)
            im.set_data(image)
            plt.draw()
    
    if mortalityGraph:
        plt.figure(num=2)
        plt.plot([x[0] for x in mort],[x[1] for x in mort]) 
        plt.plot([x[0] for x in mort],[x[2] for x in mort])
        figman = plt.get_current_fig_manager()
        geom = figman.window.geometry()
        x0,y0,dx,dy = geom.getRect()
        figman.window.setGeometry(20, 900, dx, dy)   
        
    
    healthySurvivors = len([x for x in people if x.status == 'healthy'])
    freeloadSurvivors = len([x for x in people if x.status == 'freeloader'])

    healthySurvivePercent = (100.*(float(healthySurvivors) / healthyStart))
    try:    
        freeloadSurvivePercent = (100.*(float(freeloadSurvivors) / freeloadStart))  
    except:
        freeloadSurvivePercent = -1.0
    
    return t, healthySurvivePercent, freeloadSurvivePercent

def setupAndGetPeople(imsize = 128,
                      fraction = 4,
                      n_infect = 1,
                      fraction_immune = .3,
                      fraction_freeloader = .1,
                      deathRate = .1,
                      batch = False):
    '''Sets up the "population" for the simulation, 
    returns as a list of people/pixels'''
                          
    plt.close('all')
    numberOfPeople = int((imsize*imsize)/fraction)
  
    n_healthy = numberOfPeople - n_infect
    n_immune = int(fraction_immune * n_healthy)
    n_free = int(fraction_freeloader * n_immune)
    n_immune = n_immune - n_free
    
    n_healthy = n_healthy - n_immune - n_free

    if not batch:    
        status = ('\nStarting Conditions\nTotal people: %i\t'
                  'Healthy people: %d\n'
                  'Immunised: %d\t'
                  'Freeloaders: %d' % (numberOfPeople,
                                      float(n_healthy)/1,
                                      float(n_immune)/1,
                                      float(n_free)/1))
        print status
    
     
    people = initPeople(imsize,n_healthy,n_infect,n_immune,n_free,deathRate)
    
    if not batch:
        image = makeImage(people,imsize)
        
        fig,ax = plt.subplots(1,1,figsize=(9,9))
        plt.tight_layout()
     
        im = ax.imshow(image, interpolation='none')    
        fig.canvas.draw()
        figman = plt.get_current_fig_manager()
        geom = figman.window.geometry()
        x,y,dx,dy = geom.getRect()
        figman.window.setGeometry(20, 50, dx, dy+50)
        plt.show()
    else:
        im = 0
    return people,im
                      

class pixel():
    def __init__(self,imageSize,position,status='healthy',deathRate=0.1):
        '''pixel has an initial position and is healthy by default
        Options for status are  'healthy'
                                'infected'
                                'immune'
                                '''
        self.size = imageSize
        self.x = int(position[0])
        self.y = int(position[1])
        self.alive = True
      
        self.lengthOfInfection = 0
        self.status = status   
        
        self.statusColor = {'healthy':[0,1,0],  #GREEn
                       'infected':[1,0,0],      #RED 
                       'immune':[0,0,1],        #BLUE
                        'freeloader':[1,0,1],   #CYAN
                        'dead':[.5,.1,.1]}
        
        self.value = self.statusColor[self.status]
        self.deathRate = deathRate
        
        
    def move(self,infectedPeoplePositions):
        infectionLength = 25
      #  imageMap[self.x,self.y] = 0        
        if not self.status == 'dead':
            xmove = np.random.randint(-1,2)
            ymove = np.random.randint(-1,2)
            
            if self.x+xmove >= 0 and self.x+xmove < self.size:        
                self.x = self.x+xmove
                
            if self.y+ymove >= 0 and self.y+ymove < self.size:                
                self.y = self.y+ymove
            
            if self.status == 'infected':
                self.lengthOfInfection+=1 
            
                if self.lengthOfInfection >= infectionLength:              
                    coinflip = np.random.rand(1)
                                       
                    if coinflip[0] < self.deathRate:                                 
                        self.status = 'dead'                           
                    else:                    
                        self.status = 'immune'
                        self.lengthOfInfection = 0
                    self.value = self.statusColor[self.status]
        
    def getNeighbours(self):
        neighbours = []
        for i in range(-1,2):
            for j in range(-1,2):
                newx,newy = self.x+i,self.y+1
                if newx>=0 and newy>=0 and newx<self.size and newy<self.size:
                    neighbours.append((self.x+i,self.y+j))
    #    imageMap[self.x,self.y] = self.value
        return neighbours 
    
    def infect(self):
        self.status = 'infected'
        self.value = self.statusColor[self.status]
        
        
        
    
def makeImage(people,imageSize):
    image = np.zeros([imageSize,imageSize,3])  
    for person in people:
        image[person.x,person.y] = person.value
    return image


def getInfectedPositions(people):
    infPos = []
    for person in people:
        if person.status == 'infected':
            infPos.append((person.x,person.y))
    return infPos

def initPeople(imsize,numberOfPeople,n_infect,n_immune,n_freeloaders,deathRate):
   
    people = []
    
    for i in range(0,numberOfPeople):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos,deathRate=deathRate))
        
    for i in range(0,n_infect):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos,status='infected',deathRate=deathRate))
    
    for i in range(0,n_immune):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos,status='immune',deathRate=deathRate))
        
    for i in range(0,n_freeloaders):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos,status='freeloader',deathRate=deathRate))
    return people
    

#runSim(False)
main()