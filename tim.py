from PIL import Image
from sty import fg
import sys
import os


def error(prompt):
    print(fg(255, 50, 50) + 'ERROR:' + fg.rs, prompt)
    sys.exit(1)


## last argument should be the filename
filename = sys.argv[-1]

## all used for displaying images relative to terminal size
term_columns = os.get_terminal_size().columns
term_lines = os.get_terminal_size().lines
baseheight = term_lines - 1

try:
    img = Image.open(filename)
except FileNotFoundError:
    error("Image path was not found")

## calculations for displaying images relative to terminal size
hpercent = (baseheight/float(img.size[1]))
wsize = int((float(img.size[0])*float(hpercent)) * 2)

## applying new size to image
img = img.resize((wsize,baseheight))

## creating a new file name
filename = "_new.".join(filename.split("."))
img.save(filename)

## OPEN THE NEW RESIZED IMAGE
img = Image.open(filename)
pixels = img.load()

xdim, ydim = img.size
##IMAGE STORES A DICT OF ARRAYS WITH COLOURED CHARACTERS TO REPRESENT PIXELS
image = {}

for y in range(xdim):
    for x in range(ydim):
        if str(x) not in image:
            image[str(x)] = []
        pixel_values = pixels[y, x]
        try:
            if len(pixel_values) == 3:
                r, g, b = pixel_values
            else:
                r, g, b, a = pixel_values ##gets values for the current iterated pixel of the image
        except TypeError:
            error("Image type is not supported or the image is broken")


        qui = fg(r, g, b) + '█' + fg.rs
        image[str(x)].append(qui)


for x, row in image.items():
    spacing_to_center = ((term_columns // 2) - (xdim // 2))
    print(" "*spacing_to_center, end="")
    for char in row:
        print(char, end="")
    print()

os.remove(filename) ## clean up the new, resized image
