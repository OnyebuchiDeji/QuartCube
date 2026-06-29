#####   18-03-2026

#	QuartCube

Exploring Controlling a 3D Cube with Quaternions

### Key Features

#### Key Features: Implementations
+	Initially planned to consist of two main methods for rendering the Cube.
+	Each method demonstrates a unique way of drawing the 3D Cube:
	1.	CPU-only
	2.	with GPU
+	Managed to render Cube with CPU only
+	Managed to setup framework for manipulating view of cube using keys and mouse.
+	The afore-mentioned framework involves the use of a Camera, and hence a View Matrxi, and a Projection Matrix.
+	Cameras:
	*	Two Types were created:
		1.	First Person Shooter-like camera
		2.	Key-Controlled Look At Direction Camera.
+	Explored affine transformation matrices, both row-vector-compatible types and their major-vector-compatible counterparts. 
+	Implemented rotating cube around its axis (with functionality of rotating about custom axes), using Eulclidean methods. Implemented conditions against Gimbal lock.
+	Implemented rotating cube around its axis (and custom axes) using quaternions. This method is immune to Gimbal lock. 
+	To demonstrate rotating Cube using quaternions, the Key-Controlled Look At Direction Camera was used. The quaternions were used to modify the cube's orientation in real-time.
+	The methods utilizing just Euclidean formulas where used to predefine the cube's orientaion before rendering.

###   Key Features; Updates
+   Made updates to the rotation functions, ensuring to name them properly according to the axes they rotate.
+   Made updates to other Programs ensuring their angles were in radians before passing to a quaternion or euclidean rotational function.
+   Explained Column-Vector x Column-Major vs Row-Vector x Row-Major matrices.
+   Added functionality to draw spheres procedurally CPU-only
+   Added a Radial Camera that can rotate the scene around the origin and can zoom-in and zoom-out.
+   Created two sphere generation programs:
    -   `FirstSphere`: Attempts to generate 3D perspective-accurate sphere. Managed to generate orthographic and perspective versions.
        *   Sphere was drawn with points
        *   Resolution parameters were provided
        *   There were some errors, though, in the longitudinal and latitudinal angles for the sphere/
    -   `Mesh Sphere`: 
        *   Drew sphere with triangle meshes.
        *   Fixed the longitudinal and latitudinal ranges and angles for solving points on the sphere.
    -   References:
        The Coding Train (2016), "Coding Challenge 25: Spherical Gemoetry". 29 June [Youtube]. Available at: 'https://www.youtube.com/watch?v=RkuBWEkBrZA&t=121s' 

---

###	Setup Instructions

1.	Create and activate virtual environment (Windows):
	*	Create:	`python -m venv <your_virtual_environment>`
		-	replace '<your_virtual_environment>' with the name of your environment
	*	Activate: `<your_virtual_environment>/Scripts/activate.bat`.

2. Install requirements: `pip install -r requirements.txt`

3.	In directory with file `main.py`. Run, `python main.py`


4.  Run Different Cases:
    -   In the file './CpuCore/cpu_core.py', you'll see these lines of code:
    ```python
        # self.fc = FirstCube(self.eng)
        # self.qc = QuartCube(self.eng)
        self.qc2 = QuartCube2(self.eng)
        # self.lc = LastCube(self.eng)
        self.eng.program = self.qc2
    ```
    -   To test the different Test Cases, uncomment a single of the cases between these:
        +   `self.fc`, `self.qc`, `self.qc2`, `self.l`
        	*	`self.lc` is a correction of `self.fc` that demonstrates the FPS Camera and initial rotation and translation of cube.
        	*	`self.qc2` is like that of `self.qc`, but uses an improved/more efficient method for quaternion rotation.
        		*	The former uses a better method that directly calculates the new quaternions from product of rotation quaternions about different axes, and then directly multiplying the resulting quaternion with the 3D point to transform it.
        		*	In contrast, the latter uses a previous method that first converts each quaternion into its corresponding rotation matrix, then multiplying the matrices into the final matrix, and using that matrix to convert the Cube's Model Matrix which is then used in the rendering call (the `draw` method) to modify the Cube's points in real-time. 
        +   Then change which of those chosen above (by uncommenting) to be assigned to `self.eng.program`.
            *   Currently, `self.qc2` is assigned to it.
            *   Change that to be the name of whichever you want to test.
>	Notice that the mouse is hidden. And from tinkering, you'll see that its
	regularly repositioned to be in the centre. 

>    (To Me) Used the chance to practice Git Hooks.

---

### Architecture Diagram

```
QuartCube/
 ├── _project_diagram.txt
 ├── requirements.txt
 ├── README.md
 ├── main.py
 ├── LICENSE
 ├── GpuCore/
 ├── CpuCore/
 │  ├── __init__.py
 │  ├── programs/
 │  ├── _program.py
 │  ├── QuartCube2.py
 │  ├── QuartCube.py
 │  ├── MeshSphere.py
 │  ├── LastCube.py
 │  ├── FirstSphere.py
 │  └── FirstCube.py
 │  ├── cpu_math.py
 │  ├── cpu_graphics.py
 │  ├── cpu_engine.py
 │  └── cpu_core.py
 ├── .pddignore
 └── .gitignore 
```

###	Screenshots

![Image 1](./_scrnshots/ss_0.png)
![Image 2](./_scrnshots/ss_1.png)
![Image 3](./_scrnshots/ss_2.png)
![Image 4](./_scrnshots/ss_3.png)
![Image 5](./_scrnshots/ss_4.png)
![Image 6](./_scrnshots/ss_5.png)
![Image 7](./_scrnshots/ss_6.png)
![Image 8](./_scrnshots/ss_7.png)
![Image 9](./_scrnshots/ss_8.png)
![Image 10](./_scrnshots/ss_9.png)
![Image 11](./_scrnshots/ss_10.png)
![Image 12](./_scrnshots/ss_11.png)
![Image 13](./_scrnshots/ss_12.png)
![Image 14](./_scrnshots/ss_13.png)
![Image 15](./_scrnshots/ss_14.png)
![Image 16](./_scrnshots/ss_15.png)
![Image 17](./_scrnshots/ss_16.png)
![Image 18](./_scrnshots/ss_17.png)
![Image 19](./_scrnshots/ss_18.png)
![Image 20](./_scrnshots/ss_19.png)