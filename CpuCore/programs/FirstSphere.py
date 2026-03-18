
import pygame as pg
from CpuCore.cpu_math import *
from CpuCore.programs._program import Program
from CpuCore.cpu_graphics import RadialCamera

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..cpu_engine import Engine

    
class FirstSphere(Program):
    def __init__(self, EngineRef: "Engine"):
        super().__init__(EngineRef, EngineRef.win_res)
        ########################
        #   It's best to leave the
        #   world center as the origin (0, 0, 0)
        ########################
        self.camera = RadialCamera(self.engine_ref,
                            # worldCentre=(EngineRef.win_res[0]//2,
                            #             EngineRef.win_res[1], 0),
                            camRadius=40,
                            position=(0, 0, 40),
                            mouseVisible=False, mouseCentering=True)
        self.sphere_verts = []
        self.run_once = True


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
        # print("tVec: ", tVec2)
        # print("sourceRangeX: ", sourceRangeX)
        # print("sourceRangeY: ", sourceRangeY)
        # print("targetRangeX: ", targetRangeX)
        # print("targetRangeY: ", targetRangeY)

        remaped_tx = self.remap31(tVec2[0], sourceRangeX, targetRangeX)

        remaped_ty = self.remap31(tVec2[1], sourceRangeY, targetRangeY)

        return Vec([remaped_tx, remaped_ty])
        

    def draw_point(self, x, y, radius=10, color=(255,255,255)):
        pg.draw.circle(self.layer, color, (x, y), radius)


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
        sphere_rad = 200
        self.draw_sphere_v2(sphere_rad)


    def create_sphere_verts_v2(self, resolution: int = 40):
        """
            Creates a unit sphere
            x = rsin(theta) * cos(phi)
            y = rsin(theta) * sin(phi)
            z = rcos(theta)
            where theta is the vertical inclination (latitude)
            and phi is the azimuth angle (longitude)
            
            Also, the ranges used for `lon` and `lat`
            were not right here. But it works for now
        """
        for idx in range(0, resolution + 1, 1):
            lon: float = self.remap31(idx, Vec([0, resolution]), Vec([-np.pi, np.pi]))
            for idy in range(0, resolution + 1, 1):
                lat: float = self.remap31(idy, Vec([0, resolution]), Vec([-np.pi / 2, np.pi / 2]))
                x: float = np.sin(lon) * np.cos(lat)
                y: float = np.sin(lon) * np.sin(lat)
                z: float = np.cos(lon)
                self.sphere_verts.append(Vec([x, y, z]))

    def draw_sphere_v2(self, radius: float, resolution:int = 40):
        """
            Takes unit sphere's vertices and uses
            the remap_vector method with a factor, `fct`
            that uses the circle's radius to affect the mapping
        """
        if self.run_once:
            self.create_sphere_verts_v2()
            self.run_once = False
        for vert in self.sphere_verts:
            #   transform with camera

            vp = self.camera.proj @ self.camera.view
            vert = vp @ (Vec([*vert, 1]).reshape(4, 1)).reshape(4,)
            #   don't forget the perspective division
            vert = vert[0:3] / vert[3]

            #   try 5: the best
            fct = 0.125 * (self.engine_ref.win_res[0] / radius)

            vert = self.remap_vector(vert[0:2],
                Vec([-fct, fct]),
                Vec([fct, -fct]),
                Vec([0, self.engine_ref.win_res[0]]),
                Vec([0, self.engine_ref.win_res[1]]))

        
            # print("Point: ", point)
            self.draw_point(vert[0], vert[1], radius=4)


    def create_sphere_verts_v1(self, radius, resolution: int = 40):
        """
            idx is used to get the horizontal
            or longitudinal or azimuthal angles
            hence why appropriately `idx`
            while `idy` is for the inclination or
            vertical tilt or latitude
        
            Note the range(0, res + 1)
            is because these values will be mapped
            to be between -PI/2 and PI/2 or -PI and PI
            accordingly 

            Formula:
            x = rsin(theta) * cos(phi)
            y = rsin(theta) * sin(phi)
            z = rcos(theta)
            where theta is the vertical inclination (latitude)
            and phi is the azimuth angle (longitude)

            Also, the ranges used for `lon` and `lat`
            were not right here. But it works for now

        """
        for idx in range(0, resolution + 1, 1):
            lon: float = self.remap31(idx, Vec([0, resolution]), Vec([-np.pi, np.pi]))
            for idy in range(0, resolution + 1, 1):
                lat: float = self.remap31(idy, Vec([0, resolution]), Vec([-np.pi / 2, np.pi / 2]))
                x: float = radius * np.sin(lon) * np.cos(lat)
                y: float = radius * np.sin(lon) * np.sin(lat)
                z: float = radius * np.cos(lon)
                self.sphere_verts.append(Vec([x, y, z]))                

    def draw_sphere_v1(self, radius: float, resolution:int = 40):
        """
            I was not applying perspective division
            here, essentially resulting in orthographic
            coordinates. Hence, all the suggestions below
            are based on this.

            Also, because of this, the zoom-in/zoom-out of
            camera wasn't working

            The drawing method uses a radius.
            The only problem the radius values introduced
            was remapping the coordinates of the generated
            sphere from -1 -> 1 * radius to the
            screen's local coordinate range
            but in a way that considers the radius values
            so that the size changes in proportion to the
            radius.

            E.g. When without radius, that is, `vert / radius`
            I can use the range remap:
                #   try 2: almost
                point = self.remap_vector(point,
                    Vec([-1, 1]), Vec([1, -1]),
                    Vec([0,self.engine_ref.win_res[0]]),
                    Vec([0, self.engine_ref.win_res[1]]))

                because now the coordinates are within range 
                -1->1.
                But note that the coordinates are directly
                in this range.
                So when mapped to the screen's coordinate range,
                the result is large.

            Solution:
                Use a range larger than -1 to 1, so that the
                proportion of the normalised sphere coordinates
                will be smaller, and thus will appear smaller
                when remapped to the screen coordinate range.

                #   try 3: much closer
                point = self.remap_vector(point,
                    Vec([-4, 4]), Vec([4, -4]),
                    Vec([0,self.engine_ref.win_res[0]]),
                    Vec([0, self.engine_ref.win_res[1]]))
            Caveat:
                This disregards the need for the radius parameter
                as scale is handled by the remap source range

            New Solution:
                Use with radius, then use the below remap:

                This solution works because now the sphere's
                vertices are in range -radius->radius.

                But if I used this solution:

                    #   try 4: worth it but nope!

                    # fct = 1
                    # point = self.remap_vector(point,
                    #     Vec([-radius * fct, radius * fct]),
                    #     Vec([radius * fct, -radius * fct]),
                    #     Vec([0, self.engine_ref.win_res[0]]),
                    #     Vec([0, self.engine_ref.win_res[1]]))

                The remap result will be as with the first solution
                of the method that removes the radius.

                However, by increasing fct, it can make the results better.
                But still, it doesn't consider the radius

            Best Solution:
                This puts the radius range in reference to the
                engine's width resolution.

                Note how both for the sourceRangeX and sourceRangeY
                the width resolution value is used.
                This is because the source has to be a square range
                just as the original vertices of the sphere are in
                a square range

                fct = self.engine_ref.win_res[0] // 2

                point = self.remap_vector(point,
                    Vec([-fct, fct]),
                    Vec([fct, -fct]),
                    Vec([0, self.engine_ref.win_res[0]]),
                    Vec([0, self.engine_ref.win_res[1]]))

                This considers the radius value, and hence
                is the best
        """
        if self.run_once:
            self.create_sphere_verts_v1(radius)
            self.run_once = False

        for vert in self.sphere_verts:
            #   transform with camera
            # point = vert / radius   # without radius
            point = vert              #  with radius

            ####################################
            #   the below is the right order of multiplying
            #   the matrices here. A different order
            #   will cause a sphere with bad persepective
            #   leading to a more oval-like shape
            ####################################
            # vp = self.camera.view @ self.camera.proj
            # point = (Vec([*point, 1]) @ vp)[0:3]
            ####################################
            #   OR
            ####################################
            # vp = self.camera.proj @ self.camera.view
            # point = (vp @ Vec([*point, 1]).reshape(4, 1)).reshape(4,)[0:3]
            ####################################
            vp = self.camera.proj.transpose() @ self.camera.view
            # vp = self.camera.view @ self.camera.proj
            # vp =  self.camera.view.transpose() @ self.camera.proj.transpose()
            # vp = self.camera.proj.transpose() @ self.camera.view.transpose()
            # point = (Vec([*point, 1]) @ vp)[0:3]
            point = (vp @ Vec([*point, 1]).reshape(4, 1)).reshape(4,)[0:3]

            #   no perspective division was considered beforehand
            #   so don't uncomment | test the orthographic
            # point = point[0:3] / point[2]

            #   try 1: nah
            # point = self.remap_vector(point,
            #     Vec([-1, 1]), Vec([1, -1]),
            #     Vec([0, radius]),
            #     Vec([0, radius]))

            #   try 2: almost
            # point = self.remap_vector(point,
            #     Vec([-1, 1]), Vec([1, -1]),
            #     Vec([0,self.engine_ref.win_res[0]]),
            #     Vec([0, self.engine_ref.win_res[1]]))

            #   try 3: much closer
            # point = self.remap_vector(point,
                # Vec([-4, 4]), Vec([4, -4]),
                # Vec([0,self.engine_ref.win_res[0]]),
                # Vec([0, self.engine_ref.win_res[1]]))

            #   try 4: worth it but nope!
            # fct = 5
            # point = self.remap_vector(point,
            #     Vec([-radius * fct, radius * fct]),
            #     Vec([radius * fct, -radius * fct]),
            #     Vec([0, self.engine_ref.win_res[0]]),
            #     Vec([0, self.engine_ref.win_res[1]]))

            #   try 5: the best
            fct = self.engine_ref.win_res[0] // 2

            point = self.remap_vector(point,
                Vec([-fct, fct]),
                Vec([fct, -fct]),
                Vec([0, self.engine_ref.win_res[0]]),
                Vec([0, self.engine_ref.win_res[1]]))

        
            # print("Point: ", point)
            self.draw_point(point[0], point[1], radius=4)

                        