from PIL import Image, ImageSequence
from time import perf_counter, sleep
import urllib.request
from sty import fg
import requests
import shutil
import sys
import os


class Clock:
    def __init__(self, fps):
        self.start = perf_counter()
        self.frame_length = 1/fps

    @property
    def tick(self):
        return int((perf_counter() - self.start)/self.frame_length)

    def sleep(self):
        r = self.tick + 1
        while self.tick < r:
            sleep(1/1000)


## If gif is ended too early, it will not remove the files properly
if os.path.exists("internet_image.png"):
    os.remove("internet_image.png")

if os.path.exists("SPLIT_GIF"):
    shutil.rmtree("SPLIT_GIF")

def error(prompt):
    print(fg(255, 50, 50) + 'ERROR:' + fg.rs, prompt)
    #clean_up_files()
    sys.exit(1)


def info(prompt):
    print(fg(50, 255, 50) + 'INFO:' + fg.rs, prompt)


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


def search_gif(search_query, api_key):
    r = requests.get(f"https://api.giphy.com/v1/gifs/search?q={search_query}&api_key={api_key}&limit=1")
    j = r.json()
    url = j["data"][0]["images"]["original"]["url"][:-5]

    return url


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


def create_image_array(img, pixels):
    xdim, ydim = img.size
    image = [[] for _ in range(xdim)]
    for y in range(xdim):
        for x in range(ydim):
            pixel_values = pixels[y, x]
            try: ##gets values for the current iterated pixel of the image
                if len(pixel_values) == 3:
                    r, g, b = pixel_values ## jpg (usually)
                else:
                    r, g, b, _ = pixel_values ## png
            except TypeError:
                return False ## if frame is in 8-bit colour, it gets skipped

            qui = fg(r, g, b) + '█' + fg.rs
            image[y].append(qui)
            
    return image, xdim, ydim


def display_image_array(image, xdim):
    os.system(clear_command)
    #print(image)
    spacing_to_center = ((term_columns // 2) - (xdim // 2))
    gap = " "*spacing_to_center
    for index in range(len(image[0])):
        print(gap, end="")
        for pixels in image:
            print(pixels[index], end="")
        print()


## ...globals
clear_command = "cls" if os.name == "nt" else "clear"
GIPHY_API = os.getenv('GIPHY_API')
filename = None
is_gif = False
repeats = 1
fps = 15


## all used for displaying images relative to terminal size
term_columns = os.get_terminal_size().columns
term_lines = os.get_terminal_size().lines
basewidth = term_columns - 1
baseheight = term_lines - 1


## argument parsing
filename = sys.argv[-1] ## this gets overridden if no other flags are used

if "--search" in sys.argv:
    search_arg_index = sys.argv.index("--search")
    search_query = sys.argv[search_arg_index + 1:]
    search_query = "+".join(search_query)
    info("Query is being search for")
    url = search_gif(search_query, GIPHY_API)
    filename = get_url_image(url)

if "--repeats" in sys.argv:
    repeats_arg_index = sys.argv.index("--repeats")
    repeats = int(sys.argv[repeats_arg_index + 1])

if "--url" in sys.argv:
    url = sys.argv[-1]
    if url == "--url": ## if the last argument is the flag, raise error
        error("No url supplied")
    info("File is being downloaded")
    filename = get_url_image(url)

if "--fps" in sys.argv:
    fps_arg_index = sys.argv.index("--fps")
    fps = int(sys.argv[fps_arg_index + 1])

## initial file is stored as 'filename' changes when gifs are used
initial_filename = filename

if filename[-3:] == "gif":
    is_gif = True

## make sure not to scale the gif file, will break otherwise
if not is_gif:
    filename = scale_image(filename)


clock = Clock(fps)


##IMAGE STORES AN ARRAY OF ARRAYS WITH COLOURED CHARACTERS TO REPRESENT PIXELS
if not is_gif:
    img = Image.open(filename)
    pixels = img.load()

    pixel_array, xdim, ydim = create_image_array(img, pixels)
    display_image_array(pixel_array, xdim)

elif is_gif:
    ## creates a directory with each frame of the gif
    save_gif_frames(filename)

    ## sort all the files in frame order:
    filenames = [name.split("_", 1) for name in os.listdir("SPLIT_GIF")] ## splits frame number
    filenames.sort(key=lambda x : int(x[0])) ## sorts by frame number
    filenames = ["_".join(name) for name in filenames] ## joins frame number back 

    ## go through all the frames in the GIF directory
    for _ in range(repeats):
        for filename in filenames:
            ## scales it properly to the terminal and loads the file
            filename = scale_image(f"SPLIT_GIF/{filename}")
            img = Image.open(filename)
            pixels = img.load()
            
            try:
                pixel_dict, xdim, ydim = create_image_array(img, pixels)
            except TypeError:
                continue
            
            display_image_array(pixel_dict, xdim)
            clock.sleep()

clean_up_files()
