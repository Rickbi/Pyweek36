import pyxel
from time import perf_counter
from os.path import join, pardir
from os import getcwd

# pyxel.play(SOUND["Shoot Player"][0], SOUND["Shoot Player"][1])
SOUND = {"Explosion Meteor" : (0,0),
         "Explosion Player" : (0,1),
         "Explosion Enemie" : (0,2),
         "Explosion Boss"   : (0,3),
         "Input"            : (1,4),
         "Error"            : (1,5),
         "Buy"              : (1,6),
         "Shoot Player"     : (2,7),
         "Shoot Enemie"     : (2,8),
         "Shoot Boss"       : (2,9),
         "Hurt"             : (0,10)}

BULLETTYPE = {"yellow"  : (0,  64),
              "red"     : (4,  64),
              "blue"    : (8,  64),
              "gray"    : (12, 64),
              "green"   : (0,  68),
              "pink"    : (4,  68),
              "dark"    : (8,  68),
              "yellow2" : (12, 68)}

#         Name:        u,v,   bulletColor, recoil, maxHealth, maxVel, shield, cost, power, frameRate
SHIPS = {"Plane"     :(0,136, "gray",      50,     6,         50,     0,      0,      1,     50),
         "Jet"       :(0,168, "gray",      20,     10,        80,     6,      50,     2,     10),
         "BatJet"    :(0,152, "blue",      20,     16,        100,    10,     200,    2,     10),
         "USS"       :(0,184, "blue",      10,     20,        80,     20,     700,    3,     10),
         "Bessie"    :(0,0,   "green",     15,     16,        80,     10,     300,    1,     10),
         "Topter"    :(0,88,  "blue",      5,      16,        150,    20,     600,    2,     100),
         "X-Wing"    :(0,120, "yellow",    5,      16,        150,    16,     500,    2,     10),
         "Falcon"    :(0,104, "yellow2",   10,     20,        200,    20,     800,    3,     10),
         "Destroyer" :(0,200, "red",       50,     20,        50,     20,     900,   10,    10),
         "Super"     :(0,216, "red",       1,      999,       300,    999,    1000,   999,   10)}

#           Name:        u, v,   bulletColor, recoil, maxHealth, maxVel, shield, damage, power, frameRate
ENEMIES = {"Meteor"    :(64,88,  "gray",      -1,     1,        50,      0,      3,      -1,    10),
           "Invader"   :(64,152, "green",     100,    2,        10,      0,      1,      1,     5),
           "Alien"     :(64,184, "red",       100,    20,       10,      20,     20,     10,    10),
           "Plane"     :(64,104, "gray",      60,     6,        20,      0,      2,      1,     50),
           "Jet"       :(64,120, "yellow",    30,     20,       50,      20,     20,     2,     10),
           "Tie"       :(64,136, "yellow2",   20,     8,        80,      0,      2,      1,     10),
           "Vader"     :(64,168, "red",       15,     20,       80,      20,     20,     2,     10)}

class Sprite():
    def __init__(self, x:int, y:int, img:int, w:int, h:int, u:int, v:int, maxVel:int=0, colorKey:int=None, animations=None, animationSpeed=0) -> None:
        self.x = x
        self.y = y
        self.xInt = x
        self.yInt = y
        self.img = img
        self.w = w
        self.h = h
        self.u = u
        self.v = v
        self.colorKey = colorKey
        self.animations = animations
        self.animationSpeed = animationSpeed
        
        self.animationLoops = -1
        self.playing = ""
        self.frame = 0
        self.animationTime = 0

        self.temTime = perf_counter()
        self.dt = 0

        self.vm = maxVel
        self.vx = 0
        self.vy = 0

        self.autoMove = False
        self.stopAtTime = 0
        self.stopAtX = 0
        self.stopAtY = 0
        self.timeStop = 0

    def collidePoint(self, x, y):
        re = False
        if self.x <= x < self.x + self.w:
            if self.y <= y < self.y + self.h:
                re = True
        return re
    
    def collideSprite(self, other):
        re = False
        if self.x + self.w >= other.x and self.x <= other.x + other.w and self.y + self.h >= other.y and self.y <= other.y + other.h:
            re = True
        return re

    def animationLoop(self):
        if self.playing:
            dt = perf_counter() - self.animationTime
            if self.animationSpeed*dt >= 1:
                self.frame += 1
                if self.frame >= len(self.animations[self.playing]):
                    self.animationLoops -= 1
                    if self.animationLoops == 0:
                        self.playing = ""
                        return
                    self.frame = 0
                self.animationTime = perf_counter()
                self.u = self.animations[self.playing][self.frame][0]
                self.v = self.animations[self.playing][self.frame][1]

    def playAnimation(self, animationName, loops=-1, fromStart=False):
        self.animationLoops = loops
        self.playing = animationName
        self.animationTime = perf_counter()
        if fromStart or self.frame >= len(self.animations[self.playing]):
            self.frame = 0
        self.u = self.animations[self.playing][self.frame][0]
        self.v = self.animations[self.playing][self.frame][1]
    
    def stopAnimation(self, fromStart=False):
        self.playing = ""
        if fromStart:
            self.frame = 0

    def userInput(self):
        vx = 0
        vy = 0
        if pyxel.btnp(pyxel.KEY_RIGHT, repeat=1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT, repeat=1):
            vx += 1
        if pyxel.btnp(pyxel.KEY_LEFT, repeat=1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, repeat=1):
            vx += -1

        if pyxel.btnp(pyxel.KEY_UP, repeat=1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP, repeat=1):
            vy += -1
        if pyxel.btnp(pyxel.KEY_DOWN, repeat=1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN, repeat=1):
            vy += 1

        vm = (vx**2 + vy**2)**0.5
        if vm:
            vx = vx/vm
            vy = vy/vm
            
        self.vx = vx
        self.vy = vy

    def move(self, px:int, py:int, time:float):
        dx = px - self.x
        dy = py - self.y
        if dx != 0 or dy != 0:
            vx = dx/time
            vy = dy/time
            self.vm = (vx**2 + vy**2)**0.5
            self.vx = vx/self.vm
            self.vy = vy/self.vm
            self.autoMove = True
            self.stopAtTime = time
            self.stopAtX = px
            self.stopAtY = py
            self.timeStop = 0

    def updateAutoMove(self, dt):
        if self.autoMove:
            self.timeStop += dt
            if self.timeStop >= self.stopAtTime:
                self.vx = 0
                self.vy = 0
                self.xInt = self.stopAtX
                self.yInt = self.stopAtY
                self.x = self.stopAtX
                self.y = self.stopAtY
                self.autoMove = False

    def update(self):
        self.dt = perf_counter() - self.temTime
        self.temTime = perf_counter()

        self.animationLoop()
        self.updateAutoMove(self.dt)

        self.x += self.vm*self.vx*self.dt
        self.y += self.vm*self.vy*self.dt
        self.xInt = round(self.x)
        self.yInt = round(self.y)

    def draw(self):
        pyxel.blt(self.xInt, self.yInt, self.img, self.u, self.v, self.w, self.h, self.colorKey)


class Bullet(Sprite):
    def __init__(self, x: int, y: int, power: int, maxVel: int, container, type) -> None:
        super().__init__(x, y, img=0, w=4, h=4, u=BULLETTYPE[type][0], v=BULLETTYPE[type][1], maxVel=maxVel, colorKey=0)
        self.power = power
        self.container = container
        self.type = type
    
    def update(self):
        super().update()
        if pyxel.height < self.y or pyxel.width < self.x or self.x < 0:
                self.container.remove(self)


class Ship():
    def __init__(self, name, dic) -> None:
        self.name = name
        u = dic[self.name][0]
        v = dic[self.name][1]

        self.animation = {"idle": [(u + i*16, v) for i in range(3)],
                          "death": [(i*16, 16) for i in range(7)],
                          "end": [(u + 48, v)]}

        self.bulletsColor = dic[self.name][2]
        self.recoil = dic[self.name][3]
        self.maxHealth = dic[self.name][4]
        self.maxVel = dic[self.name][5]
        self.shield = dic[self.name][6]
        self.cost = dic[self.name][7]
        self.power = dic[self.name][8]
        self.animationSpeed = dic[self.name][9]
    
    def draw(self, x, y):
        pyxel.blt(x, y, 0, self.animation["idle"][0][0], self.animation["idle"][0][1], 16, 16, 0)


class Player(Sprite):
    def __init__(self) -> None:
        self.ships = ["Plane"]
        super().__init__(x=pyxel.width//2 - 8, y=pyxel.height - 32, img=0, w=16, h=16, u=0, v=0, colorKey=0, animationSpeed=10)
        
        self.shipName = self.ships[0]
        self.recoil = 1
        self.maxRecoil = 1
        self.maxHealth = 1
        self.health = self.maxHealth
        self.maxShields = 1
        self.shields = self.maxShields
        self.power = 1
        self.alive = True
        self.bullets = []
        self.score = 0
        self.darkMatter = 0
        self.bulletColor = "green"

        self.changeShip(self.ships[0])

    def changeShip(self, name):
        ship = Ship(name, SHIPS)
        self.shipName = name
        self.animationSpeed = ship.animationSpeed
        self.u = ship.animation["idle"][0][0]
        self.v = ship.animation["idle"][0][1]
        self.vm = ship.maxVel
        self.animations = ship.animation
        self.bulletColor = ship.bulletsColor
        self.playAnimation("idle")
        self.maxRecoil = ship.recoil
        self.recoil = -1
        self.power = ship.power
        self.maxHealth = ship.maxHealth
        self.maxShields = ship.shield
        self.health = self.maxHealth
        self.shields = self.maxShields

    def shoot(self):
        x = self.x + self.w//2 - 2
        y = self.y-8
        v = 200
        b = Bullet(x, y, self.power, v, self.bullets, self.bulletColor)
        b.vy = -1
        self.bullets.append(b)
        pyxel.play(SOUND["Shoot Player"][0], SOUND["Shoot Player"][1])

    def update(self):
        super().update()

        if self.x < 0:
            self.x = 0
        elif self.x + self.w > pyxel.width:
            self.x = pyxel.width - self.w
        
        if self.y < 0:
            self.y = 0
        elif self.y + self.h > pyxel.height:
            self.y = pyxel.height - self.h

        if self.alive:
            self.userInput()
            if pyxel.btnp(pyxel.KEY_A, repeat=1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X, repeat=1):
                if self.recoil < 0:
                    self.shoot()
                    self.recoil = self.maxRecoil
            
            self.recoil -= 1
            
            if self.health > self.maxHealth:
                self.health = self.maxHealth
            elif self.health < 0:
                self.health = 0
            
            if self.shields > self.maxShields:
                self.shields = self.maxShields
            elif self.shields < 0:
                self.shields = 0

            if self.health <= 0:
                self.playAnimation("death", 1)
                self.alive = False
                self.health = 0
                self.vx = 0
                self.vy = 0
                pyxel.play(SOUND["Explosion Player"][0], SOUND["Explosion Player"][1])
        
        for bullet in self.bullets:
            bullet.update()

    def draw(self):
        if not self.alive:
            u = self.animations["end"][0][0]
            v = self.animations["end"][0][1]
            pyxel.blt(self.xInt, self.yInt, self.img, u, v, self.w, self.h, self.colorKey)
        
        for bullet in self.bullets:
            bullet.draw()
        super().draw()

        if self.shields > 0:
            pyxel.circb(self.xInt + 7, self.yInt + 7, 16, 6)


class Enemie(Sprite):
    def __init__(self, x, y, container, name) -> None:
        self.ship = Ship(name, ENEMIES)
        super().__init__(x=x, y=y, img=0, w=16, h=16, u=0, v=32, maxVel=100, colorKey=0)

        self.alive = True
        self.bullets = container

        self.animationSpeed = self.ship.animationSpeed
        self.u = self.ship.animation["idle"][0][0]
        self.v = self.ship.animation["idle"][0][1]
        self.vm = self.ship.maxVel
        self.animations = self.ship.animation
        self.bulletColor = self.ship.bulletsColor
        self.playAnimation("idle")
        self.recoilMax = self.ship.recoil
        self.recoil = self.recoilMax
        self.power = self.ship.power
        self.maxHealth = self.ship.maxHealth
        self.maxShields = self.ship.shield
        self.health = self.maxHealth
        self.shields = self.maxShields
        self.points = 10

        self.playAnimation("idle")

        #self.vx = 0.9
        self.vy = 1
        self.shootVel = 200
        self.shootX = 0
        self.shootY = 1

    def shoot(self):
        x = self.x + self.w//2 - 2
        y = self.y + self.h//2 - 2
        b = Bullet(x, y, self.power, self.shootVel, self.bullets, self.bulletColor)
        b.vx = self.shootX
        b.vy = self.shootY
        self.bullets.append(b)
        if self.ship.name in ("Jet", "Vader", "Alien"):
            pyxel.play(SOUND["Shoot Boss"][0], SOUND["Shoot Boss"][1])
        else:
            pyxel.play(SOUND["Shoot Enemie"][0], SOUND["Shoot Enemie"][1])

    def moveMeteor(self, player):
        self.vx = 1
        self.vy = 1
        if self.x > pyxel.width:
            self.x = -self.w

    def movePlane(self, player):
        if self.vx == 0:
            self.vx = 1

        d = 1
        if self.x > player.x + d:
            self.vx = -0.5
        elif self.x < player.x - d:
            self.vx = 0.5
        else:
            self.vx = 0

        if self.y < 0:
            self.vy = 0.5
        elif self.y + self.h > pyxel.height-32:
            self.vy = -0.5
    
    def moveJet(self, player):
        if self.vx == 0:
            self.vx = 1

        d = 1
        if self.x > player.x + d:
            self.vx = -0.5
        elif self.x < player.x - d:
            self.vx = 0.5
        else:
            self.vx = 0

        if self.y < 0:
            self.vy = 1
        elif self.y + self.h > pyxel.height//2:
            self.vy = -0.5

    def moveTie(self, player):
        if self.vx == 0:
            self.vx = 1
        
        vx = player.x - self.x
        vy = player.y - self.y
        d = (vx**2 + vy**2)**0.5
        self.shootX = vx/d
        self.shootY = vy/d

        if self.x < 16:
            self.vx = 1
        elif self.x + self.w > pyxel.width-16:
            self.vx = -0.5

        if self.y < 0:
            self.vy = 0.3
        elif self.y + self.h > pyxel.height-64:
            self.vy = -1
    
    def moveInvader(self, player):
        if self.vx == 0:
            self.vx = 1
            self.vy = 0.5

        if self.x <= 0:
            self.vx = 1
            self.y += 16
            self.x = 0
        elif self.x + self.w >= pyxel.width:
            self.vx = -1
            self.y += 16
            self.x = pyxel.width - self.w
        
        if self.y < 0:
            self.vy = 0.5
        elif self.y + self.h > pyxel.height-64:
            self.vy = -1

    def moveVader(self, player):
        if self.vx == 0:
            self.vx = 0.1
        
        vx = player.x - self.x
        vy = player.y - self.y
        d = (vx**2 + vy**2)**0.5
        self.shootX = vx/d
        self.shootY = vy/d

        if self.x < 32:
            self.vx = 0.1
        elif self.x + self.w > pyxel.width-32:
            self.vx = -0.1

        if self.y < 0:
            self.vy = 1
        elif self.y + self.h > pyxel.height//2:
            self.vy = -0.1
    
    def moveAlien(self, player):
        if self.vx == 0:
            self.vx = 1
            self.vy = 0.5

        if self.x <= 0:
            self.vx = 1
            self.y += 16
            self.x = 0
        elif self.x + self.w >= pyxel.width:
            self.vx = -1
            self.y += 16
            self.x = pyxel.width - self.w

        if self.vx == 0:
            self.vx = 1
        
        if self.y < 0:
            self.vy = 0.5
        elif self.y + self.h > pyxel.height-64:
            self.vy = -1
        
        vx = player.x - self.x
        vy = player.y - self.y
        d = (vx**2 + vy**2)**0.5
        self.shootX = vx/d
        self.shootY = vy/d

    def update(self, player):
        super().update()
        if self.alive:  
            self.recoil -= 1
            if self.recoil == 0:
                self.shoot()
                self.recoil = self.recoilMax
            
            if self.ship.name == "Meteor":
                self.moveMeteor(player)
            elif self.ship.name == "Plane":
                self.movePlane(player)
            elif self.ship.name == "Jet":
                self.moveJet(player)
            elif self.ship.name == "Tie":
                self.moveTie(player)
            elif self.ship.name == "Invader":
                self.moveInvader(player)
            elif self.ship.name == "Vader":
                self.moveVader(player)
            elif self.ship.name == "Alien":
                self.moveAlien(player)
            
            if self.health <= 0:
                self.playAnimation("death", 1)
                self.alive = False
                self.health = 0
                self.vx = 0
                self.vy = 0
                if self.ship.name == "Meteor":
                    pyxel.play(SOUND["Explosion Meteor"][0], SOUND["Explosion Meteor"][1])
                elif self.ship.name in ("Jet", "Vader", "Alien"):
                    pyxel.play(SOUND["Explosion Boss"][0], SOUND["Explosion Boss"][1])
                else:
                    pyxel.play(SOUND["Explosion Enemie"][0], SOUND["Explosion Enemie"][1])

    def draw(self):
        if not self.alive:
            u = self.animations["end"][0][0]
            v = self.animations["end"][0][1]
            pyxel.blt(self.xInt, self.yInt, self.img, u, v, self.w, self.h, self.colorKey)
        
        super().draw()

        if self.shields > 0:
            pyxel.circb(self.xInt + 7, self.yInt + 7, 16, 8)


class ChangeShipMenu():
    def __init__(self, game) -> None:
        nameShips = list(SHIPS.keys())
        self.ships = [Ship(name, SHIPS) for name in nameShips]
        self.selection = 0
        self.game = game

    def update(self):
        if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.selection = (self.selection - 1)%len(self.ships)
            pyxel.play(SOUND["Input"][0], SOUND["Input"][1])
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.selection = (self.selection + 1)%len(self.ships)
            pyxel.play(SOUND["Input"][0], SOUND["Input"][1])
        if pyxel.btnp(pyxel.KEY_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
            if self.ships[self.selection].name in self.game.player.ships:
                self.game.player.changeShip(self.ships[self.selection].name)
                pyxel.play(SOUND["Input"][0], SOUND["Input"][1])
            else:
                if self.game.player.darkMatter >= self.ships[self.selection].cost:
                    self.game.player.darkMatter -= self.ships[self.selection].cost
                    self.game.player.ships.append(self.ships[self.selection].name)
                    self.game.player.changeShip(self.ships[self.selection].name)
                    pyxel.play(SOUND["Buy"][0], SOUND["Buy"][1])
                else:
                    pyxel.play(SOUND["Error"][0], SOUND["Error"][1])
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.game.scene = "Main Menu"
            pyxel.play(SOUND["Input"][0], SOUND["Input"][1])

    def draw(self):
        x = pyxel.width//2 - 8
        y = pyxel.height//2 - 8
        self.ships[self.selection].draw(x, y)
        pyxel.blt(x+4-20, y+4, 0, 16, 72, 8, 8, 0)
        pyxel.blt(x+4+20, y+4, 0, 24, 72, 8, 8, 0)
        if self.ships[self.selection].name == self.game.player.shipName:
            pyxel.rectb(x-5, y-5, 26, 26, 9)

        #pyxel.text(10, 40, f"Dark Matter: {self.game.player.darkMatter}", 1)
        d = self.game.player.darkMatter
        pyxel.blt(10, 20, 0, 0, 40, 8, 8, 0)
        pyxel.text(20, 22, f"x{d}",7)
        
        name = self.ships[self.selection].name
        pyxel.text((pyxel.width - len(name)*4 + 1)//2, y - 12, f"{name}", 7)
        if self.ships[self.selection].name in self.game.player.ships:
            pyxel.text(10, y + 30, "Cost: Sold", 3)
        else:
            if self.game.player.darkMatter >= self.ships[self.selection].cost:
                pyxel.text(10, y + 30, f"Cost:", 6)
                pyxel.blt(33, y + 28, 0, 0, 40, 8, 8, 0)
                pyxel.text(43, y + 30, f"x{self.ships[self.selection].cost}", 6)
            else:
                pyxel.text(10, y + 30, f"Cost:", 8)
                pyxel.blt(33, y + 28, 0, 0, 40, 8, 8, 0)
                pyxel.text(43, y + 30, f"x{self.ships[self.selection].cost}", 8)
        pyxel.text(10, y + 40, "Health:", 7)
        for i in range(self.ships[self.selection].maxHealth):
            if i%2==0:
                pyxel.blt(45 + i*5, y + 40, 0, 0, 32, 4, 8, 0)
            else:
                pyxel.blt(44 + i*5, y + 40, 0, 4, 32, 4, 8, 0)
        pyxel.text(10, y + 50, "Shileds:", 7)
        for i in range(self.ships[self.selection].shield):
            if i%2==0:
                pyxel.blt(45 + i*5, y + 50, 0, 8, 32, 4, 8, 0)
            else:
                pyxel.blt(44 + i*5, y + 50, 0, 12, 32, 4, 8, 0)
        pyxel.text(10, y + 60, f"Bullets Power: {self.ships[self.selection].power}", 7)
        pyxel.text(10, y + 70, f"Recoil: {self.ships[self.selection].recoil}", 7)
        pyxel.text(10, y + 80, f"Speed: {self.ships[self.selection].maxVel}", 7)
        pyxel.text(10, y + 90, f"Bullet Color:", 7)
        b = BULLETTYPE[self.ships[self.selection].bulletsColor]
        pyxel.blt(64, y + 91, 0, b[0], b[1], 4, 4, 0)


class Menu():
    def __init__(self, game) -> None:
        self.selection = 0
        self.game = game
        self.options = ["Start Game", "Buy Ship", "Exit Game"]
        self.lenghts = [len(option)*4 - 1 for option in self.options]

    def update(self):
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.selection = (self.selection - 1)%len(self.options)
            pyxel.play(SOUND["Input"][0], SOUND["Input"][1])
        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.selection = (self.selection + 1)%len(self.options)
            pyxel.play(SOUND["Input"][0], SOUND["Input"][1])
        if pyxel.btnr(pyxel.KEY_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
            pyxel.play(SOUND["Input"][0], SOUND["Input"][1])
            if self.selection == 0:
                self.game.reset()
                self.game.scene = "Game Stage 1"
            elif self.selection == 1:
                self.game.scene = "Buy Ship Menu"
            elif self.selection == 2:
                pyxel.quit()

    def drawStats(self):
        s = self.game.player.score
        d = self.game.player.darkMatter
        pyxel.text(10, 10, f"Score: {s}", 7)
        #pyxel.text(10, 40, f"Dark Matter: {d}", 1)
        pyxel.blt(10, 20, 0, 0, 40, 8, 8, 0)
        pyxel.text(20, 22, f"x{d}",7)

    def drawInstructions(self):
        x = 10
        y = pyxel.height//2
        pyxel.text(x, y, "Press arrows keys to move", 7)
        pyxel.text(x, y+7, "Press 'A' key to select / shoot", 7)
        pyxel.text(x, y+7*2, "Press 'Z' key to go back", 7)
        pyxel.text(x, y+7*3, "Hold 'S' and 'X' at the same time to self desctruct", 7)
        pyxel.text(x, y+7*4, "Press 'F4' to quit", 7)
        pyxel.text(x, y+7*5, "Press 'ALT' + 'ENTER' to toggle full screen", 7)

    def drawOptions(self):
        y0 = pyxel.height - 20*len(self.options)
        for i, option in enumerate(self.options):
            x = pyxel.width//2 - self.lenghts[i]//2
            y = y0 + 10*i
            pyxel.text(x, y, option, 7)
        x = pyxel.width//2 - self.lenghts[self.selection]//2 - 20
        y = y0 + 10*self.selection - 2
        pyxel.blt(x, y, 0, 0, 72, 16, 16, 0)

    def draw(self):
        self.drawOptions()
        self.drawStats()
        #self.drawInstructions()


class Game:
    def __init__(self) -> None:
        pyxel.init(160, 240, title="Dark Matter", fps=60, display_scale=4, quit_key=pyxel.KEY_F4, capture_sec=10)
        path = join(getcwd(), pardir, "assets", "assets.pyxres")
        pyxel.load(path)

        self.scenesList = ["Main Menu", "Buy Ship Menu", "Game Stage 1", "Game Stage 2"]
        self.scene = "Main Menu"
        self.stage = 0
        self.time0 = 0
        self.totalTime = 0

        self.menu = Menu(self)
        self.buyMenu = ChangeShipMenu(self)
        self.frame_count = 0
        self.enemieRate = 100

        # Enemies
        self.bullets = []
        self.enemies = []
        # Player
        self.player = Player()

        self.stars = []
        self.starsSpeedMax = 2
        self.starsColor = 7
        self.starsSpeed = self.starsSpeedMax
        for i in range(20):
            x = pyxel.rndi(0, pyxel.width)
            y = pyxel.rndi(0, pyxel.height)
            self.stars.append([x, y])

    def reset(self):
        self.player.x = pyxel.width//2 - 8
        self.player.y = pyxel.height - 80

        self.player.playAnimation("idle")
        self.player.score = 0
        self.player.bullets = []
        self.player.health = self.player.maxHealth
        self.player.shields = self.player.maxShields
        self.player.alive = True
        self.time0 = perf_counter()
        self.stage = 0

        self.bullets = []
        self.enemies = []

    def manageStages(self):
        enemieList = ["Meteor",   "Invader",   "Invader",    "Plane",     "Plane",      "Tie",       "Tie"]
        backGround = [(6, 7, 50), (3, 6, 150), (11, 5, 200), (9, 4, 200), (10, 3, 400), (2, 2, 200), (8, 1, 400)]
        self.starsColor = backGround[self.stage%len(enemieList)][0]
        self.starsSpeedMax = backGround[self.stage%len(enemieList)][1]
        self.enemieRate = backGround[self.stage%len(enemieList)][2]
        boss = ["Alien", "Jet", "Vader"]
        self.frame_count += 1
        currentLoop = self.stage//len(enemieList) + 1

        if self.frame_count%self.enemieRate == 0:
            name = enemieList[self.stage%len(enemieList)]

            w = round((pyxel.width-16)/currentLoop)
            for i in range(currentLoop):
                x = pyxel.rndi(w*i, w*(i+1))
                y = -16
                e = Enemie(x, y, self.bullets, name)
                self.enemies.append(e)

            self.frame_count = 1

        if self.stage%len(enemieList) in (2,4,6):
            done = True
            for enemie in self.enemies:
                if enemie.ship.name in boss:
                    done = False
            if done:
                for enemie in self.enemies:
                    enemie.health = 0
                    enemie.points = 0
        else:
            done = self.totalTime > 15

        if done:
            self.stage += 1
            self.time0 = perf_counter()
            if self.stage%len(enemieList) in (2,4,6):
                w = round((pyxel.width-16)/currentLoop)
                for i in range(currentLoop):
                    x = pyxel.rndi(w*i, w*(i+1))
                    y = -16
                    e = Enemie(x, y, self.bullets, boss[(self.stage%len(enemieList))//2-1])
                    self.enemies.append(e)
        
    def updateGame(self):
        self.player.update()
        if self.player.alive:
            self.totalTime = perf_counter() - self.time0

        self.manageStages()
        
        for bullet in self.bullets:
            bullet.update()

        for enemie in self.enemies:
            enemie.update(self.player)
            if enemie.alive:
                if enemie.y > pyxel.height:
                    self.enemies.remove(enemie)

                for bullet in self.player.bullets:
                    if enemie.collidePoint(bullet.x+2, bullet.y+2):
                        pyxel.play(SOUND["Hurt"][0], SOUND["Hurt"][1])
                        self.player.bullets.remove(bullet)
                        if enemie.shields > 0:
                            enemie.shields -= bullet.power
                        else:
                            enemie.shields = 0
                            enemie.health -= bullet.power
                
                if self.player.alive and enemie.collideSprite(self.player):
                    enemie.health = 0
                    enemie.shields = 0
                    if self.player.shields > 0:
                        self.player.shields -= enemie.ship.cost
                    self.player.health -= enemie.ship.cost

            else:
                if enemie.playing == "":
                    self.enemies.remove(enemie)
                    self.player.score += enemie.points
                    x = enemie.x + 8
                    y = enemie.y + 8
                    op = ["pink", "blue", "dark"]
                    p = Bullet(x, y, 10, 20, self.bullets, op[pyxel.rndi(0, 2)])
                    p.vy = 1
                    self.bullets.append(p)

        if self.player.alive:
            for bullet in self.bullets:
                if self.player.collidePoint(bullet.x+2, bullet.y+2):
                    if bullet.type == "pink":
                        if self.player.health < self.player.maxHealth:
                            self.bullets.remove(bullet)
                            self.player.health += bullet.power
                            pyxel.play(SOUND["Buy"][0], SOUND["Buy"][1])
                            if self.player.health > self.player.maxHealth:
                                self.player.health = self.player.maxHealth
                    elif bullet.type == "dark":
                        self.bullets.remove(bullet)
                        self.player.darkMatter += bullet.power
                        pyxel.play(SOUND["Buy"][0], SOUND["Buy"][1])
                    elif bullet.type == "blue":
                        if self.player.shields < self.player.maxShields:
                            self.bullets.remove(bullet)
                            self.player.shields += bullet.power
                            pyxel.play(SOUND["Buy"][0], SOUND["Buy"][1])
                            if self.player.shields > self.player.maxShields:
                                self.player.shields = self.player.maxShields
                    else:
                        self.bullets.remove(bullet)
                        pyxel.play(SOUND["Hurt"][0], SOUND["Hurt"][1])
                        if self.player.shields > 0:
                            self.player.shields -= bullet.power
                        else:
                            self.player.shields = 0
                            self.player.health -= bullet.power
        else:
            if self.player.playing == "":
                if pyxel.btnr(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                    #self.player.darkMatter += self.player.score//10
                    self.scene = "Main Menu"
                    pyxel.play(SOUND["Input"][0], SOUND["Input"][1])

        if (pyxel.btnp(pyxel.KEY_S, hold=100, repeat=1) and pyxel.btnp(pyxel.KEY_X, hold=100, repeat=1)) or (pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A, hold=100, repeat=1) and pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B, hold=100, repeat=1)):
            self.player.shields = 0
            self.player.health = 0

        if pyxel.btnp(pyxel.KEY_F2):
            current = self.player.shipName
            li = list(SHIPS.keys())
            i = li.index(current)
            next_i = (i + 1)%len(li)
            nextShip = li[next_i]
            self.player.changeShip(nextShip)

    def drawGame(self):
        pyxel.text(10,pyxel.height - 8,f"Score: {self.player.score}",7)
        
        for i in range(self.player.health):
            if i%2==0:
                pyxel.blt(10 + i*5, pyxel.height - 20, 0, 0, 32, 4, 8, 0)
            else:
                pyxel.blt(9 + i*5, pyxel.height - 20, 0, 4, 32, 4, 8, 0)
        for i in range(self.player.shields):
            if i%2==0:
                pyxel.blt(11 + i*5, pyxel.height - 18, 0, 8, 32, 4, 8, 0)
            else:
                pyxel.blt(10 + i*5, pyxel.height - 18, 0, 12, 32, 4, 8, 0)
        
        pyxel.blt(pyxel.width//2, pyxel.height - 10, 0, 0, 40, 8, 8, 0)
        pyxel.text(pyxel.width//2 + 10, pyxel.height - 8, f"x{self.player.darkMatter}",7)
        pyxel.text(pyxel.width//2 + 40, pyxel.height - 8, f"Stage: {self.stage}", 1)
        
        #pyxel.text(10,70,f"Ship: {self.player.health}",1)
        #pyxel.text(10,80,f"Shields: {self.player.shields}",1)
        #pyxel.text(10,90,f"Dark Matter: {self.player.darkMatter}",1)
        #pyxel.text(10, 10, f"Time: {self.totalTime}", 1)
        
        recoil = (0, round(self.player.recoil/self.player.maxRecoil*100))[self.player.recoil > 0]
        #pyxel.text(10, 10, f"Recoil: {recoil} %", 1)
        #pyxel.blt(pyxel.width//2 - 8, pyxel.height - 27, 0, 16, 32, 16, 4, 0)
        d = 40
        maxW = pyxel.width-d*2
        w = maxW*recoil//100
        pyxel.rect(d, pyxel.height - 27, pyxel.width-d*2, 4, 1)
        pyxel.rect((pyxel.width - w)//2, pyxel.height - 27 + 1, w, 2, 2)
        
        for bullet in self.bullets:
            bullet.draw()
        for enemie in self.enemies:
            enemie.draw()
        self.player.draw()

        if not self.player.alive:
            msg = "GAME OVER"
            x = (pyxel.width - 4*9-1)//2
            y = pyxel.height//2
            pyxel.text(x, y, msg, 7)
    
    def update(self):
        if self.scene == "Main Menu":
            self.menu.update()
        elif self.scene == "Game Stage 1":
            self.updateGame()
        elif self.scene == "Buy Ship Menu":
            self.buyMenu.update()
        
        if self.starsSpeed == 0:
            for star in self.stars:
                star[0] = (star[0] + 1)%pyxel.width
                star[1] = (star[1] + 1)%pyxel.height
            self.starsSpeed = self.starsSpeedMax
        
        self.starsSpeed -= 1

    def drawBackground(self):
        pyxel.cls(0)

        for star in self.stars:
            pyxel.pset(star[0], star[1], self.starsColor)
        
    def draw(self):
        self.drawBackground()

        if self.scene == "Main Menu":
            self.menu.draw()
            self.starsColor = 7
            self.starsSpeedMax = 2
        elif self.scene == "Game Stage 1":
            self.drawGame()
        elif self.scene == "Buy Ship Menu":
            self.buyMenu.draw()
            self.starsColor = 11
            self.starsSpeedMax = 2

    def run(self):
        pyxel.run(self.update, self.draw)


if __name__ == "__main__":
    Game().run()
