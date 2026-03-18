""" 
    This program renders a cube but with different controls.
    Firstly, rotations are now done with Arrow Keys
    and the mouse directly affects the Cube Model,
    rotating it with quaternions around its own axis!

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

    
class QuartCube(Program):
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
        
        self.camera = ArrowCamera(self.engine_ref, position=(0, 0, 100), mouseVisible=True, mouseCentering=True)
        #   view (camera at 0, 0, 5, looking at origin)
        self.cols = [pg.Color(255, 0, 0), pg.Color(0, 255, 0), pg.Color(0, 0, 255), pg.Color(255, 255, 255)]
        self.bg_cols = [(23, 39.5, 39.5), (46, 79, 79), (12, 12, 12)]
        # self.init_cube_model()

    def init_cube_model(self):
        """
            Values here for translation should be between -1 and 1
            because this is directly applied on the Cube's Vertices

            Also, for translation, the point or matrix to be transformed
            should be on the left

            For unknown reasons, the translation matrix doesn't work properly
            The Z-axis of the translation works only when the values are between
            the range -1 and 1

            The X and Y transalations just do not work!

            Rotation Matrices Work!

            Upon research, the answer came to me on why the translation
            wasn't working.
                *   The translate() function is correct, and the application to the cube model
                is also correct.
                *   The reason it was not working is due to the nature of the translate matrix.

                For other matrices, M, to be applied on a vector V
                    -   M * V works.
                    -   But for the translate matrix, only
                        V * M works.
                Due to this, because in the `draw` method, the model matrix mM
                is applied to the Cube's vertices in the order:
                    -   M * V
                when M contains the translation matrix, the result was completely wrong!
            
            Caveat:
                The issue is that other transformations added to the model even after translate
                may be affected by the new order of multiplication, leading to wrong results
            
            Core Cause:
                Depending whether one treats their vectors' shape, either as a column vector
                or row vectore, there is a difference in how the parameters of a Matrix will be arranged.
                Essentially, given a column vector (shape: 4, 1 or 4, 1), a column-major matrix is needed
                And given a row vector, shaped (1, 4), a row-major matrix is needed.

                Between a column-major and row-major matrix, although the parameters' formulas remain the same,
                a column-major and row-major matrix are essentially transposes of each other.

                The good thing is that this column-major (column vertices) vs row-major (row vertices)
                change only affects the translation matrix (I am semi-certain)

                because of how matrix application works with the last rows and last columns of
                4x4 matrices
                
            Solution:
                Make a `translate_column_major` matrix that works on column vectors.
            
            Now, all transformations work!
        """
        
        #   testing normal translations
        # translation_mat = translate((0.0, 0.0, -2.5))
        # self.cube_model = translate((-1.0, 1.5, 0.0))
        self.cube_model @= translate_column_major((-1.0, 1.5, 0.0))
        rotation_mat = rotate_yaw(45)
        rotation_mat @= rotate_pitch(22.5)
        rotation_mat @= rotate_roll(30)
        self.cube_model = rotation_mat @ scale(2.0) @ self.cube_model

        #   testing rotation using quaternions
        # rel_x, rel_y = pg.mouse.get_rel()
        # self.camera.yaw += rel_x * 0.10
        # self.camera.pitch -= rel_y * 0.1

        ################################
        #   Limiting pitch movement to prevent unnatural movements
        #   up and down from Gimbal Lock
        #   Actually, quaternions are not affected by Gimbal Lock
        #   so no need to limit it
        # self.camera.pitch = max(-89, min(89, self.camera.pitch))
        ################################

        # rot_mat = quaternion_single_axis_rotation((0, 1, 0), np.radians(50))
        # # rot_mat = quaternion_single_axis_rotation((0, 0, 1), np.radians(self.camera.pitch))
        # # rot_mat @= quaternion_single_axis_rotation((0, 1, 0),np.radians(self.camera.yaw))
        
        # self.cube_model = self.cube_model @ rot_mat

        ...
        
    
    def update_orientation(self):
        """
            Gets Mouse Positions and Update Cube's Orientation
            using quaternions.

            The quaternion operation used here obtains a quaternion
            from Euler Axis-Angle data, and then converts the quaternion
            to a rotation matrix!
        """
        rel_x, rel_y = pg.mouse.get_rel()
        yaw_angle = rel_x * 0.07
        pitch_angle = rel_y * 0.07
        ##  Limiting pitch movement to prevent unnatural movements up and down
        # self.camera.pitch = max(-89, min(89, self.camera.pitch))

        #   note the axis matches the angle
        rot_mat = quaternion_single_axis_rotation((0, 0, 1), np.radians(pitch_angle))
        rot_mat @= quaternion_single_axis_rotation((0, 1, 0), np.radians(yaw_angle))
        
        self.cube_model = self.cube_model @ rot_mat


    def update(self):
        self.layer.fill(self.bg_cols[2])   #   dark slate gray
        self.update_orientation()
        self.draw_cube()
    
    def remap01(self, a: float, b: float, t: float):
        return (t - a) / (b - a)

    def remap(self, sourceVec2: np.array, targetVec2: np.array):
        remapedSource = np.array([self.remap01(-1, 1, sourceVec2[0]),
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
            p0 = np.array([*self.cube_verts[vert_idx[0]], 1.0]).reshape(4, 1)
            p1 = np.array([*self.cube_verts[vert_idx[1]], 1.0]).reshape(4, 1)
            p2 = np.array([*self.cube_verts[vert_idx[2]], 1.0]).reshape(4, 1)
            
            """
                must apply model w transform on points first
                before depth culling! if a triangle's normal is not aligned
                to the camera's forward vecctor, don't append that triangle's points
            """
            should_draw = False

            p0 = self.cube_model @ p0
            p1 = self.cube_model @ p1
            p2 = self.cube_model @ p2
            # p0 = (p0.reshape(1, 4) @ self.cube_model).reshape(4, 1)
            # p1 = (p1.reshape(1, 4) @ self.cube_model).reshape(4, 1)
            # p2 = (p2.reshape(1, 4) @ self.cube_model).reshape(4, 1)
            # p0mv = mv @ p0
            # p1mv = mv @ p1
            # p2mv = mv @ p2
            # line1 = p1mv - p0mv
            # line2 = p2mv - p1mv

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
                
    def draw_cube_v2b(self):
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

        # mvp = self.camera.proj @ self.camera.view @ self.cube_model


        for vert_idx in self.cube_indices:
            #   must ensure points are column vectors and that the w component is 1.0 for the translation
            #   three points of triangle
            p0 = np.array([*self.cube_verts[vert_idx[0]], 1.0]).reshape(4, 1)
            p1 = np.array([*self.cube_verts[vert_idx[1]], 1.0]).reshape(4, 1)
            p2 = np.array([*self.cube_verts[vert_idx[2]], 1.0]).reshape(4, 1)
            
            
            """
                must apply model w transform on points first
                before depth culling! if a triangle's normal is not aligned
                to the camera's forward vecctor, don't append that triangle's points
            """
            should_draw = False

            # p0 = self.cube_model @ p0
            # p1 = self.cube_model @ p1
            # p2 = self.cube_model @ p2

            """
                The below was needed to debug the translation matrix
                it shows me requiring to reshape the points to row vector shape
                and requires changing the order of the matrix multiplication.

                This was something that only affected the translation matrix.
                Hence, I had to reshape the points back to column vectors so
                that the view-projection matrices can work on them properly
            """
            p0 = (p0.reshape(1, 4) @ self.cube_model).reshape(4, 1)
            p1 = (p1.reshape(1, 4) @ self.cube_model).reshape(4, 1)
            p2 = (p2.reshape(1, 4) @ self.cube_model).reshape(4, 1)
            # p0mv = mv @ p0
            # p1mv = mv @ p1
            # p2mv = mv @ p2
            # line1 = p1mv - p0mv
            # line2 = p2mv - p1mv

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
            p0 = p0[:3] / p0[3] #   perspective division
            p1 = (vp @ p1).reshape(4,)
            p1 = p1[:3] / p1[3] #   perspective division
            p2 = (vp @ p2).reshape(4,)
            p2 = p2[:3] / p2[3] #   perspective division


            if should_draw:
                p0 = self.remap(p0[0:2], np.array(self.engine_ref.win_res))
                p1 = self.remap(p1[0:2], np.array(self.engine_ref.win_res))
                p2 = self.remap(p2[0:2], np.array(self.engine_ref.win_res))
                #   use polygons so they can be filled!
                pg.draw.polygon(self.layer, self.cols[3], [p0, p1, p2], width=1)
    
    def draw_cube_v2(self):
        """
            Tried to fix the issues with translation here.
            But seems like this affects none of it!

            But instead discovered that culling faces after applying view and
            depth transforms properly works with the Cube's model transforms!
        """
        self.camera.update()

        mvp = self.camera.proj @ self.camera.view @ self.cube_model


        for vert_idx in self.cube_indices:
            #   must ensure points are column vectors and that the w component is 1.0 for the translation
            #   three points of triangle
            p0 = np.array([*self.cube_verts[vert_idx[0]], 1.0]).reshape(4, 1)
            p1 = np.array([*self.cube_verts[vert_idx[1]], 1.0]).reshape(4, 1)
            p2 = np.array([*self.cube_verts[vert_idx[2]], 1.0]).reshape(4, 1)
            
            
            #   normalized device coordinates (ndc)
            #   gotten from perspective division
            p0 = (mvp @ p0).reshape(4,)
            p0 = p0[:3] / p0[3]
            p1 = (mvp @ p1).reshape(4,)
            p1 = p1[:3] / p1[3]
            p2 = (mvp @ p2).reshape(4,)
            p2 = p2[:3] / p2[3]

            #   must apply model-view transform on points first
            #   depth culling! if a triangle's normal is not aligned
            #   to the camera's forward vecctor, don't append that triangle's points
            should_draw = False
            # mv = self.camera.view @ self.cube_model
            # p0mv = mv @ p0
            # p1mv = mv @ p1
            # p2mv = mv @ p2
            # line1 = p1mv - p0mv
            # line2 = p2mv - p1mv
            # normal = np.cross(line1.reshape(4,)[:3], line2.reshape(4,)[:3])

            line1 = p1 - p0
            line2 = p2 - p1
            normal = np.cross(line1[:3], line2[:3])

            if np.dot(normal, p0[:3] - self.camera.position) < 0.0:
                should_draw = True

            #   perspective division
            if should_draw:
                p0 = self.remap(p0[0:2], np.array(self.engine_ref.win_res))
                p1 = self.remap(p1[0:2], np.array(self.engine_ref.win_res))
                p2 = self.remap(p2[0:2], np.array(self.engine_ref.win_res))
                #   use polygons so they can be filled!
                pg.draw.polygon(self.layer, self.cols[3], [p0, p1, p2], width=1)
       
    def draw_cube_v1(self):
        """
            OG Method of Drawing Cube involving Culling Faces
            with points that have not yet been transformed.

            It doesn't work well after applying cube's model transforms
        """
        self.camera.update()

        mvp = self.camera.proj @ self.camera.view @ self.cube_model


        for vert_idx in self.cube_indices:
            #   must ensure points are column vectors and that the w component is 1.0 for the translation
            #   three points of triangle
            p0 = np.array([*self.cube_verts[vert_idx[0]], 1.0]).reshape(4, 1)
            p1 = np.array([*self.cube_verts[vert_idx[1]], 1.0]).reshape(4, 1)
            p2 = np.array([*self.cube_verts[vert_idx[2]], 1.0]).reshape(4, 1)
            
            should_draw = False
            line1 = p1 - p0
            line2 = p2 - p1
            normal = np.cross(line1.reshape(4,)[:3], line2.reshape(4,)[:3])

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
            if should_draw:
                p0 = self.remap(p0[0:2], np.array(self.engine_ref.win_res))
                p1 = self.remap(p1[0:2], np.array(self.engine_ref.win_res))
                p2 = self.remap(p2[0:2], np.array(self.engine_ref.win_res))
                #   use polygons so they can be filled!
                pg.draw.polygon(self.layer, self.cols[3], [p0, p1, p2], width=1)
                