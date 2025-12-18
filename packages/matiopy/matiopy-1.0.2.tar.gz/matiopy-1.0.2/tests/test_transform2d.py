import unittest
import numpy as np
import math
from src.matiopy.transform2d.transform2d import Transform2D


class TestTransform2D(unittest.TestCase):

    def setUp(self):
        self.transform = Transform2D()

    def test_creation(self):
        """Тест создания трансформации"""
        t = Transform2D()
        expected_matrix = np.eye(3, dtype=np.float64)
        self.assertTrue(np.array_equal(t.matrix, expected_matrix))

    def test_creation_with_list(self):
        """Тест создания с использованием списка"""
        t = Transform2D([[1, 2, 3], [4, 5, 6], [0, 0, 1]])
        self.assertEqual(t.a, 1)
        self.assertEqual(t.c, 2)
        self.assertEqual(t.e, 3)
        self.assertEqual(t.b, 4)
        self.assertEqual(t.d, 5)
        self.assertEqual(t.f, 6)

    def test_creation_with_numpy_array(self):
        """Тест создания с numpy массивом"""
        t = Transform2D(np.array([[2, 0, 0], [0, 2, 0], [0, 0, 1]]))
        self.assertEqual(t.a, 2)
        self.assertEqual(t.d, 2)

    def test_invalid_matrix_dimensions(self):
        """Тест на неверные размеры матрицы"""
        with self.assertRaises(Exception):
            Transform2D([[1, 2], [3, 4]])

    def test_svg_constructor(self):
        """Тест SVG конструктора"""
        t = Transform2D.svg(a=2, b=1, c=3, d=4, e=5, f=6)
        self.assertEqual(t.a, 2)
        self.assertEqual(t.b, 1)
        self.assertEqual(t.c, 3)
        self.assertEqual(t.d, 4)
        self.assertEqual(t.e, 5)
        self.assertEqual(t.f, 6)

    def test_translate(self):
        """Тест перемещения"""
        t = Transform2D()
        t.translate(10, 20)
        self.assertEqual(t.e, 10)
        self.assertEqual(t.f, 20)

    def test_scale(self):
        """Тест масштабирования"""
        t = Transform2D()
        t.scale(2, 3)
        self.assertEqual(t.a, 2)
        self.assertEqual(t.d, 3)

    def test_rotate_radians(self):
        """Тест поворота в радианах"""
        t = Transform2D()
        t.rotate(math.pi / 2)  # 90 градусов
        expected_cos = math.cos(math.pi / 2)
        expected_sin = math.sin(math.pi / 2)
        self.assertAlmostEqual(t.a, expected_cos, places=10)
        self.assertAlmostEqual(t.b, expected_sin, places=10)
        self.assertAlmostEqual(t.c, -expected_sin, places=10)
        self.assertAlmostEqual(t.d, expected_cos, places=10)

    def test_rotate_degrees(self):
        """Тест поворота в градусах"""
        t = Transform2D()
        t.rotate(90, 'deg')  # 90 градусов
        expected_cos = math.cos(math.radians(90))
        expected_sin = math.sin(math.radians(90))
        self.assertAlmostEqual(t.a, expected_cos, places=10)
        self.assertAlmostEqual(t.b, expected_sin, places=10)

    def test_reflect_origin(self):
        """Тест отражения относительно начала координат"""
        t = Transform2D()
        t.reflect('origin')
        self.assertEqual(t.a, -1)
        self.assertEqual(t.d, -1)

    def test_reflect_x(self):
        """Тест отражения относительно оси X"""
        t = Transform2D()
        t.reflect('x')
        self.assertEqual(t.d, -1)
        self.assertEqual(t.a, 1)

    def test_reflect_y(self):
        """Тест отражения относительно оси Y"""
        t = Transform2D()
        t.reflect('y')
        self.assertEqual(t.a, -1)
        self.assertEqual(t.d, 1)

    def test_inverse(self):
        """Тест обратной матрицы"""
        t = Transform2D.svg(a=2, d=3, e=5)
        original_matrix = t.matrix.copy()
        t.inverse()

        # Произведение матрицы на обратную должно дать единичную матрицу
        result = np.matmul(original_matrix, t.matrix)
        expected = np.eye(3, dtype=np.float64)
        self.assertTrue(np.allclose(result, expected, atol=1e-10))

    def test_transform_single_point(self):
        """Тест преобразования одной точки"""
        t = Transform2D()
        t.translate(10, 20)
        point = [5, 5]
        result = t * point
        expected = [15, 25]
        self.assertTrue(np.allclose(result, expected))

    def test_transform_multiple_points(self):
        """Тест преобразования нескольких точек"""
        t = Transform2D()
        t.scale(2, 2)
        points = [[1, 2], [3, 4], [5, 6]]
        result = t * points
        expected = [[2, 4], [6, 8], [10, 12]]
        self.assertTrue(np.allclose(result, expected))

    def test_compose_method(self):
        """Тест метода compose"""
        t = Transform2D.compose(
            translate_x=10,
            translate_y=20,
            scale_x=2,
            scale_y=3,
            angle=math.pi / 4
        )
        point = [1, 1]
        result = t * point

        # Проверим что преобразование работает
        self.assertEqual(len(result), 2)

    def test_set_transform(self):
        """Тест метода set_transform"""
        t = Transform2D()
        t.set_transform(
            translate_x=10,
            translate_y=20,
            scale_x=2,
            scale_y=3,
            angle=math.pi / 4
        )
        self.assertEqual(t.e, 10)
        self.assertEqual(t.f, 20)

    def test_str_representation(self):
        """Тест строкового представления"""
        t = Transform2D.svg(a=1, b=2, c=3, d=4, e=5, f=6)
        expected_str = "Transform2D(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)"
        self.assertEqual(str(t), expected_str)

    def test_properties(self):
        """Тест свойств трансформации"""
        t = Transform2D.svg(a=2, b=1, c=3, d=4, e=5, f=6)
        self.assertEqual(t.scale_x, 2)
        self.assertEqual(t.scale_y, 4)
        self.assertEqual(t.shear_x, 1)
        self.assertEqual(t.shear_y, 3)
        self.assertEqual(t.translate_x, 5)
        self.assertEqual(t.translate_y, 6)

    def test_transform_chain(self):
        """Тест цепочки преобразований"""
        t = Transform2D()
        t.translate(10, 20).scale(2, 3).rotate(math.pi / 4)
        point = [1, 1]
        result = t * point

        # Проверим что цепочка работает
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result, np.ndarray)

    def test_set_origin(self):
        """Тест установки начала координат"""
        t = Transform2D()
        t.set_origin(100, 200)
        self.assertEqual(t.e, 100)
        self.assertEqual(t.f, 200)


if __name__ == '__main__':
    unittest.main()