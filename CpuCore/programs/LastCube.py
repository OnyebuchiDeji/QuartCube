""" 
    This LastCube demonstrates drawing of a Cube
    and the proper application of rotation matrices
    that support column vector multiplications.

    Hence, the rotation matrices must be ordered in a way that
    supports column vectors, which is the Column-Major ordering.
    This is simply the transpose of their original counterparts

    Date: 06-02-2026
"""

import pygame as pg
from CpuCore.cpu_math import *
from CpuCore.programs._program import Program
from CpuCore.cpu_graphics import FirstPersonCamera

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..cpu_engine import Engine


class LastCube(Program):
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

        self.init_cube_model()


    def update_orientation(self):
        """Gets Mouse Positions and Update Cube's Orientation"""
        ...
    
    def init_cube_model(self):
        self.cube_model @= translate_column_major((-1.0, 1.5, 0.0))

        """
            The effect of rotating around the Y-axis for a 3d model
            around the certain axis, with the axis defined by one's line of sight
            when looking at the cube from above, is meant to be such that the rotation
            is anticlockwise instead of clockwise.

            However, the effect of the normal `rotate_yaw` rotates the cube in a Clockwise direction.
            This is because this rotation matrix is not suitable for multiplication with column vectors
            but for row vectors.

            The correct form is the transpose of the original row-vector-compatible (row-major) matrix,
            which is its column-major form

            Notice the difference in the results of stacking rotations
            between the `row-major` rotation matrices vs
            those of their `column-major` form 

            Also, to apply the matrices on the cube model's matrix,
            this is the proper order to apply it:

            `self.cube_model = self.cube_model @ rotation_mat`
            or
            `self.cube_model @= rotation_mat`
        """
        # rotation_mat = rotate_yaw(45)
        # rotation_mat @= rotate_pitch(22.5)
        # rotation_mat @= rotate_roll(30)
        
        rotation_mat = rotate_yaw_column_major(45)
        rotation_mat @= rotate_pitch_column_major(22.5)
        rotation_mat @= rotate_roll_column_major(30)
        
        ##  wrong
        # self.cube_model = rotation_mat @ scale(1.0) @ self.cube_model

        ##  right
        # self.cube_model = self.cube_model @ rotation_mat
        ##  or
        self.cube_model @= scale(1.0)
        self.cube_model @= rotation_mat
        ...


    def update(self):
        self.update_orientation()
        self.layer.fill(self.bg_cols[2])   #   dark slate gray
        self.draw_cube()
    
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


    def draw_cube(self):
        """
            For each cube vertex,
            transform according to the model transformation,
            view transformation, and perspective, and then
            draw each triangle's points consecutively according to the indices
        """
        self.camera.update()

        for vert_idx in self.cube_indices:
            #   must ensure points are column vectors and that the w component is 1.0 for the translation
            #   three points of triangle
            p0 = Vec([*self.cube_verts[vert_idx[0]], 1.0]).reshape(4, 1)
            p1 = Vec([*self.cube_verts[vert_idx[1]], 1.0]).reshape(4, 1)
            p2 = Vec([*self.cube_verts[vert_idx[2]], 1.0]).reshape(4, 1)
            
            """
                must apply model w transform on points first
                before back-face culling! if a triangle's normal is not aligned
                to the camera's forward vecctor, don't append that triangle's points
            """
            should_draw = False

            p0 = self.cube_model @ p0
            p1 = self.cube_model @ p1
            p2 = self.cube_model @ p2

            line1 = p1 - p0
            line2 = p2 - p1
            normal = np.cross(line1.reshape(4,)[:3], line2.reshape(4,)[:3])

            if np.dot(normal, p0.reshape(4,)[:3] - self.camera.position) < 0.0:
            # if np.dot(normal, self.camera.forward) < 0.0:
                should_draw = True
            
            #   normalized device coordinates (ndc)
            #   gotten from perspective division
            vp = self.camera.proj @ self.camera.view
            p0 = (vp @ p0).reshape(4,)
            p0 = p0[:3] / p0[3]
            p1 = (vp @ p1).reshape(4,)
            p1 = p1[:3] / p1[3]
            p2 = (vp @ p2).reshape(4,)
            p2 = p2[:3] / p2[3]


            #   perspective division
            if should_draw:
                p0 = self.remap(p0[0:2], np.array(self.engine_ref.win_res))
                p1 = self.remap(p1[0:2], np.array(self.engine_ref.win_res))
                p2 = self.remap(p2[0:2], np.array(self.engine_ref.win_res))
                #   use polygons so they can be filled!
                pg.draw.polygon(self.layer, self.cols[3], [p0, p1, p2], width=1)
            