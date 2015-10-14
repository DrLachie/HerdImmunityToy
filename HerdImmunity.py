# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 14:51:05 2015

@author: whitehead
"""

from skimage import io
import numpy as np
import time
from matplotlib import pyplot as plt

global infectionLength

infectionLength = 25


def main():
    plt.close('all')
    imsize = 100
    numberOfPeople = (imsize*imsize)/5
    print 'Number of people %i' % numberOfPeople
    n_infect = 1
    n_immune = int(0.1 * numberOfPeople)
    numberOfPeople = numberOfPeople - n_infect - n_immune
    
       
    people = initPeople(imsize,numberOfPeople,n_infect,n_immune)
    image = makeImage(people,imsize)
    
    fig,ax = plt.subplots(1,1,figsize=(9,9))
 
    im = ax.imshow(image, interpolation='none')    
    fig.canvas.draw()
    figman = plt.get_current_fig_manager()
    geom = figman.window.geometry()
    x,y,dx,dy = geom.getRect()
    figman.window.setGeometry(20, 20, dx, dy)
    
    infectedPeople = getInfectedPositions(people) 
    
    
   # figman.window.setPosition(0,0)
   

    for i in range(0,150):
        time.sleep(.01)
        
        for person in people:   
            person.move(infectedPeople)
        
        infectedPeople = getInfectedPositions(people) 
        image = makeImage(people,imsize)        
        
        for person in people:
            if person.status == 'healthy':
                NN = person.getNeighbours()
                for pos in NN:
                    if pos in infectedPeople:
                        person.infect()
                        
                
        image = makeImage(people,imsize)  
        plt.title('Infected people: %i' % len(infectedPeople))
        
        
        im.set_data(image)
        fig.canvas.draw()


class pixel():
    def __init__(self,imageSize,position,status='healthy'):
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
        
        self.statusColor = {'healthy':[0,1,0],
                       'infected':[1,0,0],
                       'immune':[0,0,1]}
        
        self.value = self.statusColor[self.status]
        
        
    def move(self,infectedPeoplePositions):
      #  imageMap[self.x,self.y] = 0        
       
        xmove = np.random.randint(-1,2)
        ymove = np.random.randint(-1,2)
        
        if self.x+xmove >= 0 and self.x+xmove < self.size:        
            self.x = self.x+xmove
            
        if self.y+ymove >= 0 and self.y+ymove < self.size:                
            self.y = self.y+ymove
        
        if self.status == 'infected':
            self.lengthOfInfection+=1 
        
        if self.lengthOfInfection > infectionLength:
            self.status = 'immune'           
            self.value = self.statusColor['immune']
        
    def getNeighbours(self):
        neighbours = []
        for i in range(-1,2):
            for j in range(-1,2):
                newx,newy = self.x+i,self.y+1
                if newx>=0 and newy>=0 and newx<self.size and newy<self.size:
                    neighbours.append([self.x+i,self.y+j])
    #    imageMap[self.x,self.y] = self.value
        return neighbours 
    
    def infect(self):
        self.status = 'infected'
        self.value = self.statusColor[self.status]
        
        
        
    
def makeImage(people,imageSize):
    image = np.ndarray([imageSize,imageSize,3]) *0    
    for person in people:
        image[person.x,person.y] = person.value
    return image


def getInfectedPositions(people):
    infPos = []
    for person in people:
        if person.status == 'infected':
            infPos.append([person.x,person.y])
    return infPos

def initPeople(imsize,numberOfPeople,n_infect,n_immune):
    image = []    
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
    
    return people
    

main()