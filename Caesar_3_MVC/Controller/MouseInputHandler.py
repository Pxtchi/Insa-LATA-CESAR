import pygame
from Model.constants import *
from Model.control_panel import *
from EventManager.Event import Event
from EventManager.allEvent import StateChangeEvent, TickEvent, QuitEvent
from Model.Plateau import Plateau, cell_size
from Model.Route import Route
from Model.Buildings.Building import *
from Model.Buildings.House import *
from Model.Buildings.WorkBuilding import *
from Model.Buildings.UrbanPlanning import *

class MouseInputHandler:
    """
    Handles mouse input.
    """
    def __init__(self, evManager, model) -> None:
        self.evManager = evManager
        self.model = model
        self.clicked = False
        self.initialMouseCoordinate = False
        self.finalClickCoordinate = False

    def handleInput(self, event: Event) -> None:
        """
        Receive events posted to the message queue. 
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                        self.clicked = True
                        self.initialMouseCoordinate = pygame.mouse.get_pos()

                        if self.model.pause_menu.Exit_rect.collidepoint(event.pos) and self.model.pause_menu.pause:
                            self.model.pause_menu.exit()

                        if self.model.pause_menu.Continue_rect.collidepoint(event.pos) and self.model.pause_menu.pause:
                            self.model.pause_menu.pause = False
                            self.model.actualGame.pause = False

                        if self.model.pause_menu.Savegame_rect.collidepoint(event.pos) and self.model.pause_menu.pause:
                            pass

                        if self.model.pause_menu.Replay_rect.collidepoint(event.pos) and self.model.pause_menu.pause:
                            self.model.actualGame.restart = True
                            self.model.actualGame.update()
                            self.model.pause_menu.pause = False
                            self.model.actualGame.pause = False
        elif event.type == pygame.MOUSEBUTTONUP:
                if(self.clicked):
                        # get current state
                        self.finalClickCoordinate = pygame.mouse.get_pos()
                        currentstate = self.model.state.peek()
                        if currentstate == STATE_INTRO_SCENE:
                                self.handleMouseEventsStateIntroScene(event)
                        if currentstate == STATE_MENU:
                                self.handleMouseEventsStateMenu(event)
                        if currentstate == STATE_PLAY:
                                self.handleMouseEventsStatePlay(event)
                if event.button == 1:
                        self.clicked = False
                        self.initialMouseCoordinate = None

        #  Preview clear land
        
        elif event.type == pygame.MOUSEMOTION:
            temp = pygame.mouse.get_pos()
            if temp != self.initialMouseCoordinate:
                self.handleMouseMouvement(event)

        # Handle all hover
        self.hoverEvent(event)

    def hoverEvent(self, event):
        mousePos = event.pos 
        currentstate = self.model.state.peek()
        if currentstate == STATE_INTRO_SCENE:
            self.handleHoverEventIntroScene(mousePos)
        elif currentstate == STATE_MENU:
            self.handleHoverEventMenu(mousePos)
        elif currentstate == STATE_PLAY:
            self.checkEveryButton(event)
            
    def handleHoverEventIntroScene(self, mousePos):
        self.model.introScene.handleHoverEvent(mousePos)

    def handleHoverEventMenu(self, mousePos):
        self.model.menu.handleHoverEvent(mousePos)

    def handleMouseEventsStateIntroScene(self, event):
        """
        Handles intro scene mouse events.
        """
        feedBack = self.model.introScene.handleMouseInput(event)
        self.evManager.Post(feedBack)

    def handleMouseEventsStateMenu(self, event):
        """
        Handles menu mouse events.
        """
        feedBack = self.model.menu.handleMouseInput(event)
        self.evManager.Post(feedBack)

    def checkEveryButton(self, event):
        """
            Check if a button has been pressed
        """
        
        #Handle the buttons of the control panel
        
        event.pos = (event.pos[0] - (self.model.actualGame.width - big_gap_menu.dim[0]), event.pos[1] - 24)
        for button in self.model.actualGame.controls.listOfButtons:
            button.handle_event(event)

    def handleMouseEventsStatePlay(self, event):
        """
        Handles game mouse events
        """
        #Pelle
        if self.model.actualGame.controls.clear_land_button.clicked and not self.model.actualGame.controls.clear_land_button.rect.collidepoint((event.pos[0] - 1758.0, event.pos[1] - 24)):
            x, y = self.initialMouseCoordinate
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x1 = int(cart_x // cell_size)
            grid_y1 = int(cart_y // cell_size)

            x, y = event.pos
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x2 = int(cart_x // cell_size)
            grid_y2 = int(cart_y // cell_size)
        
            if grid_x1 <0:
                grid_x1 = 0
            if grid_x2 <0:
                grid_x2 = 0
            if grid_y1 <0:
                grid_y1 = 0
            if grid_y2 <0:
                grid_y2 = 0

            if grid_x1 > self.model.actualGame.nbr_cell_x-1:
                grid_x1 = self.model.actualGame.nbr_cell_x-1
            if grid_x2 > self.model.actualGame.nbr_cell_x-1:
                grid_x2 = self.model.actualGame.nbr_cell_x-1
            if grid_y1 > self.model.actualGame.nbr_cell_y-1:
                grid_y1 = self.model.actualGame.nbr_cell_y-1
            if grid_y2 > self.model.actualGame.nbr_cell_y-1:
                grid_y2 = self.model.actualGame.nbr_cell_y-1

            if grid_x1 > grid_x2:
                temp = grid_x1
                grid_x1 = grid_x2
                grid_x2 = temp

            if grid_y1 > grid_y2:
                temp = grid_y1
                grid_y1 = grid_y2
                              
                grid_y2 = temp

            for xi in range(grid_x1, grid_x2+1):
                for yi in range(grid_y1, grid_y2+1):
                        if self.model.actualGame.map[xi][yi].sprite not in list_of_undestructible:
                            self.model.actualGame.map[xi][yi].sprite = "land1"
                            if self.model.actualGame.map[xi][yi].road :
                                self.model.actualGame.map[xi][yi].road.delete()
                                self.model.actualGame.treasury = self.model.actualGame.treasury - DESTRUCTION_COST
                            if self.model.actualGame.map[xi][yi].structure :
                                self.model.actualGame.map[xi][yi].structure.delete()
                                self.model.actualGame.treasury = self.model.actualGame.treasury - DESTRUCTION_COST
                              
                            
            self.model.actualGame.collision_matrix = self.model.actualGame.create_collision_matrix()
            
            self.model.actualGame.foreground.initForegroundGrid()
                
        #Routes
        if self.model.actualGame.controls.build_roads_button.clicked and not self.model.actualGame.controls.build_roads_button.rect.collidepoint((event.pos[0] - 1758.0, event.pos[1] - 24)):
        
            x, y = self.initialMouseCoordinate
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x1 = int(cart_x // cell_size)
            grid_y1 = int(cart_y // cell_size)

            x, y = event.pos
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x2 = int(cart_x // cell_size)
            grid_y2 = int(cart_y // cell_size)
        
            if grid_x1 <0:
                grid_x1 = 0
            if grid_x2 <0:
                grid_x2 = 0
            if grid_y1 <0:
                grid_y1 = 0
            if grid_y2 <0:
                grid_y2 = 0

            if grid_x1 > self.model.actualGame.nbr_cell_x-1:
                grid_x1 = self.model.actualGame.nbr_cell_x-1
            if grid_x2 > self.model.actualGame.nbr_cell_x-1:
                grid_x2 = self.model.actualGame.nbr_cell_x-1
            if grid_y1 > self.model.actualGame.nbr_cell_y-1:
                grid_y1 = self.model.actualGame.nbr_cell_y-1
            if grid_y2 > self.model.actualGame.nbr_cell_y-1:
                grid_y2 = self.model.actualGame.nbr_cell_y-1

            pattern = 0
            if grid_x1 > grid_x2:
                pattern += 1

            if grid_y1 > grid_y2:
                pattern += 2

            if self.model.actualGame.map[grid_x1][grid_y1].sprite not in list_of_undestructible and self.model.actualGame.map[grid_x2][grid_y2].sprite not in list_of_undestructible:

                match(pattern):
                    case 0:
                        for xi in range(grid_x1, grid_x2+1):
                            if self.model.actualGame.map[xi][grid_y2].road == None and self.model.actualGame.map[xi][grid_y2].structure == None and self.model.actualGame.map[xi][grid_y2].sprite not in list_of_collision:
                                Route(self.model.actualGame.map[xi][grid_y2], self.model.actualGame)

                        for yi in range(grid_y1, grid_y2+1):
                            if self.model.actualGame.map[grid_x1][yi].road == None and self.model.actualGame.map[grid_x1][yi].structure == None and self.model.actualGame.map[grid_x1][yi].sprite not in list_of_collision:
                                Route(self.model.actualGame.map[grid_x1][yi], self.model.actualGame)
                    case 1:
                        for xi in range(grid_x1, grid_x2-1, -1):
                            if self.model.actualGame.map[xi][grid_y1].road == None and self.model.actualGame.map[xi][grid_y1].structure == None and self.model.actualGame.map[xi][grid_y1].sprite not in list_of_collision:
                                Route(self.model.actualGame.map[xi][grid_y1], self.model.actualGame)
                        for yi in range(grid_y1, grid_y2+1):
                            if self.model.actualGame.map[grid_x2][yi].road == None and self.model.actualGame.map[grid_x2][yi].structure == None and self.model.actualGame.map[grid_x2][yi].sprite not in list_of_collision:
                                Route(self.model.actualGame.map[grid_x2][yi], self.model.actualGame)
                    case 2:
                        for xi in range(grid_x1, grid_x2+1):
                            if self.model.actualGame.map[xi][grid_y1].road == None and self.model.actualGame.map[xi][grid_y1].structure == None and self.model.actualGame.map[xi][grid_y1].sprite not in list_of_collision:
                                Route(self.model.actualGame.map[xi][grid_y1], self.model.actualGame)
                        for yi in range(grid_y1, grid_y2-1, -1):
                            if self.model.actualGame.map[grid_x2][yi].road == None and self.model.actualGame.map[grid_x2][yi].structure == None and self.model.actualGame.map[grid_x2][yi].sprite not in list_of_collision:
                                Route(self.model.actualGame.map[grid_x2][yi], self.model.actualGame)
                    case 3:
                        for xi in range(grid_x1, grid_x2-1, -1):
                            if self.model.actualGame.map[xi][grid_y2].road == None and self.model.actualGame.map[xi][grid_y2].structure == None and self.model.actualGame.map[xi][grid_y2].sprite not in list_of_collision:
                                Route(self.model.actualGame.map[xi][grid_y2], self.model.actualGame)
                        for yi in range(grid_y1, grid_y2-1, -1):
                            if self.model.actualGame.map[grid_x1][yi].road == None and self.model.actualGame.map[grid_x1][yi].structure == None and self.model.actualGame.map[grid_x1][yi].sprite not in list_of_collision:
                                Route(self.model.actualGame.map[grid_x1][yi], self.model.actualGame)
                            
            self.model.actualGame.collision_matrix = self.model.actualGame.create_collision_matrix()
            
        #Buildings
        #HousingSpot
        if self.model.actualGame.controls.build_housing_button.clicked and not self.model.actualGame.controls.build_housing_button.rect.collidepoint((event.pos[0] - 1758.0, event.pos[1] - 24)):
        
        #Mouse Selection :
            x, y = self.initialMouseCoordinate
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x1 = int(cart_x // cell_size)
            grid_y1 = int(cart_y // cell_size)

            x, y = event.pos
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x2 = int(cart_x // cell_size)
            grid_y2 = int(cart_y // cell_size)
        
            if grid_x1 <0:
                grid_x1 = 0
            if grid_x2 <0:
                grid_x2 = 0
            if grid_y1 <0:
                grid_y1 = 0
            if grid_y2 <0:
                grid_y2 = 0

            if grid_x1 > self.model.actualGame.nbr_cell_x-1:
                grid_x1 = self.model.actualGame.nbr_cell_x-1
            if grid_x2 > self.model.actualGame.nbr_cell_x-1:
                grid_x2 = self.model.actualGame.nbr_cell_x-1
            if grid_y1 > self.model.actualGame.nbr_cell_y-1:
                grid_y1 = self.model.actualGame.nbr_cell_y-1
            if grid_y2 > self.model.actualGame.nbr_cell_y-1:
                grid_y2 = self.model.actualGame.nbr_cell_y-1

            if grid_x1 > grid_x2:
                temp = grid_x1
                grid_x1 = grid_x2
                grid_x2 = temp

            if grid_y1 > grid_y2:
                temp = grid_y1
                grid_y1 = grid_y2
                grid_y2 = temp

            #Building Construction :
            for xi in range(grid_x1, grid_x2+1):
                for yi in range(grid_y1, grid_y2+1):
                        for xcr in range (xi-2,xi+3,1) :
                            for ycr in range (yi-2,yi+3,1) :
                                if 0<=xcr<self.model.actualGame.nbr_cell_x and 0<=ycr<self.model.actualGame.nbr_cell_y:
                                    if not self.model.actualGame.map[xi][yi].road and not self.model.actualGame.map[xi][yi].structure and self.model.actualGame.map[xi][yi].sprite not in list_of_collision:
                                        if self.model.actualGame.map[xcr][ycr].road :
                                            HousingSpot(self.model.actualGame.map[xi][yi],self.model.actualGame)

        #Prefecture     
        if self.model.actualGame.controls.security_structures.clicked and not self.model.actualGame.controls.security_structures.rect.collidepoint((event.pos[0] - 1758.0, event.pos[1] - 24)):
        
        #Mouse Selection :
            x, y = self.initialMouseCoordinate
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x1 = int(cart_x // cell_size)
            grid_y1 = int(cart_y // cell_size)

            x, y = event.pos
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x2 = int(cart_x // cell_size)
            grid_y2 = int(cart_y // cell_size)
        
            if grid_x1 <0:
                grid_x1 = 0
            if grid_x2 <0:
                grid_x2 = 0
            if grid_y1 <0:
                grid_y1 = 0
            if grid_y2 <0:
                grid_y2 = 0

            if grid_x1 > self.model.actualGame.nbr_cell_x-1:
                grid_x1 = self.model.actualGame.nbr_cell_x-1
            if grid_x2 > self.model.actualGame.nbr_cell_x-1:
                grid_x2 = self.model.actualGame.nbr_cell_x-1
            if grid_y1 > self.model.actualGame.nbr_cell_y-1:
                grid_y1 = self.model.actualGame.nbr_cell_y-1
            if grid_y2 > self.model.actualGame.nbr_cell_y-1:
                grid_y2 = self.model.actualGame.nbr_cell_y-1

            if grid_x1 > grid_x2:
                temp = grid_x1
                grid_x1 = grid_x2
                grid_x2 = temp

            if grid_y1 > grid_y2:
                temp = grid_y1
                grid_y1 = grid_y2
                grid_y2 = temp

            #Building Construction :
            for xi in range(grid_x1, grid_x2+1):
                for yi in range(grid_y1, grid_y2+1):
                    if self.model.actualGame.map[xi][yi].getConnectedToRoad() > 0 :
                        if not self.model.actualGame.map[xi][yi].road and not self.model.actualGame.map[xi][yi].structure and self.model.actualGame.map[xi][yi].sprite not in list_of_collision:
                            Prefecture(self.model.actualGame.map[xi][yi],self.model.actualGame,(1,1),"Prefecture",1)

        #Engineer
        if self.model.actualGame.controls.engineering_structures.clicked and not self.model.actualGame.controls.engineering_structures.rect.collidepoint((event.pos[0] - 1758.0, event.pos[1] - 24)):
        
        #Mouse Selection :
            x, y = self.initialMouseCoordinate
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x1 = int(cart_x // cell_size)
            grid_y1 = int(cart_y // cell_size)

            x, y = event.pos
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x2 = int(cart_x // cell_size)
            grid_y2 = int(cart_y // cell_size)
        
            if grid_x1 <0:
                grid_x1 = 0
            if grid_x2 <0:
                grid_x2 = 0
            if grid_y1 <0:
                grid_y1 = 0
            if grid_y2 <0:
                grid_y2 = 0

            if grid_x1 > self.model.actualGame.nbr_cell_x-1:
                grid_x1 = self.model.actualGame.nbr_cell_x-1
            if grid_x2 > self.model.actualGame.nbr_cell_x-1:
                grid_x2 = self.model.actualGame.nbr_cell_x-1
            if grid_y1 > self.model.actualGame.nbr_cell_y-1:
                grid_y1 = self.model.actualGame.nbr_cell_y-1
            if grid_y2 > self.model.actualGame.nbr_cell_y-1:
                grid_y2 = self.model.actualGame.nbr_cell_y-1

            if grid_x1 > grid_x2:
                temp = grid_x1
                grid_x1 = grid_x2
                grid_x2 = temp

            if grid_y1 > grid_y2:
                temp = grid_y1
                grid_y1 = grid_y2
                grid_y2 = temp

            #Building Construction :
            for xi in range(grid_x1, grid_x2+1):
                for yi in range(grid_y1, grid_y2+1):
                    if self.model.actualGame.map[xi][yi].getConnectedToRoad() > 0 :
                        if not self.model.actualGame.map[xi][yi].road and not self.model.actualGame.map[xi][yi].structure and self.model.actualGame.map[xi][yi].sprite not in list_of_collision:
                            EnginnerPost(self.model.actualGame.map[xi][yi],self.model.actualGame,(1,1),"EngineerPost",1)

        #Well
        if self.model.actualGame.controls.water_related_structures.clicked and not self.model.actualGame.controls.water_related_structures.rect.collidepoint((event.pos[0] - 1758.0, event.pos[1] - 24)):
        #Mouse Selection :
            x, y = self.initialMouseCoordinate
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x1 = int(cart_x // cell_size)
            grid_y1 = int(cart_y // cell_size)

            x, y = event.pos
            world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
            world_y = y - self.model.actualGame.camera.vect.y

            cart_y = (2 * world_y - world_x) / 2
            cart_x = cart_y + world_x
            grid_x2 = int(cart_x // cell_size)
            grid_y2 = int(cart_y // cell_size)
        
            if grid_x1 <0:
                grid_x1 = 0
            if grid_x2 <0:
                grid_x2 = 0
            if grid_y1 <0:
                grid_y1 = 0
            if grid_y2 <0:
                grid_y2 = 0

            if grid_x1 > self.model.actualGame.nbr_cell_x-1:
                grid_x1 = self.model.actualGame.nbr_cell_x-1
            if grid_x2 > self.model.actualGame.nbr_cell_x-1:
                grid_x2 = self.model.actualGame.nbr_cell_x-1
            if grid_y1 > self.model.actualGame.nbr_cell_y-1:
                grid_y1 = self.model.actualGame.nbr_cell_y-1
            if grid_y2 > self.model.actualGame.nbr_cell_y-1:
                grid_y2 = self.model.actualGame.nbr_cell_y-1

            if grid_x1 > grid_x2:
                temp = grid_x1
                grid_x1 = grid_x2
                grid_x2 = temp

            if grid_y1 > grid_y2:
                temp = grid_y1
                grid_y1 = grid_y2
                grid_y2 = temp

            #Building Construction :
            for xi in range(grid_x1, grid_x2+1):
                for yi in range(grid_y1, grid_y2+1):
                    #for xcr in range (xi-1,xi+1,1) :
                        #for ycr in range (yi-1,yi+1,1) :
                            #if self.model.actualGame.map[xcr][ycr].getConnectedToRoad() > 0 :
                                if not self.model.actualGame.map[xi][yi].road and not self.model.actualGame.map[xi][yi].structure and self.model.actualGame.map[xi][yi].sprite not in list_of_collision:
                                    Well(self.model.actualGame.map[xi][yi],self.model.actualGame,"Well")
                                    
        #Overlay part
        #Fire
        if self.model.actualGame.controls.overlays_button.clicked:
            self.model.actualGame.foreground.initOverlayGrid()
            for x in range(40):
                for y in range(40):
                    if isinstance(self.model.map[x][y], Building):
                        self.model.actualGame.foreground.addOverlayInfo("risk", self.model.map[x][y].get_fireRisk())
                    

    def mousePosToGridPos(self, mousePos):
        x, y = mousePos
        world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
        world_y = y - self.model.actualGame.camera.vect.y

        cart_y = (2 * world_y - world_x) / 2
        cart_x = cart_y + world_x
        grid_x1 = int(cart_x // cell_size)
        grid_y1 = int(cart_y // cell_size)

        if grid_x1 <0:
            grid_x1 = 0
        
        if grid_y1 <0:
            grid_y1 = 0
   
        if grid_x1 > self.model.actualGame.nbr_cell_x-1:
            grid_x1 = self.model.actualGame.nbr_cell_x-1
        if grid_y1 > self.model.actualGame.nbr_cell_y-1:
            grid_y1 = self.model.actualGame.nbr_cell_y-1
        return (grid_x1, grid_y1)

    def handleMouseMouvement(self, event):
        """ Here we are going to manage the movement of the mouse"""
        #Pelle
        if self.clicked:
            if self.model.actualGame.controls.clear_land_button.clicked and not self.model.actualGame.controls.clear_land_button.rect.collidepoint(event.pos) and self.initialMouseCoordinate != None:
                self.model.actualGame.foreground.initForegroundGrid()

                x, y = self.initialMouseCoordinate
                world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
                world_y = y - self.model.actualGame.camera.vect.y

                cart_y = (2 * world_y - world_x) / 2
                cart_x = cart_y + world_x
                grid_x1 = int(cart_x // cell_size)
                grid_y1 = int(cart_y // cell_size)

                x, y = event.pos
                world_x = x - self.model.actualGame.camera.vect.x - self.model.actualGame.surface_cells.get_width() / 2
                world_y = y - self.model.actualGame.camera.vect.y

                cart_y = (2 * world_y - world_x) / 2
                cart_x = cart_y + world_x
                grid_x2 = int(cart_x // cell_size)
                grid_y2 = int(cart_y // cell_size)
            
                if grid_x1 <0:
                    grid_x1 = 0
                if grid_x2 <0:
                    grid_x2 = 0
                if grid_y1 <0:
                    grid_y1 = 0
                if grid_y2 <0:
                    grid_y2 = 0

                if grid_x1 > self.model.actualGame.nbr_cell_x-1:
                    grid_x1 = self.model.actualGame.nbr_cell_x-1
                if grid_x2 > self.model.actualGame.nbr_cell_x-1:
                    grid_x2 = self.model.actualGame.nbr_cell_x-1
                if grid_y1 > self.model.actualGame.nbr_cell_y-1:
                    grid_y1 = self.model.actualGame.nbr_cell_y-1
                if grid_y2 > self.model.actualGame.nbr_cell_y-1:
                    grid_y2 = self.model.actualGame.nbr_cell_y-1

                if grid_x1 > grid_x2:
                    temp = grid_x1
                    grid_x1 = grid_x2
                    grid_x2 = temp

                if grid_y1 > grid_y2:
                    temp = grid_y1
                    grid_y1 = grid_y2
                    grid_y2 = temp

                for xi in range(grid_x1, grid_x2+1):
                    for yi in range(grid_y1, grid_y2+1):
                        self.model.actualGame.foreground.addEffect(xi, yi, 'red')
        else:
            self.model.actualGame.foreground.initForegroundGrid()
            (x, y) = self.mousePosToGridPos(event.pos)
            self.model.actualGame.foreground.addEffect(x, y, 'default')