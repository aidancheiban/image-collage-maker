<<<<<<< HEAD
# PowerPoint Image Collage

This Python tool combines 1,000+ PNG images into one high-resolution collage sized for a modern widescreen PowerPoint slide (16:9). The default output is a 4K PNG: **3840 × 2160 pixels**.

## Setup

Python 3.10 or newer is recommended.

```powershell
python -m pip install -r requirements.txt
```

Put PNG files in `input_images`, then run:

```powershell
python collage.py
```

The finished file is `collage.png`. Images are processed one at a time, so a large input collection does not need to fit in memory all at once. Files are placed in alphabetical filename order.

## Useful options

```powershell
# Add 4-pixel gaps with a black background
python collage.py --gap 4 --background black

# Keep every image fully visible (may leave background bars)
python collage.py --fit contain

# Produce an 8K 16:9 image
python collage.py --width 7680 --height 4320 --output collage_8k.png

# Include PNGs in subfolders
python collage.py --recursive
```

Run `python collage.py --help` for all options. PowerPoint's modern widescreen slide is 13.333 × 7.5 inches; PNG files have no fixed physical size, so the 16:9 pixel dimensions are what preserve the exact slide shape. In PowerPoint, insert the collage and set it to fill the slide.
=======
# image-collage-maker
Creates a collage of inputted images.
>>>>>>> 8cac07bce231e0e28388cc3acd2cc6fcb5b94595
