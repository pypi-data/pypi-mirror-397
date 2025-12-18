import math
import numpy as np


class Vector2D:
    """Класс для работы с 2D векторами"""

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)

    @classmethod
    def from_array(cls, arr):
        """Создание вектора из массива"""
        return cls(arr[0], arr[1])

    @classmethod
    def from_angle(cls, angle: float, magnitude: float = 1.0):
        """Создание вектора из угла и величины"""
        return cls(
            magnitude * math.cos(angle),
            magnitude * math.sin(angle)
        )

    def to_array(self):
        """Преобразование в numpy массив"""
        return np.array([self.x, self.y], dtype=np.float64)

    def magnitude(self):
        """Вычисление длины вектора"""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        """Нормализованный вектор"""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def dot(self, other):
        """Скалярное произведение"""
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        """Векторное произведение (z-компонента)"""
        return self.x * other.y - self.y * other.x

    def angle(self, other=None):
        """Угол между векторами"""
        if other is None:
            return math.atan2(self.y, self.x)
        dot_product = self.normalized().dot(other.normalized())
        dot_product = max(-1.0, min(1.0, dot_product))  # Ограничение для acos
        return math.acos(dot_product)

    def rotate(self, angle: float):
        """Поворот вектора на угол"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def distance_to(self, other):
        """Расстояние до другого вектора"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    # Операторы
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError("Division by zero")
        return Vector2D(self.x / scalar, self.y / scalar)

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def __eq__(self, other):
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __str__(self):
        return f"Vector2D({self.x:.3f}, {self.y:.3f})"