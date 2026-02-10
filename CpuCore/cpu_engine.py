""" 
    This is in charge of starting up pygame and maintaining the game loop
"""

import pygame as pg
import sys


class Engine:
    def __init__(self, title: str, winRes: tuple):
        # pg.init()
        self.win_res = winRes
        self.screen: pg.Surface= pg.display.set_mode(self.win_res)
        self.clock = pg.time.Clock()
        self.title_str = title
        self.delta_time = 0

        self.program = None
    
    def update(self):
        self.delta_time = self.clock.tick()
        pg.display.set_caption(f"{self.title_str}: {self.clock.get_fps(): .1f}")
        self.update_time()
        if self.program != None:
            self.program.update()
        pg.display.flip()

    def update_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def check_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            if self.program != None:
                if self.program.camera.mouse_centering:
                    if e.type == self.program.camera.mce_id:
                        #   set the mouse cursor to be at the center always
                        pg.mouse.set_pos([
                            int(self.win_res[0] / 2), int(self.win_res[1] / 2)]) 

    def start(self):
        while True:
            self.check_events()
            self.update()