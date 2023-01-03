from Model.Buildings.Building import *
from Model.Walker import *
from Model.Case import *

class WorkBuilding(Building):
    def __init__(self, position, case, size, desc, walker, active, connectedToRoad=0, fireRisk=0, collapseRisk=0, status=False):
        super().__init__(position, case, size, desc, connectedToRoad, status, fireRisk, collapseRisk)
        self.walker = walker
        self.active = False

    def setWalker(self,newWalker):
        self.walker=newWalker

    def getWalker(self):
        return self.walker

    def setActive(self,NewActive):
        self.active = NewActive

    def getActive(self):
        return self.active

    def buildAWorkBuilding(laCase, wbsize,wbdesc,wbwalker,wbSprite):
        newWorkbuilding = WorkBuilding(laCase.coor,laCase,wbsize,wbdesc,wbwalker,0,laCase.connectedToRoad,0,0,True)
        laCase.setFeature(wbdesc)
        #laCase.setSprite(wbSprite)
        return newWorkbuilding

class Prefecture(WorkBuilding) :

    cityPrefectures = []

    def __init__(self, case, size, desc, walker, active, connectedToRoad=0, fireRisk=0, collapseRisk=0, status=False):
        super().__init__( case, size, desc, connectedToRoad, walker, active, status, fireRisk, collapseRisk)

     
    def buildAPrefecture(laCase, lePlateau) :
        #Create a Walker myWalker
        newPrefecture = WorkBuilding.buildAWorkBuilding(laCase,"Prefecture","Security_00001.png") # + myWalker
        Prefecture.cityPrefectures.append(newPrefecture)

    def activatePrefecture(aPrefecture,lePlateau) :
        aPrefecture.setActive(True)
        #Create a Prefect myPrefect
        #aPrefecture.setWalker(myPrefect)
        #Case.getRelative(aPrefecture.case,0,1,lePlateau).addSprite("Security_00002.png")
        

