"""
    This links the engine and the program.

    It contains highlevel operations such as looking at performance
    or specifying GPU interactions. 
"""

import pygame as pg
# from CpuCore.cpu_graphics import Cube
from CpuCore.cpu_engine import Engine
from CpuCore.programs.FirstCube import FirstCube
from CpuCore.programs.QuartCube import QuartCube
from CpuCore.programs.QuartCube2 import QuartCube2
from CpuCore.programs.LastCube import LastCube




class CpuCore:
    def __init__(self):
        self.eng = Engine("QuartQuest", (1200, 675))
        # self.fc = FirstCube(self.eng)
        # self.qc = QuartCube(self.eng)
        self.qc2 = QuartCube2(self.eng)
        # self.lc = LastCube(self.eng)
        self.eng.program = self.qc2

    
    def run(self):
        self.eng.start()