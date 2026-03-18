
import pygame as pg
from CpuCore.cpu_math import *
from CpuCore.programs._program import Program
from CpuCore.cpu_graphics import RadialCamera

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..cpu_engine import Engine

    
class MeshSphere(Program):
    def __init__(self, EngineRef: "Engine"):
        super().__init__(EngineRef, EngineRef.win_res)
        self.camera = RadialCamera(self.engine_ref,
                            camRadius=40,
                            position=(0, 0, 40),
                            mouseVisible=False, mouseCentering=True)
        self.sphere_verts = []
        self.run_once = True
        self.g_sphere_radius = 200


    def remap01(self, t: float, a: float, b: float) -> float:
        return (t - a) / (b - a)

    def remap31(self, t:float, sourceRange: np.ndarray, targetRange: np.ndarray) -> float:
        """
            Purer, more flexible remap.
            Remaps a value t originall within sourceRange, to its proportional
            in targetRange.
            Called `remap31` as it takes 3 arguments and returns one float
        """
        normalised_t = self.remap01(t, sourceRange[0], sourceRange[1])
        return targetRange[0] + normalised_t * (targetRange[1] - targetRange[0])

    def remap_vector(self, tVec2: np.ndarray,
        sourceRangeX: np.ndarray, sourceRangeY: np.ndarray,
        targetRangeX: np.ndarray, targetRangeY: np.ndarray):
        """
            Remap method for remapping a whole vector proportionally
            from its original sourceRange for both its X and Y axes
            to a new targetRange for both its X and Y axes
        """

        remaped_tx = self.remap31(tVec2[0], sourceRangeX, targetRangeX)

        remaped_ty = self.remap31(tVec2[1], sourceRangeY, targetRangeY)

        return Vec([remaped_tx, remaped_ty])
        

    def draw_point(self, x, y, radius=10, color=(255,255,255)):
        pg.draw.circle(self.layer, color, (x, y), radius)

    def draw_triangle(self, verts: list[tuple[float, float]], color=(255,255,255), fill=3):
        pg.draw.polygon(self.layer, color, (verts), width=3)


    def update(self):
        # self.layer.fill((75, 67, 69))   # dark ash
        self.layer.fill((54, 69, 79))   # charcoal
        if self.camera != None:
            self.camera.update()
        self.draw()

    def draw(self):
        """
            Draws sphere using longitude and latitude angles
        """
        self.draw_sphere_v3(resolution=40)


    def draw_triangle(self, verts: list[tuple[float, float]], color=(255,255,255), fill=3):
        pg.draw.polygon(self.layer, color, (verts), width=3)

    def transform_vert(self, vert:np.ndarray):
        #   transform with camera
        vp = self.camera.proj @ self.camera.view
        vert = vp @ (Vec([*vert, 1]).reshape(4, 1)).reshape(4,)
        #   don't forget the perspective division
        vert = vert[0:3] / vert[3]

        #   try 5: the best
        fct = 0.125 * (self.engine_ref.win_res[0] / self.g_sphere_radius)

        vert = self.remap_vector(vert[0:2],
            Vec([-fct, fct]),
            Vec([fct, -fct]),
            Vec([0, self.engine_ref.win_res[0]]),
            Vec([0, self.engine_ref.win_res[1]]))
        return vert


    def create_sphere_verts_v2(self, resolution: int = 40):
        """
            Creates a unit sphere properly
            with the right longitude and latitude values
            and ranges.
        """
        for idx in range(0, resolution + 1, 1):
            lon: float = self.remap31(idx, Vec([0, resolution]), Vec([0, 2 * np.pi]))
            for idy in range(0, resolution + 1, 1):
                lat: float = self.remap31(idy, Vec([0, resolution]), Vec([0, np.pi]))

                #   Mistakenly switched angles
                #   But it works as intended
                x: float = np.sin(lat) * np.cos(lon)
                y: float = np.sin(lat) * np.sin(lon)
                z: float = np.cos(lat)

                #   Correct
                self.sphere_verts.append(Vec([x, y, z]))

    def draw_sphere_v3(self, resolution:int = 40):
        """
            Draws Triangle Mesh with 2 Triangle Strips
            and applies depth culling.
            That is, dont' draw vertices of faces that
            are behind others
        """
        if self.run_once:
            self.create_sphere_verts_v2(resolution)
            self.run_once = False

        tri_verts1 = []
        tri_verts2 = []

        ##########################
        #   By increasing of `res_step`, one can reduce the number
        #   of triangle strips drawn and hence
        #   improve performance
        ##########################
        res_step = 2
        for idx in range(0, resolution, res_step):
            for idy in range(0, resolution, res_step):

                #   idv is index of current vertex

                #   First Triangle
                #   The below gets three vertices starting from idv
                #   then the one immediately below, then
                #   the one on the same row (height) as idv but different column
                idv0 = idx * (resolution + 1) + idy
                idv1 = idx * (resolution + 1) + idy + 1
                idv2 = (idx + 1) * (resolution + 1) + idy
                tri_verts1 = [
                    self.sphere_verts[idv0],
                    self.sphere_verts[idv1],
                    self.sphere_verts[idv2]
                ]

                #   Second triangle
                idv3 = idv1
                idv4 = (idx + 1) *  (resolution + 1) + idy + 1
                idv5 = idv2
                tri_verts2 = [
                    self.sphere_verts[idv3],
                    self.sphere_verts[idv4],
                    self.sphere_verts[idv5]
                ]

                should_draw = False

                line1 = tri_verts1[1] - tri_verts1[0]
                line2 = tri_verts1[2] - tri_verts1[1]

                normal = np.cross(line1, line2)

                if np.dot(normal, tri_verts1[0] - self.camera.position) < 0.0:
                    should_draw = True

                ##############################
                #   By putting the `transform_vert`
                #   logic in the branch along with the
                #   `draw_triangle`, it does not
                #   process vertices that will not be drawn
                #   and this increases performance by 10 fps 
                #   from 20 fps when the branch only stopped the
                #   triangle drawing to 30 fps now that the
                #   branch stops both the transform and drawing
                ##############################
                if should_draw:
                    for idv, vert in enumerate(tri_verts1):
                        tri_verts1[idv] = self.transform_vert(vert)
                    for idv, vert in enumerate(tri_verts2):
                        tri_verts2[idv] = self.transform_vert(vert)

                    self.draw_triangle([(v[0] , v[1]) for v in tri_verts1], fill=2)
                    self.draw_triangle([(v[0] , v[1]) for v in tri_verts2], fill=2)

    def draw_sphere_v2(self, resolution:int = 40):
        """
            Draws Triangle Mesh with 2 Triangle Strips
        """
        if self.run_once:
            self.create_sphere_verts_v2(resolution)
            self.run_once = False

        tri_verts1 = []
        tri_verts2 = []

        ##########################
        #   By increasing of `res_step`, one can reduce the number
        #   of triangle strips drawn and hence
        #   improve performance
        ##########################
        res_step = 3
        for idx in range(0, resolution, res_step):
            for idy in range(0, resolution, res_step):

                #   idv is index of current vertex

                #   First Triangle
                #   The below gets three vertices starting from idv
                #   then the one immediately below, then
                #   the one on the same row (height) as idv but different column
                idv0 = idx * (resolution + 1) + idy
                idv1 = idx * (resolution + 1) + idy + 1
                idv2 = (idx + 1) * (resolution + 1) + idy
                tri_verts1 = [
                    self.sphere_verts[idv0],
                    self.sphere_verts[idv1],
                    self.sphere_verts[idv2]
                ]

                #   Second triangle
                idv3 = idv1
                idv4 = (idx + 1) *  (resolution + 1) + idy + 1
                idv5 = idv2
                tri_verts2 = [
                    self.sphere_verts[idv3],
                    self.sphere_verts[idv4],
                    self.sphere_verts[idv5]
                ]

                for idv, vert in enumerate(tri_verts1):
                    tri_verts1[idv] = self.transform_vert(vert)
                self.draw_triangle([(v[0] , v[1]) for v in tri_verts1], fill=2)
                for idv, vert in enumerate(tri_verts2):
                    tri_verts2[idv] = self.transform_vert(vert)
                self.draw_triangle([(v[0] , v[1]) for v in tri_verts2], fill=2)


    def create_sphere_verts_v1(self, resolution: int = 40):
        """
            Creates a unit sphere
            But still uses the wrong angle values
            and ranges in the calculation of x,y,z
        """
        for idx in range(0, resolution + 1, 1):
            lon: float = self.remap31(idx, Vec([0, resolution]), Vec([-np.pi, np.pi]))
            for idy in range(0, resolution + 1, 1):
                lat: float = self.remap31(idy, Vec([0, resolution]), Vec([-np.pi / 2, np.pi / 2]))

                #   Mistakenly switched angles
                #   But it works as intended
                x: float = np.sin(lon) * np.cos(lat)
                y: float = np.sin(lon) * np.sin(lat)
                z: float = np.cos(lon)

                #   Correct
                self.sphere_verts.append(Vec([x, y, z]))


    def draw_sphere_v1(self, resolution:int = 40):
        """
            Draws Triangle Mesh with 2 Triangle Strips
        """
        if self.run_once:
            self.create_sphere_verts_v1(resolution)
            self.run_once = False

        tri_verts1 = []
        tri_verts2 = []

        ##########################
        #   By increasing of `res_step`, one can reduce the number
        #   of triangle strips drawn and hence
        #   improve performance
        ##########################
        res_step = 2
        ##########################
        #   Why is it `range(0, res, res_step)` 
        #   It's to reduce the range so that the last value
        #   for each iteration axis is not used.
        #   This is because in the code below, you 
        #   can see that to get some ids of next point
        #   like idv1, idv2, and idv4, `+ 1` is added
        #   to either the axes indices, `idx` or `idy`
        ##########################
        for idx in range(0, resolution, res_step):
            for idy in range(0, resolution, res_step):

                #   idv is index of current vertex

                #   First Triangle
                #   The below gets three vertices starting from idv
                #   then the one immediately below, then
                #   the one on the same row (height) as idv but different column
                idv0 = idx * (resolution + 1) + idy
                idv1 = idx * (resolution + 1) + idy + 1
                idv2 = (idx + 1) * (resolution + 1) + idy
                tri_verts1 = [
                    self.sphere_verts[idv0],
                    self.sphere_verts[idv1],
                    self.sphere_verts[idv2]
                ]

                #   Second triangle
                idv3 = idv1
                idv4 = (idx + 1) *  (resolution + 1) + idy + 1
                idv5 = idv2
                tri_verts2 = [
                    self.sphere_verts[idv3],
                    self.sphere_verts[idv4],
                    self.sphere_verts[idv5]
                ]

                for idv, vert in enumerate(tri_verts1):
                    tri_verts1[idv] = self.transform_vert(vert)
                self.draw_triangle([(v[0] , v[1]) for v in tri_verts1], fill=2)
                for idv, vert in enumerate(tri_verts2):
                    tri_verts2[idv] = self.transform_vert(vert)
                self.draw_triangle([(v[0] , v[1]) for v in tri_verts2], fill=2)

        
                # print("Point: ", point)
                # self.draw_point(vert[0], vert[1], radius=4)
