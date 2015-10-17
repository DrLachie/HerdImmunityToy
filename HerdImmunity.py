# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 14:51:05 2015

@author: whitehead
"""

import numpy as np
import time
from matplotlib import pyplot as plt    
    
def main():
    tic = time.time()
    imsize = 128
    people,im = setupAndGetPeople(imsize,
                                  fraction = 4, #density of people
                                  n_infect = 1, #number of initial infections
                                  fraction_immune = .8,
                                  fraction_freeloader = .5,   #fraction of immune who choose note to
                                  deathRate = 1. #chance of death from infection
                                  )                          
                                                              
    runLoop(people,
            im,
            imsize,
            maxTime = 1000,
            liveUpdate = True
            )
    #draw again at the end       
    image = makeImage(people,imsize)
    im.set_data(image)
    plt.draw()
    
    elapsed = time.time() - tic
    print '%f seconds to run' % elapsed
  
def runLoop(people,
            im,
            imsize,
            maxTime = 500,
            liveUpdate = True):
    healthyStart = len([x for x in people if x.status == 'healthy'])
    freeloadStart = len([x for x in people if x.status == 'freeloader'])    
    print freeloadStart    
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
        
        
    print 'Virus survived for %i rounds' % t
    print '%.2f%% of un-vaccinateable survived' % healthySurvivePercent
    print '%.2f%% of freeloaders survived' % freeloadSurvivePercent
    
    

def setupAndGetPeople(imsize = 128,
          fraction = 4,
          n_infect = 1,
          fraction_immune = .3,
          fraction_freeloader = .1,
          deathRate = .1):
              
    plt.close('all')
    numberOfPeople = int((imsize*imsize)/fraction)
  
    n_healthy = numberOfPeople - n_infect
    n_immune = int(fraction_immune * n_healthy)
    n_free = int(fraction_freeloader * n_immune)
    n_immune = n_immune - n_free
    
    n_healthy = n_healthy - n_immune - n_free
    status = ('\nStarting Conditions\nTotal people: %i\t'
              'Healthy people: %d\n'
              'Immunised: %d\t'
              'Freeloaders: %d' % (numberOfPeople,
                                  float(n_healthy)/1,
                                  float(n_immune)/1,
                                  float(n_free)/1))
    print status
    
     
    people = initPeople(imsize,n_healthy,n_infect,n_immune,n_free,deathRate)
    
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
    return people,im
                      

class pixel():
    def __init__(self,imageSize,position,status='healthy',deathRate=.1):
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
        self.deathrate = deathRate
        
        
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
                    if coinflip[0] < 0.95:                                 
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
        people.append(pixel(imsize,newPos))
    
    for i in range(0,n_infect):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos,status='infected'))
    
    for i in range(0,n_immune):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos,status='immune'))
        
    for i in range(0,n_freeloaders):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos,status='freeloader'))
    
    return people
    

main()