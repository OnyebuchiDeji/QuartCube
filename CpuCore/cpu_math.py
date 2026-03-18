import numpy as np


Vec = np.array

# Vec2 = np.zeros(2)
# Vec3 = np.zeros(3)
# Vec4 = np.zeros(4)
Mat3 = np.identity(3)   #   or np.eye(3)
Mat4 = np.identity(4)   #   or np.eye(4)

"""
    The Quaternion Functions
"""


def quaternion_from_axis_angle(axis: np.array, theta: float) -> np.ndarray:
    """
        Here, Euler's Axis-Angle Rotation is Converted to a Quaternion
        Axis: is a unit vector (x, y, z)
        Theta: amount of rotation around Axis 

        Return:
            An array of the coeffiecients of the Quaternion
    """
    q0: float = np.cos(theta / 2.0)
    q1 = axis[0] * np.sin(theta / 2.0)
    q2 = axis[1] * np.sin(theta / 2.0)
    q3 = axis[2] * np.sin(theta / 2.0)
    return np.array([q0, q1, q2, q3])

def quaternion_to_axis_angle(q0:float, q1:float, q2:float, q3:float) -> np.ndarray:
    """
        Here, the quaternion, represented by the four elements q0...q3
        is converted to Euler's Axis-Angle Representation

        Return:
            An array of the axis and angle magnitude (theta) that represent
            the Euler Axis-Angle
        
        Cases:
        identity_quaternion = np.array([1.0, 0.0, 0.0, 0.0])
            If the input quaternion is equal to the identity quaternion,
            no rotation is produced; hence the operation:
                `
                    x, y, z = np.array([q1, q2, q3]) / np.sin(theta / 2.0)
                `
            will fail, and theta will be zero
    """
    if q0 == 1.0:   # then theta == 0, so return x, y, z, theta = 1, 0, 0, 0
        return np.array([1.0, 0.0, 0.0, 0.0])   #   last value is theta

    theta : float = 2.0 * np.acos(q0) 
    x, y, z = np.array([q1, q2, q3]) / np.sin(theta / 2.0)
        
    return np.array([x, y, z, theta])


def quaternion_to_rotation_matrix(q: np.array) -> np.ndarray:
    """
        Returns 4 by 4 rotation matrix
    """
    q0, q1, q2, q3 = q
    
    f01: float = 2.0 * q0 * q1
    f02: float = 2.0 * q0 * q2
    f03: float = 2.0 * q0 * q3
    f12: float = 2.0 * q1 * q2
    f13: float = 2.0 * q1 * q3
    f23: float = 2.0 * q2 * q3

    #   those commented-out are another version of their counterparts
    # m00: float = q0 ** 2 + q1 ** 2 - q2 ** 2 - q3 ** 2
    m00: float = 1.0 - 2.0 * np.power(q2, 2) - 2.0 * np.power(q3, 2) 
    m01: float = f12 - f03 
    m02: float = f13 + f02
    m10: float = f12 + f03
    # m11: float = q0 ** 2 - q1 ** 2 + q2 ** 2 - q3 ** 2
    m11: float = 1.0 - 2.0 * np.power(q1, 2) - 2.0 * np.power(q3, 2) 
    m12: float = f23 - f01
    m20: float = f13 - f02
    m21: float = f23 + f01
    # m22: float = q0 ** 2 - q1 ** 2 - q2 ** 2 + q3 ** 2
    m22: float = 1.0 - 2.0 * np.power(q2, 2) - 2.0 * np.power(q2, 2) 
    return np.array([
        [m00, m01, m02, 0.0],
        [m10, m11, m12, 0.0],
        [m20, m21, m22, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

def rotation_matrix_to_quaternion(r: np.array):
    """
    Docstring for rotation_matrix_to_quaternion
    
    :param r: the 4x4 matrix
    :type r: np.array

    :return: the resulting quaternon from the rotation matrix
    """

    """
        step 1: find the magnitude of each quaternion component.
        this leaves the sign of each cmponent undefined:
    """
    q0 = np.sqrt((1 + r[1, 1] + r[2, 2] + r[3, 3])/4.0)
    q1 = np.sqrt((1 + r[1, 1] - r[2, 2] - r[3, 3])/4.0)
    q2 = np.sqrt((1 - r[1, 1] + r[2, 2] - r[3, 3])/4.0)
    q3 = np.sqrt((1 - r[1, 1] - r[2, 2] + r[3, 3])/4.0)

    """
        step 2: resolve the signs, find the largest of q0, q1, q2, q3...
        and assume its sign is positive. Then compute the remaining components
        By taking the largest magnitude, one avoids division by small numbers
        which, if done otherwide, would reduce numerical accuracy

        The reason the sign is ambiguous is that any given rotation has two possible quaternion
        representations. If one is known, the other can be found by taking the negative
        of all four terms.

        Doing that has the effect of reversing both the rotation angle and the axis of rotation.
        So, for all rotation quaternions, (q0, q1, q2, q3) and (-q0, -q1, -q2, -q3) produce identical 
        rotations.

        To convert from a rotation matrix to a quaternion, these steps are needed
    """
    largest = max([q0, q1, q2, q3]) 
    #   match-case doesn't work.
    #   it gives the error:
    #   Irrefutable pattern is allowed only for the last case statement
    if q0 == largest:
        q1 = (r[3, 2] - r[2, 3]) / 4.0 * q0
        q2 = (r[1, 3] - r[3, 1]) / 4.0 * q0
        q3 = (r[2, 1] - r[1, 2]) / 4.0 * q0
    elif q1 == largest:
        q0 = (r[3, 2] - r[2, 3]) / 4.0 * q1
        q2 = (r[1, 2] + r[2, 1]) / 4.0 * q1
        q3 = (r[1, 3] + r[3, 1]) / 4.0 * q1
    elif q2 == largest:
        q0 = (r[1, 3] - r[3, 1]) / 4.0 * q2
        q1 = (r[1, 2] + r[2, 1]) / 4.0 * q2
        q3 = (r[2, 3] + r[3, 2]) / 4.0 * q2
    elif q3 == largest:
        q0 = (r[2, 1] - r[1, 2]) / 4.0 * q3
        q1 = (r[1, 3] + r[3, 1]) / 4.0 * q3
        q2 = (r[2, 3] + r[3, 2]) / 4.0 * q3

    return np.array([q0, q1, q2, q3])

    
def euler_angles_to_quaternion(u: float, v: float, w: float):
    """
        Here, the following definitions of Euler angles are used:
            *   Tait-Bryan variant of Euler Angles
            *   Yaw-pitch-roll rotation order, rotating around the z, y, and x axes respectively
            *   Intrinsic rotation (the axes move with each rotation)
            *   Active (or `alibi`) rotation (the point is rotated, not the coordinate system)
            *   Right-handed coordinate system with right-handed rotations
        These definitions are a common convention, and most people find it easiest to
        visualize using them.
        For a more thorough discussion of Euler angles, visit the link:
            https://danceswithcode.net/engineeringnotes/rotations_in_3d/rotations_in_3d_part1.html

        Given the above definition, one can convert from Euler angles to Quaternions
        as defined below, where:
            u = roll angle
            v = pitch angle
            w = yaw angle
            c() = cosine function
            s() = sine function
        The equations work for all values of Euler angle, including the condition
        of gimbal lock, where the pitch angle equals +90 degrees or -90 degrees
    """
    c = np.cos
    s = np.sin

    fu: float = u / 2.0
    fv: float = v / 2.0
    fw: float = w / 2.0 

    q0 = c(fu) * c(fv) * c(fw) + s(fu) * s(fv) * (fw)
    q1 = s(fu) * c(fv) * s(fw) - c(fu) * s(fv) * s(fw)
    q2 = c(fu) * s(fv) * c(fw) + s(fu) * c(fv) * s(fw)
    q3 = c(fu) * c(fv) * s(fw) - s(fu) * s(fv) * c(fw) 

    return np.array([q0, q1, q2, q3])

def quaternion_to_euler_angles(q: np.array):
    """
        Returns the euler angles:
            roll (u), pitch (v), and yaw (w)
        
        Consider atan(y/x) vs atan2(y, x)
        They do the same thing, but difference is in range of results

        Gimbal Lock's effect.

        The below equations are the general solution for extracting Euler
        angles from a quaternion.

        But in the special case where the pitch angle is +90 degrees or -90 degrees,
        the yaw and roll axes of rotation are aligned with each other in the world coordinate
        system, and therefore produce the same effect.
        This means there is no unique solution: any orientation can be described using an infinite
        number of yaw and roll angle combinations.

        To handle the gimbal lock, one must first use the equation for pitch to determine
        whether the pitch angle is +PI/2 or -PI/2 radians.
        Then one must set either roll or yaw to zero and solve for the others as follows

        Note that although Euler angles are susceptibel to gimbal lock,
        quaternions and rotation matrices are not.
    """
    q0, q1, q2, q3 = q

    pitch = np.asin(2.0 * (q0 * q2 - q1 * q3))

    if pitch == np.PI / 2.0:
        roll = 0
        yaw = -2.0 * np.atan2(q1, q0)
    elif pitch == -np.PI / 2.0:
        roll = 0
        yaw = 2.0 * np.atan2(q1, q0)
    else:
        #   formula 1 == formula 2
        #   atan2 function just separates the y and x arduments in atan(y/x)
        # roll = np.atan((2.0 * (q0 * q1 + q2 * q3)) / (q0 ** 2 - q1 ** 2 - q2 ** 2 + q3 ** 2))
        roll = np.atan2(2.0 * (q0 * q1 + q2 * q3), q0 ** 2 - q1 ** 2 - q2 ** 2 + q3 ** 2)

        # yaw = np.atan((2.0 * (q0 * q3 + q1 * q2)) / (q0**2 + q1 ** 2 - q2 ** 2 + q3 ** 2))
        yaw = np.atan2(2.0 * (q0 * q3 + q1 * q2), q0 ** 2 + q1 ** 2 - q2 ** 2 + q3 ** 2)

    return roll, pitch, yaw



"""
    Quaternion Arithmetic
"""

def quaternion_multiply(r: np.array, s: np.array):
    """
        Quaternion Multiplication
        :r : first quaternion
        :s : second quaternion

        Quaternion multiplication is associateive, but (except for some special cases)
        is not commutative.

        Therefore if a, b, and c are quaternions, then:
         (ab)c = a(bc)      <-- associative

         ab != ba           <--- not commutative except for special cases
    """
    r0, r1, r2, r3 = r
    s0, s1, s2, s3 = s

    t0 = r0 * s0 - r1 * s1 - r2 * s2 - r3 * s3
    t1 = r0 * s1 + r1 * s0 - r2 * s3 + r3 * s2
    t2 = r0 * s2 + r1 * s3 + r2 * s0 - r3 * s1
    t3 = r0 * s3 - r1 * s2 + r2 * s1 + r3 * s0

    return np.array([t0, t1, t2, t3])

def quaternion_invert(q: np.array):
    """
        Inverse of a quaternion; it's obtained
        by negating the imaginary components
    """
    return np.array([q[0], -q[1], -q[2], -q[3]])

def quaternion_single_axis_rotation(axis: np.array, theta: float):
    """
        This uses a Euler Angle Axis to create a quaternion
        which is then converted to a rotation matrix
    """
    quart = quaternion_from_axis_angle(axis, theta)
    return quaternion_to_rotation_matrix(quart)

def quaternion_rotation_pure(p: np.array, q: np.array, isActive: bool):
    """
        :p :    The point (x, y, z) to rotate
        :q :    The Quaternion; an array of length containing
            the coefficients of the quaternion
        
        Returns the rotated point (x', y', z') of dimensions 3
    """

    """
        Step 1: Convert the point to be rotated into a quaternion by
        assigning the point's coordinates as the quaternion's imaginary components, and setting the
        quaternion's real component to zero.

        If (x, y, z) is the point to be rotated, then it is converted to a quaternion
        this way
        p = (p0, p1, p2, p3) = (0, x, y, z)
        where p0...p3 represent the coeffiecients of the quaternion
        created from the point, p 
    """
    pq = np.array([0, p[0], p[1], p[2]])

    """
        Step 2: Perform the rotoation.

            This Quaternion Rotation requires two multiplications:

            For active rotation:
                p' = q_inv * p * q
            For passive rotation:
                p' = q * p * q_inv
            where:
                *   p is the quaternion representation of point p
                *   q is the rotation quaterion to be used to rotate the point, p
                *   q_inv is the inverse of the quaternion, q
                *   p' is the resulting rotated point
            
            Active Rotation:
                When the point is rotated with respect to the coordinate system.
            Passive Rotation:
                When the coordinate system is rotated with respect to the point.

            Both rotations are opposite from each other (in direction of rotation)

            Since quaternion multiplication is associative, the order of the following doesn't matter:
            p' = (q * p) * q_inv
            OR
            p' = q * (p * q_inv)

        Step 3: Extract the rotated coordinates from p'
                p' = (0, x', y', z')
            The rotated quaternion p' will have four elements as does any quaternion.
            However, the real element will always equal zero.
            The 3D coordinates of the rotated point (x', y', z') are therefore just
            the imaginary components of the quaternion p'
    """
    p_res = np.array([])
    if isActive:
        p_res = quaternion_multiply(quaternion_invert(q), quaternion_multiply(pq, q)) 
    else:
        p_res = quaternion_multiply(q, quaternion_multiply(pq, quaternion_invert(q)))
    
    #   return x', y', z' in indexes 1, 2, 3
    return np.array([p_res[1], p_res[2], p_res[3]])

"""
    Note that the matrices below
    have some row-major and some column-major compatible.
    All the matrix formulas have their column-major and row-major 
    forms for column-vector and row-vector compatibility respectively.
"""

def rotate_pitch(a:float) -> np.ndarray:
    """
        was named `rotate_x` since it rotates
        around the pitch-axis, which is most times
        denoted as the x-axis/vector of the 3D object

        It's more accurately called `rotate_pitch`
        since it rotates around the pitch axis to 
        to rotate the x and z components of points
        but the x component remains unchanged ---
        so it does not change the pitch-axis but changes
        the yaw and roll axes 

        Hence, more accurate to name `rotate_pitch`
        as in to rotate around the `pitch` axis.

        Row-Major Matrix (m) and Row-Vector (v)
        where m is a d x d matrix
        and v is a 1 x d vector (1 row, d columns)
        According to matrix rule for multiplication
                v * m
            (1 x d) * (d x d)   <--- dimension representation

        v = (x, y, z)
        matrix[dxd] = 
        [
            [0,0], [0,1], [0,2], [0,3],
            [1,0], [1,1], [1,2], [1,3],
            [2,0], [2,1], [2,2], [2,3],
            [3,0], [3,1], [3,2], [3,3],
        ]
        
        The inner parts of the dimension representation must match
        This is needed for the (across vector) x (down matrix) multiplication rule
        Note how below, we go across the vector v, and add the multiplications
        of its components with the values gotten from going down the matrix
        v' = v * m
        v' = transformed v 
        = [ v.x * m[0,0] + v.y * m[1,0] + v.z * m[2,0] + v.w * m[3,0],   #   note x stays the same
            v.x * m[0,1] + v.y * m[1,1] + v.z * m[2,1] + v.w * m[3,1],  #   y val changes
            v.x * m[0,2] + v.y * m[1,2] + v.z * m[2,2] + v.w * m[3,2],  #   z val changes
            v.x * m[0,3] + v.y * m[1,3] + v.z * m[2,3] + v.w * m[3,3],          #   a filler
            ]
        = [ v.x * 1.0 + v.y * 0.0 + v.z * 0.0 + v.w * 0.0,   #   note x stays the same
            v.x * 0.0 + v.y * cos(a) + v.z * sin(a) + v.w * 0.0,  #   y val changes
            v.x * 1.0 + v.y * -sin(a) + v.z * cos(a) + v.w * 0.0,  #   z val changes
            v.x * 1.0 + v.y * 0.0 + v.z * 0.0 + v.w * 1.0,          #   a filler
            ]
        
        >   Note! m[row, col]
        v', the resulting transformed vector has the resulting dimension, (1 x d)
        which is selected from the outer parts of the two operands' outer dimensions
        >   Operands are the vector, v (1 x d), and matrix m (d x d)
        Note how its dimension is the same as the operand vector, v
    """
    return np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, np.cos(a), np.sin(a), 0.0],
        [0.0, -np.sin(a), np.cos(a), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])


def rotate_pitch_column_major(a:float):
    """
        Then for the column-major version

        Column-Major matrix (m) and Column-Vector (v)
        where m is a d x d matrix
        and v is a d x 1 vector (d rows, 1 column)
        According to the matrix rule for multiplication,
        the inner parts must match. So the order of multiplication
        must change:
                m * v
            (d x d) * (d x 1)
        v= [
            [x],
            [y],
            [z]
            ]

        matrix[dxd] = 
        [
            [0,0], [0,1], [0,2], [0,3],
            [1,0], [1,1], [1,2], [1,3],
            [2,0], [2,1], [2,2], [2,3],
            [3,0], [3,1], [3,2], [3,3],
        ]
        The effect of this order of multiplication
        and the fact that the column-major matrix is the transposed
        form of the row-major matrix, gives the same transformation:

        v', the resulting transformed vector will have the dimension, (d x 1),
        from the outer parts of the two operands' outer dimensions
        and the same dimension as the operand vector, v (d x 1).

        Consider that now, the multiplication procedure involves
        going across each row of the matrix and multiplying it with each value
        gotten from going down the vector, v, and summing the values, for
        each component of the resulting vector, v'

        v' = m * v
        = [ m[0,0] * v.x + m[0,1] * v.y + m[0,2] * v.z + m[0,3] * v.w,   #   note x stays the same
            m[1,0] * v.x + m[1,1] * v.y + m[1,2] * v.z + m[1,3] * v.w,  #   y val changes
            m[2,0] * v.x + m[2,1] * v.y + m[2,2] * v.z + m[2,3] * v.w,  #   z val changes
            m[3,0] * v.x + m[3,1] * v.y + m[3,2] * v.z + m[3,3] * v.w,          #   a filler
            ]
        = [ 1.0 * v.x + 0.0     * v.y  +  0.0 +  * v.z  +  0.0 * v.w,   #   note x stays the same
            0.0 * v.x + cos(a)  * v.y  +  -sin(a) * v.z  +  0.0 * v.w,  #   y val changes
            1.0 * v.x + sin(a) * v.y  +  cos(a) * v.z  +  0.0 * v.w,  #   z val changes
            1.0 * v.x + 0.0     * v.y  +  0.0 +  * v.z  +  1.0 * v.w,          #   a filler
            ]
        >   NOte how, because of the transpose, the resulting vector of the column-major
        multiplication is the same as with that of the row-major.

        Without the transpose, for example,  
    """
    """
        return  np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, np.cos(a), -np.sin(a), 0.0],
        [0.0, np.sin(a), np.cos(a), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    """
    return rotate_roll(a).transpose()

def rotate_yaw(a:float) -> np.ndarray:
    """
        was previously called `rotate_y`,
        but whether to use x, y, or z is subjective.

        Hence, more accurate to name `rotate_yaw`
        as in to rotate around the `yaw` axis.

        This means the yaw-axis itself remains unchanged
        but rotates the roll and pitch axes, causing
        only the x and z components of the points to change
    """
    return np.array([
        [np.cos(a), 0.0, -np.sin(a), 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [np.sin(a), 0.0, np.cos(a), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

def rotate_yaw_column_major(a:float):
    return rotate_yaw(a).transpose()

def rotate_roll(a:float):
    """
        was called `rotate_z` but more
        accurately called `rotate_roll`
        since it rotates the points of
        the 3D object around the roll axis,
        making the roll axis unchanged
        but changing the pitch and yaw axis
        of the 3D object, hence only modifying the
        y and z components of the 3D object's
        points.


        Hence, more accurate to name `rotate_roll`
        as in to rotate around the `roll` axis.
    """
    return np.array([
        [np.cos(a), np.sin(a), 0.0, 0.0],
        [-np.sin(a), np.cos(a), 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

def rotate_roll_column_major(a:float):
    return rotate_pitch(a).transpose()

def translate(pos:list[float,float,float]):
    tx, ty, tz = pos
    return np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [tx, ty, tz, 1.0]
    ])

def translate_column_major(pos:list[float, float, float]):
    """
        Transpose of `translate`
        The commented-out section shows the transposed matrix
        But it's self-explanatory to use the `.transpose` method
    """
    # tx, ty, tz = pos
    # return np.array([
    #     [1.0, 0.0, 0.0, tx],
    #     [0.0, 1.0, 0.0, ty],
    #     [0.0, 0.0, 1.0, tz],
    #     [0.0, 0.0, 0.0, 1.0]
    # ])
    return translate(pos).transpose()


def scale(n:float):
    return np.array([
        [n , 0.0, 0.0, 0.0],
        [0.0, n , 0.0, 0.0],
        [0.0, 0.0, n , 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ])