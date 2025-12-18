import math
import numpy as np

class Transform2D:
    def __init__(
            self,
            matrix: np.ndarray | list = np.eye(3, dtype=np.float64)
    ):
        if isinstance(matrix, list):
            self.matrix = np.array(matrix, dtype=np.float64)
        elif isinstance(matrix, np.ndarray):
            self.matrix = matrix.astype(dtype=np.float64)
        else:
            self.matrix = matrix
        if self.matrix.shape != (3, 3):
                raise Exception(f'Invalid matrix dimensions. Expected (3, 3), got {self.matrix.shape}')

    @property
    def a(self): return self.matrix[0, 0]
    @property
    def b(self): return self.matrix[1, 0]
    @property
    def c(self): return self.matrix[0, 1]
    @property
    def d(self): return self.matrix[1, 1]
    @property
    def e(self): return self.matrix[0, 2]
    @property
    def f(self): return self.matrix[1, 2]

    @property
    def scale_x(self): return self.a
    @property
    def scale_y(self): return self.d
    @property
    def shear_x(self): return self.b
    @property
    def shear_y(self): return self.c
    @property
    def translate_x(self): return self.e
    @property
    def translate_y(self): return self.f

    # Конструктор по стандарту svg
    # [[a  c  e
    #   b  d  f
    #   0  0  1]]
    @classmethod
    def svg(
            cls,
            a: float = 1.0,
            b: float = 0.0,
            c: float = 0.0,
            d: float = 1.0,
            e: float = 0.0,
            f: float = 0.0
    ):
        return cls(np.array([
            [a, c, e],
            [b, d, f],
            [0, 0, 1]
        ], dtype=np.float64))

    # Конструктор по трансформации
    @classmethod
    def compose(
            cls,
            translate_x: float  = 0.0,
            translate_y: float  = 0.0,
            scale_x: float      = 1.0,
            scale_y: float      = 1.0,
            angle: float        = 0.0
    ):
        return (
            cls()
            .translate(
                translate_x,
                translate_y,
            )
            .scale(
                scale_x,
                scale_y
            )
            .rotate(angle)
        )

    # Перемещение начала координат на dx и dy
    def translate(self, dx: float, dy: float):
        self.matrix[:2, 2] += [dx, dy]
        return self

    # Отражение
    def reflect(self, rtype: str = 'origin'):
        if rtype == 'origin':
            self.matrix[:2:1, :2:1] *= -1
        elif rtype == 'x':
            self.matrix[1, 1] *= -1
        elif rtype == 'y':
            self.matrix[0, 0] *= -1
        return self

    # Установка начала координат в точку
    def set_origin(self, x: float, y: float):
        self.matrix[:2, 2] = [x, y]
        return self

    # Трансформация по размеру
    def scale(self, scale_x: float, scale_y: float):
        self.matrix[:2:1, :2:1] *= [scale_x, scale_y]
        return self

    # Обратная матрица преобразования
    def inverse(self):
        self.matrix = np.linalg.inv(self.matrix)
        return self

    # Поворот координат
    def rotate(self, angle: float = 0, atype: str = None):
        # Radians default
        theta = 0
        if any(atype == t for t in [None, 'rad']):
            theta = angle
        elif atype == 'deg':
            theta = math.radians(angle)

        self.matrix = np.matmul(
            self.matrix,
            np.array([
                [math.cos(theta), -math.sin(theta), 0],
                [math.sin(theta),  math.cos(theta), 0],
                [              0,                0, 1]
            ], dtype=np.float64)
        )
        return self

    # Установка трансформации
    def set_transform(
            self,
            translate_x,
            translate_y,
            scale_x,
            scale_y,
            angle
    ):
        self.translate(translate_x, translate_y)
        self.scale(scale_x, scale_y)
        self.rotate(angle)
        return self

    # Умножение на правый операнд
    def __mul__(self, other: np.ndarray | list | tuple):
        _dots = np.array(other, dtype=np.float64)
        if len(_dots.shape) > 1:
            dots_len, vec_len = _dots.shape
        else:
            dots_len = 1
            vec_len = _dots.shape

        if vec_len != 2 and _dots.shape != (2,):
            raise Exception(f'Invalid dot({type(_dots)}) dimension. Expected (2,), got {_dots.shape}')
        if dots_len > 1:
            for i in range(dots_len):
                _dots[i] = np.matmul(self.matrix, np.append(_dots[i], 1.0))[:2]
            return _dots
        else:
            return np.matmul(self.matrix, np.append(_dots, 1.0))[:2]

    # Преобразование в строку
    def __str__(self):
        return f'Transform2D({self.a}, {self.b}, {self.c}, {self.d}, {self.e}, {self.f})'
