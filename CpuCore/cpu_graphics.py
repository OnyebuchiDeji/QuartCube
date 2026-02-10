from CpuCore.cpu_math import *
import pygame as pg

FOV = 100
NEAR = 0.1
FAR = 100
SPEED = 0.01
SENSITIVITY = 0.007

class Camera:
    def __init__(self, engineRef, position=(0.0, 0.0, 4.0), yaw=-90.0, pitch=0.0, mouseVisible=True, mouseCentering=True):
        self.engine_ref = engineRef
        self.aspect_ratio = engineRef.win_res[0] / engineRef.win_res[1]
        self.position: np.array = Vec([*position], dtype='float64')
        self.up: np.array = Vec([0.0, 1.0, 0.0], dtype="float64")
        self.right: np.array = Vec([1.0, 0.0, 0.0], dtype="float64")
        self.forward: np.array = Vec([0.0, 0.0, -1.0], dtype="float64")
        self.yaw: float = yaw
        self.pitch: float = pitch
        self.h_fov = np.pi / 3.0
        self.v_fov = self.h_fov * (1.0 / self.aspect_ratio)
        self.RIGHT = np.tan(self.h_fov / 2.0)
        self.LEFT = -self.RIGHT
        self.TOP = np.tan(self.v_fov / 2.0)
        self.BOTTOM = -self.TOP

        self.view = self.get_view_matrix()
        self.proj = self.get_projection_matrix()
        self.mouse_centering = False

        #   Make Mouse Invisible
        pg.mouse.set_visible(mouseVisible)

        #   Create mouse-centering event
        self.mouse_centering = mouseCentering
        
        if mouseCentering:
            self.mce_id = pg.event.custom_type()
            self.mce_event = pg.event.Event(self.mce_id)
            pg.time.set_timer(self.mce_event, 500)

    def update(self):
        ...
    
    def move(self):
        ...
    
    @staticmethod
    def normalize(vec: np.array):
        # return vec / np.sqrt(np.power(vec[0], 2) + np.power(vec[1], 2))
        # return vec / np.sqrt(np.sum(np.power(vec, 2)))
        #   small constant to prevent the zero division error
        return vec / (np.linalg.norm(vec) + 1e-7)

    def get_view_matrix(self):
        ##  np.lookAt(eye, center, up) -> np.mat4
        ##  eye - camera position
        ##  center - position of where camera is looking atexit
        ##  Normalized up vector, how the camera is oriented
        #
        ##return np.lookAt(self.position, np.vec3(0), self.up)
        #   The above was changed after camera controls were added because pf the fact that the camera was always looking...
        #   at the model's centre, its movement was being affected because its orientation was...
        #   fixed to the camera's centre
        return self.look_at()

    def get_projection_matrix(self):
        return self.perspective_v2()

    def look_at(self)->np.ndarray:
        """
            Because the nparray's parameters are arranged in a
            column-major order, the vectors to be used must be reshaped
            to shape (4, 1) before multiplication
        """
        #   column-major order is however to be used for this purpose
        #   althpugh not essential, it's would have been if
        #   I was manually passing this matrix to the shader
        # return np.array([
        #     [self.right[0], self.up[0], self.forward[0], 0],
        #     [self.right[1], self.up[1], self.forward[1], 0],
        #     [self.right[2], self.up[2], self.forward[2], 0],
        #     [-np.dot(self.right, self.position), -np.dot(self.up, self.position), -np.dot(self.forward, self.position), 1]
        # ])

        #   construct matrix in column-major order as in GLM
        #   the below is a cleaner column-major
        view = np.eye(4)
        view[0, :3] = self.right
        view[1, :3] = self.up
        view[2, :3] = -self.forward
        view[:3, 3] = -np.dot(view[:3, :3], self.position)    #   apply translation

        return view

    def perspective(self)->np.ndarray:
        """
            Invalid! Only works when camera is centered!
        """
        #   frustrum bounds
        t: float = np.tan(np.radians(FOV) / 2.0) * NEAR
        r: float = t * self.aspect_ratio
        m00: float = NEAR / r
        m11: float = 1.0 / t 
        m22: float = (FAR + NEAR)/(-FAR + NEAR)
        m23: float = (2.0 * FAR * NEAR) / (NEAR - FAR)
        return np.array([
            [m00, 0, 0, 0],
            [0, m11, 0, 0],
            [0, 0, m22, m23],
            [0, 0, -1, 0]
        ])

    def perspective_v2(self)->np.ndarray:
        """
            Proper formula that considers the right, left, top
            and bottom boundaries of the camera frustrum!
        """
        m00 = 2.0 / (self.RIGHT - self.LEFT)
        m11 = 2.0 / (self.TOP - self.BOTTOM)
        m22 = (FAR + NEAR) / (FAR - NEAR)
        m32 = -2.0 * NEAR * FAR / (FAR - NEAR)

        return np.array([
            [m00, 0.0, 0.0, 0.0],
            [0.0, m11, 0.0, 0.0],
            [0.0, 0.0, m22, 1.0],
            [0.0, 0.0, m32, 0.0]
        ])


#   takes what it needs and provides the matrices
class FirstPersonCamera(Camera):
    def __init__(self, engineRef, position=(0.0, 0.0, 4.0), yaw=-90.0, pitch=0.0, mouseVisible=False, mouseCentering=False):
        super().__init__(engineRef, position, yaw, pitch, mouseVisible, mouseCentering)

    def update(self):
        self.move()
        self.rotate()
        self.update_camera_vectors()
        ##  To update view matrix after moving
        self.view = self.get_view_matrix()

    def rotate(self):
        rel_x, rel_y = pg.mouse.get_rel()
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY
        ##  Limiting pitch movement to prevent unnatural movements up and down from Gimbal Lock
        self.pitch = max(-89, min(89, self.pitch))
    

    def update_camera_vectors(self):
        yaw, pitch = np.radians(self.yaw), np.radians(self.pitch)
        ##  Because the forward vectir is responsible for camera's orientation...
        ##  using geometry where the forward vector is like the resultant vector, and z and x are the right and up...
        ##  and one where forward is the resultant but now, y and x or z are the others
        self.forward[0] = np.cos(yaw) * np.cos(pitch)
        self.forward[1] = np.sin(pitch)
        self.forward[2] = np.sin(yaw) * np.cos(pitch)

        self.forward = self.normalize(self.forward)
        self.right = self.normalize(np.cross(self.forward, Vec([0.0, 1.0, 0.0])))
        self.up = self.normalize(np.cross(self.right, self.forward))

    def move(self):
        velocity = SPEED * self.engine_ref.delta_time
        key = pg.key.get_pressed()
        if key[pg.K_w]:
            self.position += self.forward * velocity
        if key[pg.K_s]:
            self.position -= self.forward * velocity
        if key[pg.K_a]:
            self.position -= self.right * velocity
        if key[pg.K_d]:
            self.position += self.right * velocity
        if key[pg.K_q]:
            self.position += self.up * velocity
        if key[pg.K_e]:
            self.position -= self.up * velocity

   
class ArrowCamera(Camera):
    def __init__(self, engineRef, position=(0.0, 0.0, 4.0), yaw=-90, pitch=0.0, mouseVisible=False, mouseCentering=False):
        super().__init__(engineRef, position, yaw, pitch, mouseVisible, mouseCentering)

    def update(self):
        self.move()
        self.view = self.get_view_matrix()
    
    def move(self):
        velocity = (SPEED + 0.005) * self.engine_ref.delta_time
        angular_velocity = (SPEED + 0.04) * SENSITIVITY * self.engine_ref.delta_time
        key = pg.key.get_pressed()
        if key[pg.K_w]:
            self.position += self.forward * velocity
        if key[pg.K_s]:
            self.position -= self.forward * velocity
        if key[pg.K_a]:
            self.position -= self.right * velocity
        if key[pg.K_d]:
            self.position += self.right * velocity
        if key[pg.K_q]:
            self.position += self.up * velocity
        if key[pg.K_e]:
            self.position -= self.up * velocity
        if key[pg.K_LEFT]:
            self.camera_yaw(angular_velocity)
        if key[pg.K_RIGHT]:
            self.camera_yaw(-angular_velocity)
        if key[pg.K_UP]:
            self.camera_pitch(angular_velocity)
        if key[pg.K_DOWN]:
            self.camera_pitch(-angular_velocity)
        
    def camera_yaw(self, angle):
        rotate = rotate_y(angle)
        self.forward = (Vec([*self.forward, 1.0]) @ rotate)[:3]
        self.right = (Vec([*self.right, 1.0]) @ rotate)[:3]
        self.up = (Vec([*self.up, 1.0]) @ rotate)[:3]
    
    def camera_pitch(self, angle):
        rotate = rotate_x(angle)
        self.forward = (Vec([*self.forward, 1.0]) @ rotate)[:3]
        self.right = (Vec([*self.right, 1.0]) @ rotate)[:3]
        self.up = (Vec([*self.up, 1.0]) @ rotate)[:3]