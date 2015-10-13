# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 14:51:05 2015

@author: whitehead
"""

from skimage import io, filter
import numpy as np
import time
from matplotlib import pyplot as plt

global infectionVal, immuneVal, aliveVal, infectionLength
immuneVal = 4
infectionVal = 8
infectionLength = 10
aliveVal = 2

def main():
    plt.close('all')
    imsize = 128
    numberOfPeople = (imsize*imsize)/15
    n_infect = 10
    n_immune = int(0.9 * numberOfPeople)
    
       
    people = initPeople(imsize,numberOfPeople,n_infect,n_immune)
    image = makeImage(people,imsize)
    
    fig,ax = plt.subplots(1,1)
    im = ax.imshow(image, interpolation='none')    
    fig.canvas.draw()
    figman = plt.get_current_fig_manager()
    geom = figman.window.geometry()
    x,y,dx,dy = geom.getRect()
    figman.window.setGeometry(20, 20, dx, dy)
   # figman.window.setPosition(0,0)
   

    for i in range(0,150):
        time.sleep(.01)
        
        for person in people:   
            person.move(image)
        
        image = makeImage(people,imsize)        

        for person in people:
            if not person.infected and not person.immune:
                a = person.getNeighbours()
                for i in a:
                    pixval = image[i[0]][i[1]]
                    if pixval == infectionVal:
                        person.infected = True
                        person.value = infectionVal
                
        image = makeImage(people,imsize)  
        
        
        im.set_data(image)
        fig.canvas.draw()


class pixel():
    def __init__(self,imageSize,position,infected=False,immune=False):
        '''pixel has an initial position and is alive by default'''
        self.size = imageSize
        self.x = int(position[0])
        self.y = int(position[1])
        self.alive = True
        self.infected = infected
        self.immune = immune
        self.value = aliveVal
        self.lengthOfInfection = 0
   
      #  imageMap[self.x,self.y] = 1        
        if infected:
         #   imageMap[self.x,self.y] = 3
            self.value = infectionVal
        if immune:
           # imageMap[self.x,self.y] = 2
            self.value = immuneVal
        
        
    def move(self,imageMap):
      #  imageMap[self.x,self.y] = 0        
       
        xmove = np.random.randint(-1,2)
        ymove = np.random.randint(-1,2)
        
        if self.x+xmove >= 0 and self.x+xmove < self.size:        
            self.x = self.x+xmove
            
        if self.y+ymove >= 0 and self.y+ymove < self.size:                
            self.y = self.y+ymove
        
        if self.infected:
            self.lengthOfInfection+=1 
        
        if self.lengthOfInfection > infectionLength:
            self.immune = True
            self.infected = False
            self.value = immuneVal
        
    def getNeighbours(self):
        neighbours = []
        for i in range(-1,2):
            for j in range(-1,2):
                newx,newy = self.x+i,self.y+1
                if newx>=0 and newy>=0 and newx<self.size and newy<self.size:
                    neighbours.append([self.x+i,self.y+j])
    #    imageMap[self.x,self.y] = self.value
        return neighbours 
        
        
        
        
    
def makeImage(people,imageSize):
    image = np.ndarray([imageSize,imageSize]) *0    
    for person in people:
        image[person.x,person.y] = person.value
    return image




def initPeople(imsize,numberOfPeople,n_infect,n_immune):
    image = []    
    people = []
    for i in range(0,numberOfPeople):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos))
    
    for i in range(0,n_infect):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos,infected=True))
    
    for i in range(0,n_immune):
        newPos = [np.random.randint(0,imsize),np.random.randint(0,imsize)]        
        people.append(pixel(imsize,newPos,immune=True))
    
    return people
    

        

def initImage(imageSize,
              numberOfRandoms,
              numberOfInfected = 0,
              numberOfImmune = 0):
                  
    image = np.ndarray([imageSize,imageSize]) *0    
    
    for i in range(0,numberOfRandoms):
        posx = int(np.random.rand() * imageSize)
        posy = int(np.random.rand() * imageSize)
        #print posx,posy
        if image[posx,posy] == 0:
            image[posx,posy] = 1
        else:
            pass            
            #image[posx,posy] = image[posx,posy] + 1
        
    for i in range(0,numberOfInfected):
        posx = int(np.random.rand() * imageSize)
        posy = int(np.random.rand() * imageSize)
        #print posx,posy
        image[posx,posy] = infectionVal
        
    for i in range(0,numberOfImmune):
        posx = int(np.random.rand() * imageSize)
        posy = int(np.random.rand() * imageSize)
        #print posx,posy
        image[posx,posy] = immuneVal

    return image
    
    
    
main()