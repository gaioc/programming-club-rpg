import pygame as pg
from os import system
import esper
from dataclass import dataclass
from typing import List, Dict

#PYGAME DEPENDENCIES
clock = pg.time.Clock()
pg.font.init()

def cls():
    """Clear console."""
    system("clear")
def printScr(text: str, posx: float, posy: float, colour: pg.Color, font: pg.font.Font, screen: pg.Surface):
    """
    Render text at (posx,posy) of screen, using font in provided colour.
    """
    render = font.render(text, True, colour)
    rect = render.get_rect()
    rect.center = posx, posy
    rect.left = posx
    screen.blit(render, rect)

class Options:
    """
    Component that holds all ingame options and constants, as well as references to important objects
    """
    textSpeed : int = 1
    Screen : pg.Surface
    def __init__(self, screen: pg.Surface, textSpeed: int):
        self.textSpeed = textSpeed
        self.Screen = screen

class Input:
    """Component that internally processes input. Is configurable"""
    buttonMaps : Dict[str, List[int]]
    buttons : Dict[str, bool]
    def __init__(self, maps):
        self.buttonMaps = maps
        self.buttons = dict()
    def pumpInput(self):
        """Internally gathers and processes input. Should be called once per frame."""
        pressed = pg.key.get_pressed()
        for key in self.buttonMaps.keys():
            self.buttons[key] = any([pressed[i] for i in self.buttonMaps[key]])
        #print(self.buttons)
        pg.event.pump()

class DialogInstance:
    """
    Base class for dialog actions to inherit from
    """
    active : bool = False
    def __init__(self):
        pass
    def Update(self, screen, inputs, textSpeed):
        print("NOTIMPLEMENTED: UNDEFINED FUNCTION")
        return -2

class DialogHealPlayer(DialogInstance):
    active : bool = False
    next : int = -2
    def __init__(self, next):
        self.next = next
    def Activate(self):
        self.active = True
    def Update(self, screen, inputs, textSpeed):
        """
        Heal the player's party to full and restore TP.
        """
        print("NOTIMPLEMENTED: HEAL PARTY")
        return self.next

class DialogGiveQuest(DialogInstance):
    active : bool = False
    questID : str
    next : int = -2
    def __init__(self, questID, next):
        self.questID = questID
        self.next = next
    def Activate(self):
        self.active = True
    def Update(self, screen, inputs, textSpeed):
        """
        Give the player a quest.
        """
        print(f"NOTIMPLEMENTED: GIVE QUEST {self.questID}")
        return self.next

class DialogText(DialogInstance):
    """                                                                                    
    One "segment" of dialogue. Used internally by the Dialog component.
    """
    text : str = ""
    textInd : float = 0
    playerOptions : List[str] = []
    nextDialog : List[int] = []
    active : bool = False
    chosenOption : int = 0
    btnHeld : bool = False

    def __init__(self, text: str, playerOptions: List[str], nextDialog: List[int]):
        self.text = text
        self.playerOptions = playerOptions
        self.nextDialog = nextDialog
        self.font = pg.font.Font("ponde___.ttf", 16)
    
    def Activate(self):
        self.active = True
        self.textInd = 0
        self.chosenOption = 0
        self.btnHeld = True #used to make sure player does not accidentally skip dialogue
    def Update(self, screen: pg.Surface, inputs, textSpeed: int) -> int:
        #Draw dialog box
        pg.draw.rect(screen, (0,0,0), pg.Rect(8, 379, 624, 96))
        #cls()
        #Draw text
        
        toDisplay = list(self.text[0:int(self.textInd+textSpeed)])
        
        wrapping = 44
        
        for i in range(0, len(toDisplay), wrapping):
            printScr("".join(toDisplay[i:i+wrapping]), 16, 394+20*i//wrapping, (255,255,255), self.font, screen)
            finalPos = i
            
        #Check for skipping text scrolling
        if inputs.buttons["cancel"]:
            #print("SKIP")
            self.textInd = len(self.text)

        self.textInd += textSpeed
        
        
            
        #End of text reached?
        if self.textInd > len(self.text):
            if len(self.playerOptions) > 0:
                for i in range(len(self.playerOptions)):
                    printScr(f"{self.playerOptions[i]}", 16, 416+20*i+finalPos, (255,255,255), self.font, screen)
                #Find where to jump to from this point
                pg.draw.circle(screen, (255,255,255), (12, 416+20*self.chosenOption+finalPos), 4)
                if self.btnHeld:
                    if not(any(inputs.buttons.values())):
                        self.btnHeld = False
                    else:
                        return -1
                if inputs.buttons["confirm"]:
                    return self.nextDialog[self.chosenOption]
                    self.btnHeld = True
                elif inputs.buttons["up"]:
                    self.chosenOption = (self.chosenOption - 1) % len(self.playerOptions)
                    self.btnHeld = True
                elif inputs.buttons["down"]:
                    self.chosenOption = (self.chosenOption + 1) % len(self.playerOptions)
                    self.btnHeld = True
                return -1
            else:
                if self.nextDialog[0] == -2:
                    #print("RECT")
                    pg.draw.rect(screen, (0,255,0), pg.Rect(308, 464, 16, 16))
                else:
                    #print("CIRCLE")
                    pg.draw.circle(screen, (0,255,0), (316, 472), 8)
                pg.display.flip()
                if self.btnHeld:
                    if not(any(inputs.buttons.values())):
                        self.btnHeld = False
                    return -1
                if inputs.buttons["confirm"]:
                    return self.nextDialog[0]
                else:
                    return -1
        
        return -1


class Dialog:
    """
    Implementation of a simple dialog system using ECS.
    Consists of a list of "DialogueInstance"s.
    Update is run every frame if activated.
    """
    dialogIndex : int = 0
    texts = List[DialogInstance]
    #textOptions : list[list[str]]
    active : bool = False
    def __init__(self, texts: List[DialogInstance]):
        self.texts = texts
    def Activate(self):
        self.active = True
        self.dialogIndex = 0
    def Update(self, screen, inputs, textSpeed) -> int:
        #Update current DialogInstance
        try:
            result = self.texts[self.dialogIndex].Update(screen, inputs, textSpeed)
        except IndexError:
            raise IndexError("Invalid dialogue jump. Make sure dialogue jumps to a valid index.")
        if result == -2:
            #Code -2 means end of dialog
            self.active = False
            return -2
        if result == -1:
            #Code -1 means continue
            return -1
        else:
            #All other codes mean to jump to indexed dialogue
            self.texts[self.dialogIndex].active = False
            self.dialogIndex = result
            try:
                self.texts[self.dialogIndex].Activate()
            except IndexError:
                raise IndexError("Invalid dialogue jump. Make sure dialogue jumps to a valid index.")
class InputProcessor(esper.Processor):
    def process(self):
        """Pump inputs once per frame"""
        inputs = self.world.get_component(Input)[0][1]
        inputs.pumpInput()
class DialogProcessor(esper.Processor):
    """
    ECS System that updates active dialog boxes automatically.
    """
    def process(self):
        screen.fill((255,255,255))
        optionobj, options = self.world.get_component(Options)[0]
        inputs = self.world.get_component(Input)[0][1]
        for ent, dial in self.world.get_component(Dialog):
            if dial.active:
                dial.Update(options.Screen, inputs, options.textSpeed)
        pg.display.flip()
def readDialogFile(dialogFileContents):
    """
    Reads a string containing multiple formatted dialogs, 
    and returns a Dict object with their names and parsed content.
    """
    dialogDict = dict()
    # SPLIT FILE INTO INDIVIDUAL DIALOGS
    rawDialogs = dialogFileContents.split("\n\n")
    for rawDialog in rawDialogs:
        # GET ID USED IN DICT
        name = rawDialog.split("\n")[0]
        # GET LINES OF DIALOG/OTHER FUNCTIONS
        contents = rawDialog.split("\n")[1:]
        finalContents = []
        for line in contents:
            parts = line.split("|")
            data = parts[0]
            options = [i for i in parts[1].split(",") if i] # Remove redundant/empty entries
            next = [i for i in list(map(int, parts[2].split(","))) if i] # Remove redundant/empty entries
            if line[0] == "\\":
                #PROCESS DIALOG FUNCTIONS
                parts = line.split("|")
                functionWithArgs = data.split(" ")
                function = functionWithArgs[0]
                if function == "\HealPlayer":
                    finalContents.append(DialogHealPlayer(int(parts[2])))
                elif function == "\GiveQuest":
                    finalContents.append(DialogGiveQuest(functionWithArgs[1], int(parts[2])))
                else:
                    finalContents.append(DialogInstance())
            else:
                finalContents.append(DialogText(data, options, next))
        dialogDict[name] = Dialog(finalContents)
    return dialogDict




"""Initialization"""
world = esper.World()
screen = pg.display.set_mode([640,480])
dialogProcess = DialogProcessor()
world.add_processor(InputProcessor(), priority=10)
world.add_processor(dialogProcess, priority=0)

#Example usage
world.create_entity(Input({
    "confirm":[pg.K_z, pg.K_RETURN],
    "cancel":[pg.K_x, pg.K_LSHIFT, pg.K_RSHIFT],
    "up":[pg.K_UP],
    "down":[pg.K_DOWN]
}))


#Configure Options
world.create_entity(Options(screen, int(input("Enter text speed: (1-10)"))/4))

#Read Dialog File
with open("dialog.txt") as dialogData:
    dialogDict = readDialogFile(dialogData.read())

test = world.create_entity(dialogDict["Kaepora Gaebora Monologue"])
world.component_for_entity(test, Dialog).Activate()

while 1:
    #Game loop
    world.process()
    inputs = world.get_component(Input)[0][1]
    print(inputs.buttons)
    clock.tick(30)