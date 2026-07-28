import tempfile
import unittest
from pathlib import Path

from PIL import Image

from collage import build_collage, choose_grid, find_pngs


class CollageTests(unittest.TestCase):
    def test_grid_contains_every_image(self):
        columns, rows = choose_grid(1001, 3840, 2160)
        self.assertGreaterEqual(columns * rows, 1001)
        self.assertLess(columns * (rows - 1), 1001)

    def test_build_has_exact_dimensions(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            paths = []
            for index, color in enumerate(("red", "green", "blue")):
                path = folder / f"{index}.png"
                Image.new("RGBA", (40 + index, 30), color).save(path)
                paths.append(path)
            output = folder / "out.png"
            build_collage(paths, output, width=320, height=180, gap=2)
            with Image.open(output) as result:
                self.assertEqual(result.size, (320, 180))
                self.assertEqual(result.mode, "RGB")

    def test_find_pngs_is_case_insensitive_and_sorted(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            (folder / "B.PNG").touch()
            (folder / "a.png").touch()
            (folder / "ignore.jpg").touch()
            self.assertEqual([path.name for path in find_pngs(folder)], ["a.png", "B.PNG"])


if __name__ == "__main__":
    unittest.main()
