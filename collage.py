"""Build a high-resolution, PowerPoint-sized collage from PNG images."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageColor, ImageOps, UnidentifiedImageError


DEFAULT_WIDTH = 3840
DEFAULT_HEIGHT = 2160
DEFAULT_INPUT = Path("input_images")
DEFAULT_OUTPUT = Path("collage.png")


def parse_color(value: str) -> tuple[int, int, int]:
    """Parse a Pillow color string and return an RGB tuple."""
    try:
        return ImageColor.getcolor(value, "RGB")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid color {value!r}") from exc


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def nonnegative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def find_pngs(folder: Path, recursive: bool = False) -> list[Path]:
    """Return PNG files in stable, case-insensitive filename order."""
    iterator = folder.rglob("*") if recursive else folder.iterdir()
    return sorted(
        (path for path in iterator if path.is_file() and path.suffix.lower() == ".png"),
        key=lambda path: str(path.relative_to(folder)).casefold(),
    )


def choose_grid(count: int, width: int, height: int) -> tuple[int, int]:
    """Choose a compact grid whose shape closely matches the canvas."""
    if count < 1:
        raise ValueError("count must be at least one")

    ideal_columns = math.sqrt(count * width / height)
    candidates = range(max(1, math.floor(ideal_columns) - 2), math.ceil(ideal_columns) + 3)

    def score(columns: int) -> tuple[float, int]:
        rows = math.ceil(count / columns)
        cell_ratio = (width / columns) / (height / rows)
        # Prefer nearly square tiles, then fewer unused grid positions.
        return abs(math.log(cell_ratio)), columns * rows - count

    columns = min(candidates, key=score)
    return columns, math.ceil(count / columns)


def _edges(total: int, cells: int, gap: int) -> list[int]:
    usable = total - gap * (cells - 1)
    if usable < cells:
        raise ValueError("gap is too large for the selected output size")
    return [round(index * usable / cells) + index * gap for index in range(cells + 1)]


def build_collage(
    paths: Sequence[Path],
    output: Path,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    gap: int = 0,
    background: tuple[int, int, int] = (255, 255, 255),
    fit: str = "cover",
) -> tuple[int, int]:
    """Compose paths into one RGB PNG and return (columns, rows)."""
    if not paths:
        raise ValueError("No PNG images were provided")

    columns, rows = choose_grid(len(paths), width, height)
    x_edges = _edges(width, columns, gap)
    y_edges = _edges(height, rows, gap)
    canvas = Image.new("RGB", (width, height), background)

    for index, path in enumerate(paths):
        row, column_in_row = divmod(index, columns)
        items_in_row = min(columns, len(paths) - row * columns)
        # Center a partial final row using half-cell offsets.
        offset = (columns - items_in_row) * (width - gap * (columns - 1)) / columns / 2
        left = round(x_edges[column_in_row] + offset)
        right = round(x_edges[column_in_row + 1] + offset)
        top, bottom = y_edges[row], y_edges[row + 1]
        tile_size = (right - left, bottom - top)

        try:
            with Image.open(path) as source:
                source.load()
                rgba = source.convert("RGBA")
        except (OSError, UnidentifiedImageError) as exc:
            raise ValueError(f"Could not read {path}: {exc}") from exc

        if fit == "cover":
            tile = ImageOps.fit(rgba, tile_size, method=Image.Resampling.LANCZOS)
        elif fit == "contain":
            tile = ImageOps.contain(rgba, tile_size, method=Image.Resampling.LANCZOS)
        else:
            raise ValueError("fit must be 'cover' or 'contain'")

        tile_background = Image.new("RGB", tile_size, background)
        paste_at = ((tile_size[0] - tile.width) // 2, (tile_size[1] - tile.height) // 2)
        tile_background.paste(tile, paste_at, tile)
        canvas.paste(tile_background, (left, top))

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="PNG", optimize=True, compress_level=6)
    return columns, rows


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Combine PNG files into a high-resolution 16:9 slide collage."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="input folder")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="output PNG")
    parser.add_argument("--width", type=positive_int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=positive_int, default=DEFAULT_HEIGHT)
    parser.add_argument("--gap", type=nonnegative_int, default=0, help="pixels between tiles")
    parser.add_argument("--background", type=parse_color, default=(255, 255, 255))
    parser.add_argument("--fit", choices=("cover", "contain"), default="cover")
    parser.add_argument("--recursive", action="store_true", help="include nested folders")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    if not args.input.is_dir():
        print(f"Error: input folder does not exist: {args.input}", file=sys.stderr)
        return 2

    paths = find_pngs(args.input, args.recursive)
    if not paths:
        print(f"Error: no PNG files found in {args.input}", file=sys.stderr)
        return 2

    print(f"Found {len(paths):,} PNG files. Building {args.width}x{args.height} collage...")
    try:
        columns, rows = build_collage(
            paths, args.output, args.width, args.height, args.gap, args.background, args.fit
        )
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Done: {args.output.resolve()} ({columns} columns x {rows} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
