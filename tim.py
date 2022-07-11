from PIL import Image, ImageSequence
import urllib.request
from sty import fg
import shutil
import time
import sys
import os


def error(prompt):
    print(fg(255, 50, 50) + 'ERROR:' + fg.rs, prompt)
    #clean_up_files()
    sys.exit(1)


def get_url_image(image_url):
    urllib.request.urlretrieve(image_url, f'internet_image.{image_url[-3:]}')
    
    return f'internet_image.{image_url[-3:]}'


def clean_up_files():
    if os.path.exists("internet_image.png"):
        os.remove("internet_image.png")

    if os.path.exists("SPLIT_GIF"):
        shutil.rmtree("SPLIT_GIF")

    if is_gif:
        os.remove(initial_filename) ## clean up the new, resized image
    else:
        os.remove(filename)

def save_gif_frames(gif):
    if not os.path.exists("SPLIT_GIF"):
        os.mkdir("SPLIT_GIF")
    gif = Image.open(gif)
    for frame_count, frame in enumerate(ImageSequence.Iterator(gif)):
        frame.save(f"SPLIT_GIF/{frame_count}_TIM_SPLIT_GIF.png",format = "png", lossless = True)


def scale_image(filename):
    try:
        img = Image.open(filename)
    except FileNotFoundError:
        error("Image path was not found")

    ## calculations for displaying images relative to terminal size
    hpercent = (baseheight/float(img.size[1]))
    wsize = int((float(img.size[0])*float(hpercent)) * 2)

    ## DEFAULT: Scales to height. IF WIDTH TOO LARGE, scale to width instead
    if wsize > basewidth:
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth, hsize))
    else:
        ## applying new size to image
        img = img.resize((wsize,baseheight))

    ## creating a new file name: img/test.png => img/test_new.png
    filename = "_new.".join(filename.split("."))
    img.save(filename)

    return filename


def create_pixel_dict(img, pixels):
    image = {}
    xdim, ydim = img.size
    for y in range(xdim):
        for x in range(ydim):
            if str(x) not in image:
                image[str(x)] = []
            pixel_values = pixels[y, x]
            try: ##gets values for the current iterated pixel of the image
                if len(pixel_values) == 3:
                    r, g, b = pixel_values ## jpg (usually)
                else:
                    r, g, b, a = pixel_values ## png
            except TypeError:
                return False

            qui = fg(r, g, b) + '█' + fg.rs
            image[str(x)].append(qui)
            
    return image, xdim, ydim


def display_pixel_dict(image, xdim):
    os.system("cls")
    for x, row in image.items():
        spacing_to_center = ((term_columns // 2) - (xdim // 2))
        print(" "*spacing_to_center, end="")
        for char in row:
            print(char, end="")
        print()


## ...globals
filename = None
is_gif = False

## all used for displaying images relative to terminal size
term_columns = os.get_terminal_size().columns
term_lines = os.get_terminal_size().lines
baseheight = term_lines - 1
basewidth = term_columns - 1


## argument parsing
filename = sys.argv[-1]

if "--url" in sys.argv:
    url = sys.argv[-1]
    filename = get_url_image(url)
else:
    filename = sys.argv[-1]

## initial file is stored as 'filename' changes when gifs are used
initial_filename = filename

if filename[-3:] == "gif":
    is_gif = True

## make sure not to scale the gif file, will break otherwise
if not is_gif:
    filename = scale_image(filename)


##IMAGE STORES A DICT OF ARRAYS WITH COLOURED CHARACTERS TO REPRESENT PIXELS
if not is_gif:
    img = Image.open(filename)
    pixels = img.load()

    pixel_dict, xdim, ydim = create_pixel_dict(img, pixels)
    display_pixel_dict(pixel_dict, xdim)

elif is_gif:
    ## creates a directory with each frame of the gif
    save_gif_frames(filename)

    ## sort all the files in frame order:
    filenames = [name.split("_", 1) for name in os.listdir("SPLIT_GIF")] ## splits frame number
    filenames.sort(key=lambda x : int(x[0])) ## sorts by frame number
    filenames = ["_".join(name) for name in filenames] ## joins frame number back 

    ## go through all the frames in the GIF directory
    for filename in filenames:
        ## scales it properly to the terminal and loads the file
        filename = scale_image(f"SPLIT_GIF/{filename}")
        img = Image.open(filename)
        pixels = img.load()
        
        try:
            pixel_dict, xdim, ydim = create_pixel_dict(img, pixels)
        except TypeError:
            continue
        
        display_pixel_dict(pixel_dict, xdim)
        time.sleep(0.1)

clean_up_files()
