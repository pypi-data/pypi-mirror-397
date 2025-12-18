import unittest
import math
from src.vector2d.vector2d import Vector2D


class TestVector2D(unittest.TestCase):
    def setUp(self):
        self.v1 = Vector2D(3, 4)
        self.v2 = Vector2D(1, 2)

    def test_magnitude(self):
        """Тест вычисления длины вектора"""
        self.assertAlmostEqual(self.v1.magnitude(), 5.0)

    def test_normalized(self):
        """Тест нормализации вектора"""
        v = Vector2D(3, 4)
        norm = v.normalized()
        self.assertAlmostEqual(norm.magnitude(), 1.0)
        self.assertAlmostEqual(norm.x, 0.6)
        self.assertAlmostEqual(norm.y, 0.8)

    def test_dot_product(self):
        """Тест скалярного произведения"""
        result = self.v1.dot(self.v2)
        expected = 3 * 1 + 4 * 2
        self.assertAlmostEqual(result, expected)

    def test_cross_product(self):
        """Тест векторного произведения"""
        result = self.v1.cross(self.v2)
        expected = 3 * 2 - 4 * 1
        self.assertAlmostEqual(result, expected)

    def test_angle(self):
        """Тест вычисления угла"""
        v1 = Vector2D(1, 0)
        v2 = Vector2D(0, 1)
        angle = v1.angle(v2)
        self.assertAlmostEqual(angle, math.pi / 2)

    def test_rotation(self):
        """Тест поворота вектора"""
        v = Vector2D(1, 0)
        rotated = v.rotate(math.pi / 2)
        self.assertAlmostEqual(rotated.x, 0, places=10)
        self.assertAlmostEqual(rotated.y, 1, places=10)

    def test_distance(self):
        """Тест расстояния между векторами"""
        v1 = Vector2D(0, 0)
        v2 = Vector2D(3, 4)
        distance = v1.distance_to(v2)
        self.assertAlmostEqual(distance, 5.0)

    def test_addition(self):
        """Тест сложения векторов"""
        result = self.v1 + self.v2
        self.assertAlmostEqual(result.x, 4)
        self.assertAlmostEqual(result.y, 6)

    def test_scalar_multiplication(self):
        """Тест умножения на скаляр"""
        result = self.v1 * 2
        self.assertAlmostEqual(result.x, 6)
        self.assertAlmostEqual(result.y, 8)

    def test_from_angle(self):
        """Тест создания вектора из угла"""
        v = Vector2D.from_angle(math.pi / 4, math.sqrt(2))
        self.assertAlmostEqual(v.x, 1, places=10)
        self.assertAlmostEqual(v.y, 1, places=10)


if __name__ == '__main__':
    unittest.main()