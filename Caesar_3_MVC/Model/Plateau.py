import pygame
from Model.Zoom import Zoom
from Model.Camera import Camera
from Model.Case import Case
from View.Menu_map import Menu_map
from Model.Walker import *
from Model.control_panel import *
from Model.constants import *
from Model.Route import Route
from Model.Buildings.Building import Building
from Model.Buildings.House import House
from Model.Buildings.House import HousingSpot
from Model.Buildings.WorkBuilding import *
from Model.Controls import Controls
from Model.TopBar import TopBar
from Model.Foreground import Foreground
from random import *

counter=1

class Plateau():
    def __init__(self, screen, clock, name, heigth, width, nbr_cell_x=40, nbr_cell_y=40, attractiveness=0, listeCase=[], entities = [], structures = [], cityHousesList = [], cityHousingSpotsList = [], burningBuildings = []):
        
        self.screen = screen
        self.clock = clock
        self.minimalFont = pygame.font.SysFont(None, 20)
        self.width, self.height = self.screen.get_size()
        self.camera = Camera(self.width, self.height)
        self.running = True
        self.zoomed = True
        self.menu_map = Menu_map(self.width,self.height)

        self.name = name
        self.heigthScreen = heigth
        self.widthScreen = width
        self.nbr_cell_x = nbr_cell_x
        self.nbr_cell_y = nbr_cell_y

        self.surface_cells = pygame.Surface((nbr_cell_x * cell_size * 2, nbr_cell_y * cell_size  + 2 * cell_size )).convert_alpha()
        

        #Load de tous les spirtes
        self.image = self.load_cases_images()
        self.image_route = self.load_routes_images()
        self.image_walkers = self.load_walkers_images()
        self.image_structures = self.load_structures_images()

        self.zoom__=Zoom(self.image)

        self.attractiveness = attractiveness
        self.listeCase = listeCase
        #Trésorerie
        self.treasury = START_TREASURY + self.nbr_cell_y * ROAD_COST    #Remboursement auto des routes par défaut
        #Population
        self.population = 0

        self.map = self.default_map()
        self.foreground = Foreground(self.screen, self.nbr_cell_x, self.nbr_cell_y)
        self.default_road()

        #Tableau contenant toutes les cases occupées par les walkers
        self.walkers = [[[] for x in range(self.nbr_cell_x)] for y in range(self.nbr_cell_y)]

        #Tableau contenant l'intégralité des walker présents sur la map
        self.entities = entities 

        #Tableau des collisions de la map (pour le moment la map ne contient pas de collision)
        self.collision_matrix = self.create_collision_matrix()

        #Tableau contenant l'intégralité des bâtiments présent sur la map
        self.structures = structures
        self.cityHousesList = cityHousesList
        self.cityHousingSpotsList = cityHousingSpotsList
        self.burningBuildings = burningBuildings
        
        # Variable speed feature
        self.currentSpeed = 100

        # Left menu in game
        self.controls = Controls(self.screen, self.minimalFont, self.currentSpeed, self.increaseSpeed, self.decreaseSpeed)

        # Top menu in game
        self.topbar = TopBar(self.screen, self.treasury, self.population)


        #Define the position of the button on the full panel button who won't change position after
        # fire_overlay.change_pos(self.width-fire_overlay.dim[0]-hide_control_panel_button.dim[0]-150,27)
        # damage_overlay.change_pos(self.width-damage_overlay.dim[0]-hide_control_panel_button.dim[0]-150,52)
        # entertainment_overlay.change_pos(self.width-entertainment_overlay.dim[0]-hide_control_panel_button.dim[0]-150,77)
        # water_overlay.change_pos(self.width-water_overlay.dim[0]-hide_control_panel_button.dim[0]-150,102)
        
        # overlays_button.change_pos(self.width-overlays_button.dim[0]-hide_control_panel_button.dim[0]-10,27)
        # hide_control_panel_button.change_pos(self.width-hide_control_panel_button.dim[0]-4,24+5)
        # advisors_button.change_pos(self.width-155,179)
        # empire_map_button.change_pos(self.width-78,179)
        # assignement_button.change_pos(self.width-155,208)
        # compass_button.change_pos(self.width-116,208)
        # arrow_rotate_counterclockwise.change_pos(self.width-78,208)
        # arrow_rotate_clockwise.change_pos(self.width-39,208)                
        # undo_button.change_pos(self.width-149,445)
        # message_view_button.change_pos(self.width-99,445)
        # see_recent_troubles_button.change_pos(self.width-49,445)

        self.pause = False
        self.restart = False
        global counter
        counter = 1
        self.riviere()




    def default_map(self):

        map = []

        for cell_x in range(self.nbr_cell_x):
            map.append([])
            for cell_y in range(self.nbr_cell_y):
                cells_to_map = self.cells_to_map(cell_x, cell_y)
                map[cell_x].append(cells_to_map)
                render_pos = cells_to_map.render_pos
                self.surface_cells.blit(self.image["land2"], (render_pos[0] + self.surface_cells.get_width()/2, render_pos[1]))
        return map

    def default_road(self):
        for j in range(19, 20):
            for i in range(self.nbr_cell_y):
                Route(self.map[j][i], self)
        
    def cells_to_map(self, cell_x, cell_y):

        rectangle_cell = [
            (cell_x * cell_size , cell_y * cell_size ),
            (cell_x * cell_size  + cell_size , cell_y * cell_size ),
            (cell_x * cell_size  + cell_size , cell_y * cell_size  + cell_size ),
            (cell_x * cell_size , cell_y * cell_size  + cell_size )
        ]

        isometric_cell = [self.cartesian_to_isometric(x, y) for x, y in rectangle_cell]

        sprite=self.choose_image()
        nouvelle_case = Case(cell_x, cell_y, rectangle_cell, isometric_cell, [min([x for x, y in isometric_cell]), min([y for x, y in isometric_cell])], sprite = sprite)
        if sprite.startswith("path"):
            nouvelle_case.sprite = "land1"
            Route(nouvelle_case, self)
        return nouvelle_case
        
    def cartesian_to_isometric(self, x, y):
            return x - y,(x + y)/2

    def zoom(self,X__,bol):
        if bol:
            global cell_size
            global counter
            counter=1
            cell_size *= X__
            self.zoom__.set_zoom(X__)
            self.surface_cells.fill((0,0,0))
            self.surface_cells = pygame.Surface((self.nbr_cell_x * cell_size * 2, self.nbr_cell_y * cell_size + 2 * cell_size)).convert_alpha()
            self.map=self.default_map()

    def set_self_num(self):
        self.num=1
    def choose_image(self):
        image=""
        global counter
        if counter<=1600:

            if (counter>=1 and counter<=10) or(counter>=41 and counter<=50)or(counter>=201 and counter<=207)or (counter>=281 and counter<=286)or(counter>=361 and counter<=364)or (counter>=441 and counter<=443)or (counter>=481 and counter<=483)or (counter>=561 and counter<=562)or (counter>=641 and counter<=642) or (counter in range(21,41,1))or (counter in range(103,121,1))or (counter in range(185,201,1))or (counter in range(267,281,1))or (counter in range(349,361,1))or (counter==1200)or (counter in range(1155,1161,1))or (counter in range(1115,1121))or (counter in range(1075,1081))or (counter==1040):
                image = "tree2"
            elif (counter>=121 and counter<=129)or(counter>=161 and counter<=168)or(counter>=81 and counter<=89) or (counter>=241 and counter<=246)or(counter>=321 and counter<=324) or (counter>=401 and counter<=404)or (counter>=521 and counter<=522)or (counter>=601 and counter<=602)or (counter in range(62,81,1))or (counter in range(144,161,1))or (counter in range(226,241,1))or (counter in range(308,321,1))or (counter in range(390,401,1))or (counter==1440)or (counter in range(1395,1401,1))or (counter in range(1355,1361,1))or (counter in range(1315,1321,1))or (counter in range(1276,1281,1))or (counter==1240):
                image = "tree1"
            elif (counter >= 761 and counter<=800):
                image = "land1" # route
            elif (counter == 721):
                image = "sign2"
            elif (counter == 760):
                image = "sign1"
            elif (counter>=14 and counter<=19) or(counter>=55 and counter<=60)or(counter>=96 and counter<=101)or(counter>=137 and counter<=142)or(counter>=178 and counter<=183)or(counter>=219 and counter<=224)or(counter>=260 and counter<=265)or(counter>=301 and counter<=306)or(counter>=342 and counter<=347)or(counter>=383 and counter<=388)or(counter>=424 and counter<=429)or(counter>=465 and counter<=480)or(counter>=506 and counter<=520)or(counter>=547 and counter<=560)or(counter>=588 and counter<=600)or(counter>=629 and counter<=640)or(counter<=1573 and counter>=1569)or(counter<=1533 and counter>=1529)or(counter<=1493 and counter>=1489)or(counter<=1453 and counter>=1449)or(counter<=1413 and counter>=1409)or(counter<=1373 and counter>=1369)or(counter<=1333 and counter>=1329)or(counter<=1293 and counter>=1281)or(counter<=1253 and counter>=1241)or(counter<=1213 and counter>=1201)or(counter<=1173 and counter>=1161):
                image = "water1"
            elif (counter==20) or (counter==61)or(counter==102)or(counter==143)or(counter==184)or(counter==225)or(counter==266)or(counter==307)or(counter==348)or(counter==389)or(counter>=430 and counter<=440 )or(counter<=1133 and counter>=1121):
                image="water1"
            elif (counter>=669 and counter<=680)or counter==628 or counter==587 or counter==546 or counter==505 or counter==464 or counter==423 or counter==382 or counter==341 or counter==300 or counter==259 or counter==218 or counter==177 or counter==136 or counter==95 or counter==54 or counter==13 or(counter<=1328 and counter>=1321):
                image = "water1"
            elif (counter==1574)or(counter==1534)or(counter==1494)or(counter==1454)or(counter==1414)or(counter==1374)or(counter==1334)or(counter==1294)or(counter==1254)or(counter==1214)or(counter==1174)or(counter==1134):
                image="water1"
            elif (counter==1568)or(counter==1528)or(counter==1488)or(counter==1448)or(counter==1408)or(counter==1368):
                image="water1"
            elif (counter==1590)or(counter==1549)or(counter==1508)or(counter==1467)or(counter==1426)or(counter==1385)or(counter==1384)or(counter==1343)or(counter==1302) or (counter==1298)or (counter==1600)or (counter==1337)or (counter==1376)or (counter==1415)or (counter==1455)or (counter==1495)or (counter==1535)or (counter==1575)or (counter in range(1575,1591)):
                image = "rock1"
            elif (counter==1262) or (counter==1520):
                image="rock2"
            elif (counter in range(681,721,1))or(counter in range(722,760,1)) or(counter in range(681+40*3,720+40*4+1,1)):
                image="tree3"
            elif counter in range(720+40*4,1600,20):
                image="rock3"
            elif counter in range(1,680,20):
                image="rock3"
            else:
                image="land1"
            counter+=1
        return image

    def load_cases_images(self):


        land1 = pygame.image.load("image/C3/Land1a_00116.png").convert_alpha()
        land1 = pygame.transform.scale(land1,(land1.get_width()/2,land1.get_height()/2))
        land2 = pygame.image.load("image/C3/Land1a_00265.png").convert_alpha()
        land2 = pygame.transform.scale(land2, (land2.get_width() / 2, land2.get_height() / 2))



        tree1 = pygame.image.load("image/C3/Land1a_00059.png").convert_alpha()
        tree1 = pygame.transform.scale(tree1,(tree1.get_width()/2,tree1.get_height()/2))
        tree2 = pygame.image.load("image/C3/Land1a_00061.png").convert_alpha()
        tree2 = pygame.transform.scale(tree2, (tree2.get_width() / 2, tree2.get_height() / 2))
        tree3 = pygame.image.load("image/C3/Land1a_00039.png").convert_alpha()
        tree3 = pygame.transform.scale(tree3, (tree3.get_width() / 2, tree3.get_height() / 2))



        rock1 = pygame.image.load("image/C3/Land1a_00292.png").convert_alpha()
        rock1 = pygame.transform.scale(rock1, (rock1.get_width() / 2, rock1.get_height() / 2))
        rock2 = pygame.image.load("image/C3/land3a_00084.png").convert_alpha()
        rock2 = pygame.transform.scale(rock2, (rock2.get_width() / 2, rock2.get_height() / 2))
        rock3 = pygame.image.load("image/C3/Land1a_00223.png").convert_alpha()
        rock3 = pygame.transform.scale(rock3, (rock3.get_width() / 2, rock3.get_height() / 2))


        sign1 = pygame.image.load("image/C3/land3a_00089.png").convert_alpha()
        sign1 = pygame.transform.scale(sign1, (sign1.get_width() / 2, sign1.get_height() / 2))
        sign2 = pygame.image.load("image/C3/land3a_00087.png").convert_alpha()
        sign2 = pygame.transform.scale(sign2, (sign2.get_width() / 2, sign2.get_height() / 2))

        water1 = pygame.image.load("image/C3/Land1a_00122.png").convert_alpha()
        water1 = pygame.transform.scale(water1, (water1.get_width() / 2, water1.get_height() / 2))
        water2 = pygame.image.load("image/Water/wdown.png").convert_alpha()
        water2 = pygame.transform.scale(water2, (water2.get_width() / 2, water2.get_height() / 2))
        water3 = pygame.image.load("image/Water/wup.png").convert_alpha()
        water3 = pygame.transform.scale(water3, (water3.get_width() / 2, water3.get_height() / 2))
        water4 = pygame.image.load("image/Water/wleft.png").convert_alpha()
        water4 = pygame.transform.scale(water4, (water4.get_width() / 2, water4.get_height() / 2))
        water5 = pygame.image.load("image/Water/wright.png").convert_alpha()
        water5 = pygame.transform.scale(water5, (water5.get_width() / 2, water5.get_height() / 2))
        water6=pygame.image.load("image/Water/wdowncorner.png").convert_alpha()
        water6 = pygame.transform.scale(water6, (water6.get_width() / 2, water6.get_height() / 2))
        water7=pygame.image.load("image/Water/wupcorner.png").convert_alpha()
        water7 = pygame.transform.scale(water7, (water7.get_width() / 2, water7.get_height() / 2))
        water8 = pygame.image.load("image/Water/wleftcorner.png").convert_alpha()
        water8 = pygame.transform.scale(water8, (water8.get_width() / 2, water8.get_height() / 2))
        water9 = pygame.image.load("image/Water/wrightcorner.png").convert_alpha()
        water9 = pygame.transform.scale(water9, (water9.get_width() / 2, water9.get_height() / 2))
        water10 = pygame.image.load("image/Water/wdownw.png").convert_alpha()
        water10 = pygame.transform.scale(water10, (water10.get_width() / 2, water10.get_height() / 2))
        water11 = pygame.image.load("image/Water/wupw.png").convert_alpha()
        water11 = pygame.transform.scale(water11, (water11.get_width() / 2, water11.get_height() / 2))
        water12 = pygame.image.load("image/Water/wleftw.png").convert_alpha()
        water12 = pygame.transform.scale(water12, (water12.get_width() / 2, water12.get_height() / 2))
        water13 = pygame.image.load("image/Water/wrightw.png").convert_alpha()
        water13 = pygame.transform.scale(water13, (water13.get_width() / 2, water13.get_height() / 2))



        red = pygame.image.load("image/C3/red.png").convert_alpha()
        red = pygame.transform.scale(red, (red.get_width() / 2, red.get_height() / 2)) 

        return {"land1": land1,"land2": land2, "tree1": tree1,"tree2": tree2,
                "tree3": tree3,"rock1": rock1,"rock2": rock2,"water1":water1,"water2":water2,"water3":water3,"water4":water4,"water5":water5,"water6":water6,
                "water7": water7,"water8":water8,"water9":water9,'water10':water10,'water11':water11,'water12':water12,'water13':water13,
                "sign1":sign1,"sign2":sign2,
               "rock3":rock3, "red":red
                }
    def load_routes_images(self):
        
        west = load_image("image/Routes/Land2a_00104.png")
        east = load_image("image/Routes/Land2a_00102.png")
        east_west = load_image("image/Routes/Land2a_00094.png")
        south = load_image("image/Routes/Land2a_00101.png")
        south_west = load_image("image/Routes/Land2a_00100.png")
        south_east = load_image("image/Routes/Land2a_00097.png")
        south_east_west = load_image("image/Routes/Land2a_00109.png")
        north = load_image("image/Routes/Land2a_00105.png")
        north_west = load_image("image/Routes/Land2a_00099.png")
        north_south = load_image("image/Routes/Land2a_00095.png")
        north_south_west = load_image("image/Routes/Land2a_00108.png")
        north_east = load_image("image/Routes/Land2a_00098.png")
        north_east_west = load_image("image/Routes/Land2a_00107.png")
        north_south_east = load_image("image/Routes/Land2a_00106.png")
        north_south_east_west = load_image("image/Routes/Land2a_00110.png")

        return {0: north, 1: west, 2: south, 3: south_west, 4: east, 5: east_west, 6: south_east,
                7: south_east_west, 8: north, 9: north_west, 10: north_south, 11: north_south_west,
                12: north_east, 13: north_east_west, 14: north_south_east, 15: north_south_east_west}
    def load_walkers_images(self):
        """walker_sprite[Type_Walker(String)][Action(Int)][Direction(Int)]""" #Directions : 1 -> North  2 -> East   3 -> South  4 -> West

        #====== Citizens ======#
        citizen = {1 : create_liste_sprites_walker("Citizen", "Walk", 12)}

        #====== Prefet ======#
        prefet = {1 : create_liste_sprites_walker("Prefet", "Walk", 12), 2 : create_liste_sprites_walker("Prefet", "FarmerWalk", 12), 3 : create_liste_sprites_walker("Prefet", "Throw", 6)}

        #====== Immigrant ======#
        immigrant = {1 : create_liste_sprites_walker("Immigrant", "Walk", 12)}

        #====== Chariot ======#
        chariot = {1 : create_liste_sprites_walker("Chariot", "Walk", 1)}

        #====== engineer ======#
        engineer = {1 : create_liste_sprites_walker("Engineer", "Walk", 12)}

        return {"Citizen" : citizen, "Prefet" : prefet, "Immigrant" : immigrant, "Chariot" : chariot, "Engineer" : engineer}
    def load_structures_images(self):

        hss = load_image("image/Buildings/Housng1a_00045.png")
        st1s = load_image("image/Buildings/Housng1a_00001.png")
        st2s = load_image("image/Buildings/Housng1a_00005.png")
        lt1s = load_image("image/Buildings/Housng1a_00004.png")
        lt2s = load_image("image/Buildings/Housng1a_00006.png")
        ps = load_image("image/Buildings/Security_00001.png")
        eps = load_image("image/Buildings/transport_00056.png")
        ws = load_image("image/Buildings/Utilitya_00001.png")
        bsts = list(load_image(f"image/Buildings/BurningBuilding/BurningBuildingFrame{i}.png") for i in range(1, 9))
        burnruinss = load_image("image/Buildings/BurningBuilding/Land2a_00187.png")
        ruinss = load_image("image/Buildings/Land2a_00044.png")

        return {"HousingSpot" : hss, "SmallTent" : st1s, "SmallTent2" : st2s, "LargeTent" : lt1s, "LargeTent2" : lt2s, "Prefecture" : ps, "EngineerPost" : eps, "Well" : ws, 
                "BurningBuilding" : bsts, "Ruins" : ruinss, "BurnedRuins" : burnruinss}
    
    def increaseSpeed(self):
        if self.currentSpeed >= 0 and self.currentSpeed < 100:
            self.currentSpeed += 10 
    
    def decreaseSpeed(self):
        if self.currentSpeed > 0:
            self.currentSpeed -= 10 

    def update(self):
        if self.restart:

            self.entities.clear()
            self.listeCase.clear()
            self.structures.clear()
            self.cityHousesList.clear()
            self.cityHousingSpotsList.clear()
            self.burningBuildings.clear()

        if not self.pause:
            self.camera.update()
            self.controls.update(self.currentSpeed)
            self.topbar.update(self.treasury, self.population)

            #Update de la position des walkers
            for e in self.entities: e.update()
            for hs in self.cityHousingSpotsList: hs.generateImmigrant()
            for bb in self.burningBuildings: bb.update()
            for b in self.structures :
                if isinstance(b,Building) : b.riskCheck()   # Vérifie et incrémente les risques d'incendies et d'effondrement
                if isinstance(b,WorkBuilding): b.delay()
                self.nearbyRoadsCheck(b)                    #Supprime les maisons/hs et désactive les wb s'il ne sont pas connectés à la route
            self.population = 0
            for h in self.cityHousesList:
                h.udmCheck()   # Vérifie les upgrades, downgrades et merge d'habitations
                self.population = self.population + h.nbHab


            
    def nearbyRoadsCheck(self, b):     #Supprime les maisons/hs et désactive les wb s'il ne sont pas connectés à la route
        for xcr in range (b.case.x-2,b.case.x+3,1) :
            for ycr in range (b.case.y-2,b.case.y+3,1) :
                    if 0<=xcr<self.nbr_cell_x and 0<=ycr<self.nbr_cell_y:
                        if self.map[xcr][ycr].road :
                            return
        if isinstance(b,HousingSpot) or isinstance(b,House) :
            b.delete()
        if isinstance(b,WorkBuilding) and b.active==True :
            b.active = False

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.surface_cells, (self.camera.vect.x, self.camera.vect.y))

       
       # DRAW CELLS

        for cell_x in range(self.nbr_cell_y):
            for cell_y in range(self.nbr_cell_y):
                render_pos =  self.map[cell_x][cell_y].render_pos
                id_image = self.map[cell_x][cell_y].sprite

                # DRAW DEFAULT CELLS
                if not self.map[cell_x][cell_y].road and not self.map[cell_x][cell_y].structure:
                    id_image = self.map[cell_x][cell_y].sprite

                    self.screen.blit(self.image[id_image],
                                    (render_pos[0] + self.surface_cells.get_width()/2 + self.camera.vect.x,
                                    render_pos[1] - (self.image[id_image].get_height() - cell_size) + self.camera.vect.y))
                # DRAW ROADS
                elif self.map[cell_x][cell_y].road:
                    id_image = self.map[cell_x][cell_y].road.sprite
                    self.screen.blit(self.image_route[id_image],
                                    (render_pos[0] + self.surface_cells.get_width()/2 + self.camera.vect.x,
                                    render_pos[1] - (self.image_route[id_image].get_height() - cell_size) + self.camera.vect.y))

                # DRAW STRUCTURES
                elif isinstance(self.map[cell_x][cell_y].structure, BurningBuilding):
                    self.screen.blit(self.image_structures["BurningBuilding"][int(self.map[cell_x][cell_y].structure.index_sprite)], 
                                    (render_pos[0] + self.surface_cells.get_width()/2 + self.camera.vect.x,
                                        render_pos[1] - (self.image_structures["BurningBuilding"][int(self.map[cell_x][cell_y].structure.index_sprite)].get_height() - cell_size) + self.camera.vect.y))
                                        
                elif self.map[cell_x][cell_y].structure.case == self.map[cell_x][cell_y] :
                    id_image = self.map[cell_x][cell_y].structure.desc
                    self.screen.blit(self.image_structures[id_image], 
                                        (render_pos[0] + self.surface_cells.get_width()/2 + self.camera.vect.x,
                                            render_pos[1] - (self.image_structures[id_image].get_height() - cell_size) + self.camera.vect.y))

                # DRAW PREVIEWED CELLS AND HOVERED CELLS
                if self.foreground.hasEffect(cell_x, cell_y):
                    id_image = self.map[cell_x][cell_y].sprite
                    effectedImage = self.foreground.getEffectedImage(self.image[id_image].copy(), cell_x, cell_y)
                    self.screen.blit(effectedImage,
                                    (render_pos[0] + self.surface_cells.get_width()/2 + self.camera.vect.x,
                                    render_pos[1] - (self.image[id_image].get_height() - cell_size) + self.camera.vect.y))

                # DRAW WALKERS
                for e in self.walkers[cell_x][cell_y]:
                    self.screen.blit(self.image_walkers[e.type][e.action][e.direction][int(e.index_sprite)], 
                                        (render_pos[0] + self.surface_cells.get_width()/2 + self.camera.vect.x,
                                         render_pos[1] - (self.image_walkers[e.type][e.action][e.direction][int(e.index_sprite)].get_height() - cell_size) + self.camera.vect.y))

        self.topbar.render()
        self.controls.render()
        
        fpsText = self.minimalFont.render(f"FPS: {self.clock.get_fps():.0f}", 1, (255, 255, 255), (0, 0, 0))
        self.screen.blit(fpsText, (0, self.screen.get_height() - fpsText.get_height()))

        # if state_control_panel=="reduced":
            
        #     self.screen.blit(small_gap_menu.img_scaled, (self.width-small_gap_menu.dim[0], 24))

            
        #     display_control_panel_button.update()
        #     display_control_panel_button.change_pos(self.width-display_control_panel_button.dim[0]-5,28)
        #     display_control_panel_button.draw(self.screen)

        #     build_housing_button.update()
        #     build_housing_button.change_pos(self.width-build_housing_button.dim[0]-1,24+32)
        #     build_housing_button.draw(self.screen)

        #     clear_land_button.update()
        #     clear_land_button.change_pos(self.width-clear_land_button.dim[0]-1,24+67)
        #     clear_land_button.draw(self.screen)

        #     build_roads_button.update()
        #     build_roads_button.change_pos(self.width-build_roads_button.dim[0]-1,24+102)
        #     build_roads_button.draw(self.screen)
            

        #     water_related_structures.update()
        #     water_related_structures.change_pos(self.width-water_related_structures.dim[0]-1,24+137)
        #     water_related_structures.draw(self.screen)
           
        #     health_related_structures.update()
        #     health_related_structures.change_pos(self.width-health_related_structures.dim[0]-1,24+172)
        #     health_related_structures.draw(self.screen)
           
        #     religious_structures.update()
        #     religious_structures.change_pos(self.width-religious_structures.dim[0]-1,24+207)
        #     religious_structures.draw(self.screen)
            
        #     education_structures.update()
        #     education_structures.change_pos(self.width-education_structures.dim[0]-1,24+242)
        #     education_structures.draw(self.screen)
            
        #     entertainment_structures.update()
        #     entertainment_structures.change_pos(self.width-entertainment_structures.dim[0]-1,24+277)
        #     entertainment_structures.draw(self.screen)
            
        #     administration_or_government_structures.update()
        #     administration_or_government_structures.change_pos(self.width-administration_or_government_structures.dim[0]-1,24+312)
        #     administration_or_government_structures.draw(self.screen)
            
        #     engineering_structures.update()
        #     engineering_structures.change_pos(self.width-engineering_structures.dim[0]-1,24+347)
        #     engineering_structures.draw(self.screen)
            
        #     security_structures.update()
        #     security_structures.change_pos(self.width-security_structures.dim[0]-1,24+382)
        #     security_structures.draw(self.screen)
            
        #     industrial_structures.update()
        #     industrial_structures.change_pos(self.width-industrial_structures.dim[0]-1,24+417)
        #     industrial_structures.draw(self.screen)


    def create_collision_matrix(self):
        collision_matrix = [[1000 for x in range(self.nbr_cell_x)] for y in range(self.nbr_cell_y)]

        #La suite sera pour quand on aura un système de collision
        for x in range(self.nbr_cell_x):
            for y in range(self.nbr_cell_y):
                if self.map[x][y].collision:
                    collision_matrix[y][x] = 0
                if self.map[x][y].road:
                    collision_matrix[y][x] = 1
        return collision_matrix

    def riviere(self):

        water_list = ['water1', 'water2', 'water3', 'water4', 'water5', 'water6','water7','water8','water9','water10','water11','water12','water13']
        for x in range(self.nbr_cell_y):
            for y in range(self.nbr_cell_y):

                if self.map[x][y].sprite in water_list:
                    d,g,h,b=(None,None,None,None)
                    if x != 0 and y != 0 and x != 39 and y != 39:

                        g=self.map[x-1][y].sprite
                        d=self.map[x+1][y].sprite
                        h=self.map[x][y-1].sprite
                        b=self.map[x][y+1].sprite
                    else:

                        if x == 0 and y != 0:
                            g='water1'
                            d = self.map[x+1][y].sprite
                            h = self.map[x][y-1].sprite
                            b = self.map[x][y+1].sprite
                        if y == 0 and x != 0:

                            h = 'water1'
                            g = self.map[x - 1][y].sprite
                            d = self.map[x + 1][y].sprite
                            b = self.map[x][y + 1].sprite



                        if x == 39 and y != 39:


                            d = 'water1'
                            g = self.map[x - 1][y].sprite
                            h = self.map[x][y - 1].sprite
                            b = self.map[x][y + 1].sprite



                        if y == 39 and x != 39:
                            b = 'water1'
                            g = self.map[x - 1][y].sprite
                            d = self.map[x + 1][y].sprite
                            h = self.map[x][y - 1].sprite








                    if g in water_list:


                        if b not in water_list and  h  in water_list and d in water_list:
                            self.map[x][y].sprite='water4'
                        elif b  in water_list and  h  in water_list and d not in water_list:
                            self.map[x][y].sprite='water2'
                        elif b in water_list and  h not in water_list and d in water_list:
                            self.map[x][y].sprite='water5'
                        elif b not in water_list and  h in water_list and d not in water_list:
                            self.map[x][y].sprite='water6'
                        elif b in water_list and h not in water_list and d not in water_list:
                            self.map[x][y].sprite = 'water9'
                        elif h in water_list and  b not in water_list and d not in water_list:
                            self.map[x][y].sprite = 'water6'




                    elif g not in water_list:

                        if b in water_list and h in water_list and d in water_list:
                            self.map[x][y].sprite = 'water3'
                        elif b not in water_list and h in water_list and d in water_list:
                            self.map[x][y].sprite = 'water8'
                        elif d in water_list and b in water_list and h not in water_list:
                            self.map[x][y].sprite = 'water7'





        self.riviere2(water_list)
    def riviere2(self,water_list):

        for x in range(self.nbr_cell_y):
            for y in range(self.nbr_cell_y):

                if self.map[x][y].sprite in water_list:
                    d, g, h, b,hg,hd,bg,bd = (None, None, None, None,None,None,None,None)
                    if x != 0 and y != 0 and x != 39 and y != 39:

                        g = self.map[x-1][y].sprite
                        d = self.map[x+1][y].sprite
                        h = self.map[x][y-1].sprite
                        b = self.map[x][y+1].sprite
                        hg = self.map[x-1][y-1].sprite
                        hd = self.map[x+1][y-1].sprite
                        bg = self.map[x-1][y+1].sprite
                        bd = self.map[x+1][y+1].sprite
                    else:

                        if x == 0 and y != 0:
                            g='water1'
                            hg='water1'
                            bg='water1'
                            d = self.map[x+1][y].sprite
                            h = self.map[x][y-1].sprite
                            b = self.map[x][y+1].sprite

                        if y == 0 and x != 0:

                            h = 'water1'
                            hd='water1'
                            hg='water1'
                            g = self.map[x - 1][y].sprite
                            d = self.map[x + 1][y].sprite
                            b = self.map[x][y + 1].sprite



                        if x == 39 and y != 39:


                            d = 'water1'
                            hd='water1'
                            bd='water1'
                            g = self.map[x - 1][y].sprite
                            h = self.map[x][y - 1].sprite
                            b = self.map[x][y + 1].sprite



                        if y == 39 and x != 39:
                            b = 'water1'
                            bd='water1'
                            bg='water1'
                            g = self.map[x - 1][y].sprite
                            d = self.map[x + 1][y].sprite
                            h = self.map[x][y - 1].sprite

                    if  g != 'water1' and g in water_list  and b != 'water1' and b in water_list and h == 'water1' and d == 'water1' and bg not in water_list:
                        self.map[x][y].sprite = 'water12'


                    if g == 'water1' and b == 'water1' and h != 'water1' and h in water_list and d != 'water1' and d in water_list and hd not in water_list:
                        self.map[x][y].sprite = 'water13'

                    if d!='water1' and d in water_list and  b!='water1' and b in water_list and g =='water1' and h =='water1' and bd not in water_list:
                        self.map[x][y].sprite = 'water10'

                    if g!='water1' and g in water_list and  h!='water1' and h in water_list and d =='water1' and b =='water1' and hg not in water_list:
                        self.map[x][y].sprite = 'water11'




def load_image(path):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, (image.get_width() / 2, image.get_height() / 2))

def create_liste_sprites_walker(type, action, nb_frame):
    direction = {1 : "UpRight", 2 : "DownRight", 3 : "DownLeft", 4 : "UpLeft"}
    return {j : list(load_image(f"image/Walkers/{type}/{action}/{direction[j]}/{type}{action}{direction[j]}Frame{i}.png") for i in range(1, nb_frame+1)) for j in range(1, 5)}
