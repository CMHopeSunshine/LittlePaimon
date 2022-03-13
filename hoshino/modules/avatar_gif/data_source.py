from os import path
import imageio,random
from typing import List, Tuple
from PIL.Image import Image
from PIL import Image, ImageDraw, ImageFilter

def get_circle_avatar(avatar, size):
    #avatar.thumbnail((size, size))  
    avatar = avatar.resize((size, size))
    scale = 5
    mask = Image.new('L', (size*scale, size*scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size * scale, size * scale), fill=255)
    mask = mask.resize((size, size), Image.ANTIALIAS)
    ret_img = avatar.copy()
    ret_img.putalpha(mask)
    return ret_img

def circle(img: Image) -> Image:
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    img.putalpha(mask)
    return img

def rotate(img: Image, angle: int, expand: bool = True) -> Image:
    return img.rotate(angle, Image.BICUBIC, expand=expand)

def to_jpg(frame: Image, bg_color=(255, 255, 255)) -> Image:
    if frame.mode == 'RGBA':
        bg = Image.new('RGB', frame.size, bg_color)
        bg.paste(frame, mask=frame.split()[3])
        return bg
    else:
        return frame.convert('RGB')

async def eat(frame_dir: str, avatar: Image.Image) -> Image.Image:
    locs = [(180, 60, 100, 100), (184, 75, 100, 100), (183, 98, 100, 100),
            (179, 118, 110, 100), (156, 194, 150, 48), (178, 136, 122, 69),
            (175, 66, 122, 85), (170, 42, 130, 96), (175, 34, 118, 95),
            (179, 35, 110, 93), (180, 54, 102, 93), (183, 58, 97, 92),
            (174, 35, 120, 94), (179, 35, 109, 93), (181, 54, 101, 92),
            (182, 59, 98, 92), (183, 71, 90, 96), (180, 131, 92, 101)]
    raw_frames = []
    for i in range(23):
        raw_frame = Image.open(path.join(frame_dir+'/play', f'{i}.png'))
        raw_frame = raw_frame.convert('RGBA')
        raw_frames.append(raw_frame)
    img_frames = []
    for i in range(len(locs)):
        frame = Image.new(mode='RGB', size=(480, 400),color=(255,255,255))
        x, y, w, h = locs[i]
        avatar = avatar.resize((w,h))
        frame.paste(avatar, (x, y))
        raw_frame = raw_frames[i]
        frame.paste(raw_frame, mask=raw_frame)
        img_frames.append(frame)
    frames = []
    for i in range(2):
        frames.extend(img_frames[0:12])
    frames.extend(img_frames[0:8])
    frames.extend(img_frames[12:18])
    frames.extend(raw_frames[18:23])

    out_path = path.join(frame_dir, 'output.gif')
    imageio.mimsave(out_path, frames, format='gif', duration=0.06)
    return out_path


async def rua(frame_dir: str, avatar: Image.Image) -> Image.Image:
    frames = []
    locs = [(14, 20, 98, 98), (12, 33, 101, 85), (8, 40, 110, 76),
            (10, 33, 102, 84), (12, 20, 98, 98)]
    for i in range(5):
        frame = Image.new('RGBA', (112, 112), (255, 255, 255, 0))
        x, y, w, h = locs[i]
        frame.paste(avatar.resize((w, h), Image.ANTIALIAS), (x, y))
        hand = Image.open(path.join(frame_dir+'/petpet', f'{i}.png')).convert("RGBA")
        frame.paste(hand, mask=hand)
        frames.append(frame)
    out_path = path.join(frame_dir, 'output.gif')
    imageio.mimsave(out_path, frames, format='gif', duration=0.06)
    return out_path

async def kiss(frame_dir: str, another: Image.Image,self: Image.Image) -> Image.Image:
    user_locs = [(58, 90), (62, 95), (42, 100), (50, 100), (56, 100), (18, 120), (28, 110),
                 (54, 100), (46, 100), (60, 100), (35, 115), (20, 120), (40, 96)]
    self_locs = [(92, 64), (135, 40), (84, 105), (80, 110), (155, 82), (60, 96), (50, 80),
                 (98, 55), (35, 65), (38, 100), (70, 80), (84, 65), (75, 65)]
    frames = []
    for i in range(13):
        frame = Image.open(path.join(frame_dir+'/kiss', f'{i}.png')).convert("RGBA")
        another_head = circle(another).resize((50, 50))
        frame.paste(another_head, user_locs[i], mask=another_head)
        self_head = circle(self).resize((40, 40))
        frame.paste(self_head, self_locs[i], mask=self_head)
        frames.append(frame)
    out_path = path.join(frame_dir, 'output.gif')
    imageio.mimsave(out_path, frames, format='gif', duration=0.05)
    return out_path

async def rub(frame_dir: str, another: Image.Image, self: Image.Image) -> Image.Image:
    user_locs = [(39, 91, 75, 75), (49, 101, 75, 75), (67, 98, 75, 75),
                 (55, 86, 75, 75), (61, 109, 75, 75), (65, 101, 75, 75)]
    self_locs = [(102, 95, 70, 80, 0), (108, 60, 50, 100, 0), (97, 18, 65, 95, 0),
                 (65, 5, 75, 75, -20), (95, 57, 100, 55, -70), (109, 107, 65, 75, 0)]
    frames = []
    for i in range(6):
        frame = Image.open(path.join(frame_dir+'/rub', f'{i}.png')).convert("RGBA")
        x, y, w, h = user_locs[i]
        another_head = circle(another).resize((w, h))
        frame.paste(another_head, (x, y), mask=another_head)
        x, y, w, h, angle = self_locs[i]
        self_head = circle(self).resize((w, h))
        self_head = rotate(self_head, angle)
        frame.paste(self_head, (x, y), mask=self_head)
        frames.append(frame)
    out_path = path.join(frame_dir, 'output.gif')
    imageio.mimsave(out_path, frames, format='gif', duration=0.05)
    return out_path

async def pat(frame_dir: str, avatar: Image.Image) -> Image.Image:
    locs = [(11, 73, 106, 100), (8, 79, 112, 96)]
    img_frames = []
    for i in range(10):
        frame = Image.new('RGBA', (235, 196), (255, 255, 255, 0))
        x, y, w, h = locs[1] if i == 2 else locs[0]
        frame.paste(avatar.resize((w, h)), (x, y))
        raw_frame = Image.open(path.join(frame_dir+'/pat', f'{i}.png')).convert("RGBA")
        frame.paste(raw_frame, mask=raw_frame)
        img_frames.append(frame)
    seq = [0, 1, 2, 3, 1, 2, 3, 0, 1, 2, 3, 0, 0, 1, 2, 3,
           0, 0, 0, 0, 4, 5, 5, 5, 6, 7, 8, 9]
    frames = [img_frames[n] for n in seq]
    out_path = path.join(frame_dir, 'output.gif')
    imageio.mimsave(out_path, frames, format='gif', duration=0.085)
    return out_path

async def crawl(frame_dir: str, avatar: Image.Image) -> Image.Image:
    img = circle(avatar).resize((100, 100))
    frame = Image.open(path.join(frame_dir+'/crawl', '{:02d}.jpg'.format(random.randint(1, 92)))).convert("RGBA")
    frame.paste(img, (0, 400), mask=img)
    out_path = path.join(frame_dir, 'output.jpeg')
    frame = frame.convert('RGB')
    frame.save(out_path, format='jpeg')
    return out_path

async def throw(frame_dir: str, avatar: Image.Image) -> Image.Image:
    img = rotate(circle(avatar), random.randint(1, 360),expand=False)
    img = img.resize((143, 143))
    frame = Image.open(path.join(frame_dir+'/throw', '0.png')).convert("RGBA")
    frame.paste(img, (15, 178), mask=img)
    out_path = path.join(frame_dir, 'output.jpeg')
    frame = frame.convert('RGB')
    frame.save(out_path, format='jpeg')
    return out_path

async def support(frame_dir: str, avatar: Image.Image) -> Image.Image:
    support = Image.open(path.join(frame_dir+'/support', '0.png')).convert("RGBA")
    frame = Image.new('RGBA', support.size, (255, 255, 255, 0))
    img = rotate(avatar.resize((815, 815)), 23)
    frame.paste(img, (-172, -17))
    frame.paste(support, mask=support)
    out_path = path.join(frame_dir, 'output.jpeg')
    frame = frame.convert('RGB')
    frame.save(out_path, format='jpeg')
    return out_path

async def rip(frame_dir: str, avatar: Image.Image) -> Image.Image:
    rip = Image.open(path.join(frame_dir+'/rip', '0.png')).convert("RGBA")
    frame = Image.new('RGBA', rip.size, (255, 255, 255, 0))
    left = rotate(avatar.resize((385, 385)), 24)
    right = rotate(avatar.resize((385, 385)), -11)
    frame.paste(left, (-5, 355))
    frame.paste(right, (649, 310))
    frame.paste(rip, mask=rip)
    out_path = path.join(frame_dir, 'output.jpeg')
    frame = frame.convert('RGB')
    frame.save(out_path, format='jpeg')
    return out_path

async def always(frame_dir: str, img: Image.Image) -> Image.Image:
    always = Image.open(path.join(frame_dir+'/always', '0.png')).convert("RGBA")
    w, h = img.size
    h1 = int(h / w * 249)
    h2 = int(h / w * 47)
    height = h1 + h2 + 5

    def paste(img: Image) -> Image:
        img = to_jpg(img)
        frame = Image.new('RGBA', (249, height), (255, 255, 255, 0))
        frame.paste(always, (0, h1 - 249 + int((h2 - 47) / 2)))
        frame.paste(img.resize( (249, h1)), (0, 0))
        frame.paste(img.resize((47, h2)), (140, h1 + 2))
        return frame

    if getattr(img, 'is_animated', False):
        frames = []
        for i in range(img.n_frames):
            img.seek(i)
            frames.append(paste(img))
        out_path = path.join(frame_dir, 'output.gif')
        imageio.mimsave(out_path, frames, format='gif', duration=0.06)
        return out_path
    else:
        img = paste(img)
        out_path = path.join(frame_dir, 'output.jpeg')
        img = img.convert('RGB')
        img.save(out_path, format='jpeg')
        return out_path

avatarFunList1 = [kiss,rub]
avatarFunList2 = [eat,rua,pat]
        