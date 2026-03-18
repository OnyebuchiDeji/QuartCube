"""
    Demonstration of controlling the orientation of a Cube
    with quaternions.

    This version uses another method for rotating the cube
    where a point is directly rotated by the quaternion
    instead of by a rotation matrix created by said quaternion 

    
    Article on quaternions:
    https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
"""


import pygame as pg
from CpuCore.cpu_math import *
from CpuCore.programs._program import Program
from CpuCore.cpu_graphics import ArrowCamera

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..cpu_engine import Engine

    
class QuartCube2(Program):
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
        
        self.camera = ArrowCamera(self.engine_ref, position=(0, 0, 100), mouseVisible=False, mouseCentering=True)
        #   view (camera at 0, 0, 5, looking at origin)
        self.cols = [pg.Color(255, 0, 0), pg.Color(0, 255, 0), pg.Color(0, 0, 255), pg.Color(255, 255, 255)]
        self.bg_cols = [(23, 39.5, 39.5), (46, 79, 79), (12, 12, 12)]
        # self.init_cube_model()
        self.quart = np.array([])
        self.rel_x = 0.0
        self.rel_y = 0.0

    def init_cube_model(self):

        #   testing rotation using quaternions
        # rel_x, rel_y = pg.mouse.get_rel()
        # self.camera.yaw += rel_x * 0.10
        # self.camera.pitch -= rel_y * 0.1
        # ##  Limiting pitch movement to prevent unnatural movements up and down
        # self.camera.pitch = max(-89, min(89, self.camera.pitch))
        # rot_mat = quaternion_single_axis_rotation((0, 1, 0), 50)
        # # rot_mat = quaternion_single_axis_rotation((0, 0, 1), self.camera.pitch)
        # # rot_mat @= quaternion_single_axis_rotation((0, 1, 0), self.camera.yaw)
        
        # self.cube_model = self.cube_model @ rot_mat

        ...
        
    
    def update_quaternion(self):
        """
            Gets Mouse Positions and Update Quaternion
            that Updates Cube's Orientation

            The quaternion operation used here obtains a quaternion
            and uses it to directly transform points

            As you can see below, by multiplying different rotation
            quaternions that rotate for different axis, I combine
            their effect into one quaternion.

            This enables rotation in both the pitch and yaw angles

            Now, the order in which the different-axis-rotating
            quaternions are multiplied by each other does not matter!
                pitch-then-yaw and yaw-then-pitch have the same effects!

            This happens despite the non-commutative properties.
            Perhaps this scenarion falls within the "Special Cases"
            where commutative properties in multiplication are present

            Though I suspect something changed, I did not notice
            it when testing both pitch-then-yaw vs. yaw-then-pitch
            multiplications.
        """
        rel_xy = pg.mouse.get_rel()
        self.rel_x += rel_xy[0]
        self.rel_y += rel_xy[1]
        yaw_angle = self.rel_x * 0.07
        pitch_angle = self.rel_y * 0.07

        #   note the axis matches the angle

        #   pitch-then-yaw
        # self.quart = quaternion_from_axis_angle((0, 0, 1), pitch_angle)
        # self.quart = quaternion_multiply(self.quart, quaternion_from_axis_angle((0, 1, 0), yaw_angle))
        
        #   yaw-then-pitch
        self.quart = quaternion_from_axis_angle((0, 1, 0), np.radians(yaw_angle))
        self.quart = quaternion_multiply(self.quart, quaternion_from_axis_angle((0, 0, 1), np.radians(pitch_angle)))


    def update(self):
        self.layer.fill(self.bg_cols[2])   #   dark slate gray
        self.update_quaternion()
        self.draw_cube()
    
    def remap01(self, a: float, b: float, t: float):
        return (t - a) / (b - a)

    def remap(self, sourceVec2: np.array, targetVec2: np.array):
        """
            Used to remap the transformed points that are still
            in value range -1->1 for both x and y axes to be:

            -1 -> 1 (X-components) --->> New range: 0 -> width
            -1 -> 1 (Y-components) --->> Flipped: 1 -> -1
                                    --->> New range: 0 -> height
            the latter, for the y-components, is to compensate
            with pygame's y-axis flip
        """
        remapedSource = Vec([self.remap01(-1, 1, sourceVec2[0]),
                                self.remap01(1, -1, sourceVec2[1])])
        return remapedSource * targetVec2

    def draw_cube(self):
        """
            Since Perspective doesn't directly affect the camera, and the original
            depth-culling was done on the points, and from trial-and-error
            performing the model transform on the Cube's points before depth-culling
            has appeared to be the best.

            The conclusion was reached after noticing that even after applying
            a model-view transform before depth culling, errors occured.

            The second-best is applying all mvp transforms before depth-culling 
            as that didn't cause any issues with the rendering of triangles!
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
                before depth culling! if a triangle's normal is not aligned
                to the camera's forward vecctor, don't append that triangle's points
            """
            should_draw = False

            p0 = self.cube_model @ p0
            p1 = self.cube_model @ p1
            p2 = self.cube_model @ p2

            """
                Note, the `quaternion_rotation_pure` function needs a normal shaped
                array hence the reshape
                Then the Vec([*[...], 1.0]) is done to get back the w component for 
                the subsequent projection-view multiplications
                isActive doesn't show any very visible difference whether it's True or False
            """
            p0 = Vec([*quaternion_rotation_pure(p0.reshape(4,), self.quart, isActive=False), 1.0]).reshape(4, 1)
            p1 = Vec([*quaternion_rotation_pure(p1.reshape(4,), self.quart, isActive=False), 1.0]).reshape(4, 1)
            p2 = Vec([*quaternion_rotation_pure(p2.reshape(4,), self.quart, isActive=False), 1.0]).reshape(4, 1)

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