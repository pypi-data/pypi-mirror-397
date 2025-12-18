from src.matiopy.transform2d.transform2d import Transform2D

# Matiopy

(Transform Python)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Github: Repo](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/FrigatZero/matiopy)

---

A library for 2D transformations and vector operations

## Dependencies

---

- [Numpy](https://pypi.org/project/numpy/)
- [Python (>=3.8)](https://www.python.org/downloads/)

## Install

---

You can install ```Matiopy``` from ```PyPI```

```bash
pip install matiopy
```

## Examples

---

1. Constructor
```python
import math
import numpy
from matiopy import Transform2D as t2d

# Make new Transform from SVG
"""
    a c e
    b d f
    0 0 1
"""
matrix = t2d.svg(1, 0, 0, 1, 0, 0)
print(matrix) # Result: Transform2D(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

# Make new Transform from components
_matrix = t2d.compose(
    translate_x=0,
    translate_y=0,
    scale_x=3,
    scale_y=4,
    angle=math.pi/3 # radians default
)
print(_matrix) # Result: Transform2D(1.50.., 3.46.., -2.59.., 2.00.., 0.0, 0.0)
```

2. Translation
```python
# Translate by dx=2, dy=2
matrix.translate(2, 2)
print(matrix) # Result: Transform2D(1.0, 0.0, 0.0, 1.0, 2.0, 2.0)
```
3. Scaling
```python
# Scale by x=2, y=3
matrix.scale(2, 3)
print(matrix) # Result: Transform2D(2.0, 0.0, 0.0, 3.0, 2.0, 2.0)
```
4. Rotation
```python
# Rotate by 45 degrees/radians (radians default)
matrix.rotate(45, atype='deg')
print(matrix) # Result: Transform2D(1.41.., 2.12.., -1.41.., 2.12.., 2.0, 2.0)
matrix.rotate(-math.pi/4)
print(matrix) # Result: Transform2D(2.0.., 0.0.., 0.00.., 3.0.., 2.0, 2.0)
```
5. Use
```python
# Apply to a dot list or Numpy array
dots_numpy = numpy.array([[0, 0], [1, 0], [1, 1], [0, 1]])
# You can use tuple as dots
dots_list = [[0, 0], (1, 0), [1, 1], (0, 1)]
print(matrix * dots_numpy)
# Result:
# [[2. 2.]
#  [4. 2.]
#  [4. 5.]
#  [2. 5.]]
print(matrix * dots_list)
# Result:
# [[2. 2.]
#  [4. 2.]
#  [4. 5.]
#  [2. 5.]]
```
6. Inversion
```python
# Invert Transform Matrix
matrix.inverse()
print(matrix)
# Original: Transform2D(2.0.., 0.0.., 0.00.., 3.0.., 2.0, 2.0)
# Result:   Transform2D(0.49.., 0.00.., 0.00.., 0.33.., -0.99.., -0.66..)
```
7. Set Origin
```python
# Set Transform origin
matrix.set_origin(0, 0)
print(matrix)
# Result:   Transform2D(0.49.., 0.00.., 0.00.., 0.33.., 0.0, 0.0)
```
8. Reflect by axis
```python
# Reflect Matrix
matrix.reflect(rtype='origin')
print(matrix) # Result: Transform2D(-0.49.., 0.00.., 0.00.., -0.33.., 0.0, 0.0)
matrix.reflect(rtype='x')
print(matrix) # Result: Transform2D(-0.49.., 0.00.., 0.00.., 0.33.., 0.0, 0.0)
matrix.reflect(rtype='y')
print(matrix) # Result: Transform2D(0.49.., 0.00.., 0.00.., 0.33.., 0.0, 0.0)
```