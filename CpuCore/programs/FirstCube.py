""" 
    This program simply shows the operation of drawing
    a Cube and viewing it with a Camera, providing a First-Person
    range of motion.
"""

import pygame as pg
from CpuCore.cpu_math import *
from CpuCore.programs._program import Program
from CpuCore.cpu_graphics import FirstPersonCamera

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..cpu_engine import Engine


class FirstCube(Program):
    def __init__(self, EngineRef: "Engine"):
        super().__init__(EngineRef, EngineRef.win_res)
        #   unit cube
        self.cube_verts = [
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
            (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)]

        self.cube_indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]

        self.cube_normals = [(0, 0, 1) * 6,
                   (1, 0, 0) * 6,
                   (0, 0, -1) * 6,
                   (-1, 0, 0) * 6,
                   (0, 1, 0) * 6,
                   (0, -1, 0) * 6]

        self.cube_model = Mat4
        
        self.camera = FirstPersonCamera(self.engine_ref, position=(0, 0, 100),
                                        mouseVisible=False, mouseCentering=True)
        #   view (camera at 0, 0, 5, looking at origin)
        self.cols = [pg.Color(255, 0, 0), pg.Color(0, 255, 0), pg.Color(0, 0, 255), pg.Color(255, 255, 255)]
        self.bg_cols = [(23, 39.5, 39.5), (46, 79, 79), (12, 12, 12)]


    def update_orientation(self):
        """Gets Mouse Positions and Update Cube's Orientation"""
        ...


    def update(self):
        self.update_orientation()
        self.layer.fill(self.bg_cols[2])   #   dark slate gray
        self.draw_cube_v2()
    
    def remap01(self, a: float, b: float, t: float):
        """
            This gives the same effect as shifting domains
            e.g. if t was the X value of the point -0.25
            and a and b are the X boundaries of the domain
            of range -1 -> 1
            doing: 
                x *= 0.5 
                x += 0.5
            will effectively shift -0.25 to the appropriate
            value it should have if the domain were shifted
            from -1 -> 1 ---> 0 -> 1
        """
        return (t - a) / (b - a)

    def remap(self, sourceVec2: np.array, targetVec2: np.array):
        """
            Remaps the sourceVec2 to be within the range of targetVec2

            By default:
                The source vec's range for X and Y are between -1 and 1
                The target vec'2 range for X and Y are determined by the
                window's Resolution

        """
        #   first remap sourceVec2's domain from -1 -> 1 to be between 0 -> 1
        #   but note the 1, -1 flip. It's to accommodate for
        #   pygame's flipped origin (which starts at 0 from the top)
        remapedSource = np.array([self.remap01(-1, 1, sourceVec2[0]),
                                self.remap01(1, -1, sourceVec2[1])])
        #   then remap to be between 0 and Win Res's Width and Height
        return remapedSource * targetVec2


    def draw_cube_v2(self):
        """
            For each cube vertex,
            transform according to the model transformation,
            view transformation, and perspective, and then
            draw each triangle's points consecutively according to the indices
        """
        self.camera.update()

        # mvp = np.matmul(self.proj, np.matmul(self.view, self.cube_model))
        mvp = self.camera.proj @ self.camera.view @ self.cube_model


        for idx, vert_idx in enumerate(self.cube_indices):
            #   must ensure points are column vectors and that the w component is 1.0 for the translation
            #   three points of triangle
            p0 = np.array([*self.cube_verts[vert_idx[0]], 1.0]).reshape(4, 1)
            p1 = np.array([*self.cube_verts[vert_idx[1]], 1.0]).reshape(4, 1)
            p2 = np.array([*self.cube_verts[vert_idx[2]], 1.0]).reshape(4, 1)
            
            #   depth culling! if a triangle's normal is not aligned
            #   to the camera's forward vecctor, don't append that triangle's points
            should_draw = False
            line1 = p1 - p0
            line2 = p2 - p1
            normal = np.cross(line1.reshape(4,)[:3], line2.reshape(4,)[:3])
            #   Find the similarity in angle between the normal of the triangle's face
            #   and a vector from the camera to any point on that triangle's face
            #   the latter works because the triangle exists entirely in a plane
            #   and the normal points in the same direction on any point (or position)
            #   on that plane
            #   Now, if you look for a result > 0.0, it filters for faces on the other side
            #   that normally won't be visible
            if np.dot(normal, p0.reshape(4,)[:3] - self.camera.position) < 0.0:
                should_draw = True
            
            #   normalized device coordinates (ndc)
            #   gotten from perspective division
            p0 = (mvp @ p0).reshape(4,)
            p0 = p0[:3] / p0[3]
            p1 = (mvp @ p1).reshape(4,)
            p1 = p1[:3] / p1[3]
            p2 = (mvp @ p2).reshape(4,)
            p2 = p2[:3] / p2[3]

            #   perspective division
            p0 = self.remap(p0[0:2], np.array(self.engine_ref.win_res))
            p1 = self.remap(p1[0:2], np.array(self.engine_ref.win_res))
            p2 = self.remap(p2[0:2], np.array(self.engine_ref.win_res))
            if should_draw:
                #   use polygons so they can be filled!
                pg.draw.polygon(self.layer, self.cols[3], [p0, p1, p2], width=1)

                # pg.draw.aaline(self.layer, col, p0, p1)
                # pg.draw.aaline(self.layer, col, p1, p2)
                # pg.draw.aaline(self.layer, col, p2, p0)
                
        self.engine_ref.screen.blit(self.layer, (0, 0))
        
    def draw_cube(self):
        """
            For each cube vertex,
            transform according to the model transformation,
            view transformation, and perspective, and then
            draw each triangle's points consecutively according to the indices
        """
        self.camera.update()

        # mvp = np.matmul(self.proj, np.matmul(self.view, self.cube_model))
        mvp = self.camera.proj @ self.camera.view @ self.cube_model
        col = pg.Color(255, 0, 0)

        for vert_idx in self.cube_indices:
            #   must ensure points are column vectors
            #   and that the w component is 1.0 for the translation
            p0 = np.array([*self.cube_verts[vert_idx[0]], 1.0]).reshape(4, 1)
            p1 = np.array([*self.cube_verts[vert_idx[1]], 1.0]).reshape(4, 1)
            p2 = np.array([*self.cube_verts[vert_idx[2]], 1.0]).reshape(4, 1)
            
            #   normalized device coordinates (ndc)
            p0 = (mvp @ p0).reshape(4,)
            p0 = p0[:3] / p0[3]
            p1 = (mvp @ p1).reshape(4,)
            p1 = p1[:3] / p1[3]
            p2 = (mvp @ p2).reshape(4,)
            p2 = p2[:3] / p2[3]
            #   perspective division
            p0 = self.remap(p0[0:2], np.array(self.engine_ref.win_res))
            p1 = self.remap(p1[0:2], np.array(self.engine_ref.win_res))
            p2 = self.remap(p2[0:2], np.array(self.engine_ref.win_res))

            pg.draw.aaline(self.layer, col, p0, p1)
            pg.draw.aaline(self.layer, col, p1, p2)
            pg.draw.aaline(self.layer, col, p2, p0)

        self.engine_ref.screen.blit(self.layer, (0, 0))
        