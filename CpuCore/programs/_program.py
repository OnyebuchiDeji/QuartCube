"""
    Simple Abstract class for a Program
    
"""
from pygame import Surface

"""
    *   A program has the init and update functions

    *   Every program has a reference to the engine
"""
class Program:
    def __init__(self, EngineRef, SurfRes:tuple=(100, 100)):
        self.engine_ref = EngineRef
        self.layer =  Surface(SurfRes)
        self.camera = None
        ...
    
    
    def update(self):
        ...