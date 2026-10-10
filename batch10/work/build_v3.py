import sys, os
sys.path.insert(0, "/workspace/santa/batch5/work")
from lib5 import *
import lib3
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
G3 = os.path.join(HERE, "gen3"); SRC = "/workspace/santa/source"
lib3.OUT = os.path.dirname(HERE)

def clean_cutout():
    o = Image.open(f"{SRC}/couple_cutout.png").convert("RGBA")
    a = np.asarray(o).astype(float); r,g,b,al = [a[...,i] for i in range(4)]
    H,W = al.shape
    green = (g > r*1.15) & (g > b*1.1)            # leftover shrub/gravel bits
    al[green] = 0
    al[al < 25] = 0
    a[...,3] = al
    o = Image.fromarray(a.astype(np.uint8)); o = o.crop(o.getbbox())
    o.save(f"{SRC}/couple_cutout.png")
    # Eric alone: vertical cut just right of Mrs. Claus's hair; used flush to the frame's left edge
    e = o.crop((int(o.width*0.485), 0, o.width, o.height)); e = e.crop(e.getbbox())
    e.save(f"{SRC}/eric_cutout.png")
    return o, e

def grade(p, bg_region, amt=0.35, bright=1.0, warm=(1,1,1)):
    pa = np.asarray(p).astype(float); rgb = pa[...,:3]; m = pa[...,3] > 128
    bm = np.asarray(bg_region.convert("RGB")).astype(float).reshape(-1,3).mean(0)
    pm = rgb[m].mean(0)
    rgb = rgb * (1 + amt*(bm/pm - 1)) * bright * np.array(warm)
    pa[...,:3] = rgb.clip(0,255); return Image.fromarray(pa.astype(np.uint8))

def place(bg, person, h, x, align="left", bright=1.0, warm=(1,1,1), amt=0.3):
    k = h / person.height
    p = person.resize((round(person.width*k), h), Image.LANCZOS)
    y = S - h
    if align == "right": x = S - p.width
    p = grade(p, bg, amt, bright, warm)
    # soft shadow / occlusion behind the figure
    al = p.split()[3]
    sh = Image.new("RGBA", p.size, (0,0,0,0)); sh.putalpha(al.point(lambda v: int(v*0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    bg.alpha_composite(sh, (max(0,x-18), y+10))
    # light wrap: slight edge feather so hair/beard blend
    p.putalpha(al.filter(ImageFilter.GaussianBlur(1.2)))
    bg.alpha_composite(p, (x, y))
    return bg

def scene(name, scale=1.0, xoff=0, yoff=0, blur=0):
    im = Image.open(f"{G3}/{name}").convert("RGB")
    s = round(S*scale); im = im.resize((s, s), Image.LANCZOS)
    im = im.crop((xoff, yoff, xoff+S, yoff+S))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    return im.convert("RGBA")

def finish(c, top, bot, name):
    grad_top(c, 290, 200); grad_bottom(c, 300, 225)
    lines(c, top, 16, gap=4); lines_bottom(c, bot, bottom=1030, gap=4)
    handle(c); p = save(c, name); c.convert("RGB").save(p[:-4]+".jpg", quality=92)

couple, eric = clean_cutout()
c = scene("garage.png", 1.0, 0, 0, blur=1.0)
place(c, couple, 620, 0, "right", amt=0.25)
finish(c, [("THE SLEIGH'S IN THE SHOP.", 100, WHT), ("SANTA'S ON ROUTE 66.", 116, YEL)], [("RIDE ALONG.", 92, WHT)], "41_sleigh_in_the_shop_v3.png")

c = scene("po.png", 1.1, 150, 110, blur=1.2)
place(c, couple, 700, 0, "left", amt=0.25)
finish(c, [("CHECK YOUR REGISTRATION.", 104, YEL), ("SANTA ALREADY CHECKED HIS LIST.", 86, WHT)], [("BRING YOUR ID. SANTA WILL.", 88, WHT)], "36_check_your_registration_v3.png")

c = scene("diner.png", 1.1, 108, 60, blur=1.5)
place(c, eric, 760, 0, "left", bright=0.88, warm=(1.06,0.98,0.9), amt=0.35)
finish(c, [("SANTA'S CHECKING HIS LIST.", 100, YEL)], [("ON ELECTION DAY,", 82, WHT), ("AMERICA CHECKS THEIRS.", 92, YEL)], "23_santa_checking_his_list_v3.png")
