#!/usr/bin/env python3
"""生成桌面宠物橘猫 GIF 动画（趴窝姿态，四腿可见，300 DPI）"""

import os, math, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PIL import Image, ImageDraw

W, H = 400, 400
FPS = 12
FRAMES = 24  # 固定 24 帧（2秒）

# ── 橘猫颜色 ──
O = (255, 159, 67)     # orange
OL = (255, 185, 110)   # light
OD = (224, 128, 48)    # dark
BK = (35, 35, 35)      # black-ish
WH = (255, 255, 255)
PK = (255, 140, 140)   # pink nose
PL = (255, 190, 190)   # light pink
GY = (190, 190, 190)   # gray whiskers
BE = (255, 225, 190)   # belly
ST = (210, 115, 35)    # stripe

# ── 坐标（趴窝猫，正面略侧） ──
BCX, BCY = 200, 290    # body center
BRX, BRY = 135, 52     # body radii

HCX, HCY = 200, 215    # head center
HRX, HRY = 58, 52      # head radii

ELX, ELY = 172, 208    # left eye
ERX, ERY = 228, 208    # right eye
NOSE = (200, 225)

# 腿坐标
FL_L = [(125, 280), (85, 308), (115, 320), (148, 295)]  # front left
FL_R = [(275, 280), (315, 308), (285, 320), (252, 295)]  # front right
BL_L = [(105, 255), (72, 262), (82, 278), (115, 268)]    # back left
BL_R = [(295, 255), (328, 262), (318, 278), (285, 268)]  # back right

# 尾巴
TAIL = [(320, 275), (340, 260), (358, 235), (352, 205), (330, 185), (310, 190)]

# 耳朵
EAR_L = [(163, 175), (138, 125), (188, 163)]
EAR_R = [(237, 175), (262, 125), (212, 163)]
EIL = [(165, 172), (147, 133), (183, 163)]  # inner left
EIR = [(235, 172), (253, 133), (217, 163)]  # inner right


def draw_cat(draw: ImageDraw.Draw, state: str, t: float):
    """绘制整只猫"""
    # ── 动画参数（确保每帧有变化）──
    if state == 'sleeping':
        body_shift = int(6 * math.sin(t * 3.5))
        head_nod = int(3 * math.sin(t * 2.5))
    elif state == 'idle':
        body_shift = int(4 * math.sin(t * 3))
        head_nod = int(2 * math.sin(t * 2))
    elif state == 'studying':
        body_shift = int(3 * math.sin(t * 2))
        head_nod = int(5 * math.sin(t * 3))
    elif state == 'working':
        body_shift = 0
        head_nod = int(6 * math.sin(t * 5))
    elif state == 'happy':
        body_shift = int(3 * math.sin(t * 4))
        head_nod = int(2 * math.sin(t * 3))
    else:
        body_shift = 0
        head_nod = 0

    tail_wag = 0
    if state == 'happy':
        tail_wag = int(25 * math.sin(t * 8))  # 大幅摇尾
    elif state == 'hungry':
        body_shift = int(3 * math.sin(t * 2.5))

    # ── 阴影 ──
    shadow_y = 325 + body_shift
    draw.ellipse([BCX - 100, shadow_y - 5, BCX + 100, shadow_y + 10],
                 fill=(0, 0, 0, 25))

    # ── 尾巴 ──
    tail = list(TAIL)
    tail[-2] = (tail[-2][0] + tail_wag, tail[-2][1] + tail_wag // 2)
    tail[-1] = (tail[-1][0] + tail_wag, tail[-1][1] + tail_wag // 2)
    # Draw tail as thick line
    for i in range(len(tail) - 1):
        draw.line([tail[i], tail[i + 1]], fill=O, width=18)
    # Tail outline
    for i in range(len(tail) - 1):
        draw.line([tail[i], tail[i + 1]], fill=OD, width=2)

    # ── 后腿 ──
    for leg in [BL_L, BL_R]:
        draw.polygon(leg, fill=OD, outline=BK)
        cx = sum(p[0] for p in leg) // 4
        cy = sum(p[1] for p in leg) // 4
        draw.ellipse([cx - 7, cy - 4, cx + 7, cy + 3], fill=OL, outline=BK)

    # ── 身体 ──
    by = BCY + body_shift
    draw.ellipse([BCX - BRX, by - BRY, BCX + BRX, by + BRY],
                 fill=O, outline=BK)
    # 肚皮
    draw.ellipse([BCX - BRX + 28, by - 12, BCX + BRX - 28, by + BRY - 5],
                 fill=BE)
    # 背部条纹
    for i in range(5):
        sx = BCX - BRX + 30 + i * 48
        draw.arc([sx - 16, by - BRY + 6, sx + 16, by + BRY - 6],
                 5, 175, fill=ST, width=3)

    # ── 前腿 ──
    for leg in [FL_L, FL_R]:
        draw.polygon(leg, fill=O, outline=BK)
        px, py = leg[1][0], leg[1][1]
        draw.ellipse([px - 11, py - 5, px + 5, py + 7], fill=OL, outline=BK)

    # ── 头部 ──
    hx, hy = HCX, HCY + body_shift + head_nod
    draw.ellipse([hx - HRX, hy - HRY, hx + HRX, hy + HRY],
                 fill=O, outline=BK)
    # 脸部浅色区
    draw.ellipse([hx - 38, hy - 22, hx + 38, hy + 24], fill=OL)

    # ── 耳朵 ──
    draw.polygon(EAR_L, fill=O, outline=BK)
    draw.polygon(EAR_R, fill=O, outline=BK)
    draw.polygon(EIL, fill=PL)
    draw.polygon(EIR, fill=PL)

    # ── 额头 M ──
    mx, my = hx, hy - HRY + 10
    draw.line([mx - 12, my + 10, mx - 6, my, mx, my + 10], fill=OD, width=2)
    draw.line([mx + 12, my + 10, mx + 6, my, mx, my + 10], fill=OD, width=2)

    # ── 眼睛 ──
    if state == 'sleeping':
        for ex, ey in [(ELX, ELY + body_shift + head_nod), (ERX, ERY + body_shift + head_nod)]:
            draw.arc([ex - 13, ey + 3, ex + 13, ey + 12], 0, 180, fill=BK, width=3)
    elif state == 'happy':
        for ex, ey in [(ELX, ELY + body_shift), (ERX, ERY + body_shift)]:
            draw.arc([ex - 14, ey - 8, ex + 14, ey + 5], 0, 180, fill=BK, width=3)
    elif state == 'hungry':
        for ex, ey in [(ELX, ELY + body_shift), (ERX, ERY + body_shift)]:
            draw.ellipse([ex - 14, ey - 4, ex + 14, ey + 14], fill=WH, outline=BK)
            draw.rectangle([ex - 15, ey - 4, ex + 15, ey + 2], fill=OL)
            draw.ellipse([ex - 5, ey + 4, ex + 3, ey + 11], fill=BK)
        # 泪水
        draw.ellipse([ELX - 24, ELY + 8, ELX - 14, ELY + 22], fill=(100, 180, 255, 160))
    elif state in ('studying', 'working'):
        for ex, ey in [(ELX, ELY + body_shift + head_nod), (ERX, ERY + body_shift + head_nod)]:
            draw.ellipse([ex - 14, ey - 7, ex + 14, ey + 10], fill=WH, outline=BK)
            draw.ellipse([ex - 3, ey - 1, ex + 5, ey + 5], fill=BK)
        if state == 'studying':
            for ex, ey in [(ELX, ELY + body_shift + head_nod), (ERX, ERY + body_shift + head_nod)]:
                draw.ellipse([ex - 18, ey - 11, ex + 18, ey + 14], outline=(60, 60, 60), width=2)
            ex1, ey1 = ELX, ELY + body_shift + head_nod
            ex2 = ERX
            draw.line([ex1 + 18, ey1, ex2 - 18, ey1], fill=(60, 60, 60), width=2)
        else:  # working: 眉毛
            draw.line([ELX - 18, ELY - 12 + body_shift + head_nod, ELX + 8, ELY - 10 + body_shift + head_nod], fill=BK, width=3)
            draw.line([ERX + 18, ERY - 12 + body_shift + head_nod, ERX - 8, ERY - 10 + body_shift + head_nod], fill=BK, width=3)
    else:  # idle
        for ex, ey in [(ELX, ELY + body_shift), (ERX, ERY + body_shift)]:
            draw.ellipse([ex - 14, ey - 8, ex + 14, ey + 10], fill=WH, outline=BK)
            draw.ellipse([ex - 4, ey - 3, ex + 7, ey + 7], fill=BK)
            draw.ellipse([ex - 9, ey - 6, ex - 2, ey], fill=WH)

    # ── 鼻子 ──
    ny = NOSE[1] + body_shift + head_nod
    draw.ellipse([NOSE[0] - 5, ny - 3, NOSE[0] + 5, ny + 4], fill=PK, outline=BK)

    # ── 嘴巴 ──
    my = ny + 5
    if state == 'happy':
        draw.arc([NOSE[0] - 14, my - 2, NOSE[0] + 14, my + 16], 0, 180, fill=BK, width=2)
    elif state == 'hungry':
        draw.arc([NOSE[0] - 8, my + 4, NOSE[0] + 8, my + 14], 180, 360, fill=BK, width=2)
    else:
        draw.arc([NOSE[0] - 8, my - 1, NOSE[0] + 8, my + 10], 0, 180, fill=BK, width=2)

    # ── 胡须 ──
    for side in [-1, 1]:
        bx = hx + side * 28
        by = hy + 8
        for dy in [-6, 0, 6]:
            draw.line([bx, by + dy, bx + side * 42, by + dy + dy // 3], fill=GY, width=1)

    # ── 状态特效 ──
    if state == 'happy':
        for sx in [hx - 36, hx + 36]:
            draw.ellipse([sx - 9, hy + 2, sx + 9, hy + 14], fill=(255, 150, 150, 70))
    elif state == 'working':
        swx = hx + HRX + 10 + int(3 * math.sin(t * 6))
        swy = hy - HRY + 10
        draw.ellipse([swx, swy, swx + 12, swy + 24], fill=(100, 200, 255, 140), outline=(80, 180, 255))
    elif state == 'sleeping':
        zx = hx + HRX + 10
        zy = hy - HRY + 5
        draw.text((zx, zy), "zZ", fill=(90, 90, 180, 200))
    elif state == 'hungry':
        # 肚子咕咕叫波纹
        bx, by2 = BCX - 20, BCY + BRY - 10
        r = int(8 + 4 * math.sin(t * 6))
        if r > 8:
            draw.ellipse([bx - r, by2 - r // 2, bx + r, by2 + r // 2],
                         outline=(100, 100, 100, 100), width=1)


def make_animation(state: str, out_dir: str):
    """生成带透明背景的 PNG 帧序列"""
    import shutil
    state_dir = os.path.join(out_dir, state)
    if os.path.exists(state_dir):
        shutil.rmtree(state_dir)
    os.makedirs(state_dir)

    for i in range(FRAMES):
        t = i / FPS
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_cat(draw, state, t)
        # 抗去重
        img.putpixel((0, 0), (0, 0, 0, 0))
        frame_path = os.path.join(state_dir, f'{i:03d}.png')
        img.save(frame_path, 'PNG')

    size_kb = sum(os.path.getsize(os.path.join(state_dir, f)) for f in os.listdir(state_dir)) / 1024
    print(f'  {state:10s} → {state_dir}/  ({FRAMES} frames, {size_kb:.0f} KB)')


def main():
    assets = os.path.join(os.path.dirname(__file__), '..', 'assets')
    os.makedirs(assets, exist_ok=True)

    # 清理旧 GIF
    for old in ['pet_idle.gif', 'pet_happy.gif', 'pet_hungry.gif',
                'pet_studying.gif', 'pet_working.gif', 'pet_sleeping.gif']:
        old_path = os.path.join(assets, old)
        if os.path.exists(old_path):
            os.remove(old_path)

    states = ['idle', 'happy', 'hungry', 'studying', 'working', 'sleeping']
    print(f'Generating {len(states)} animations ({W}x{H}px, {FPS}fps, {FRAMES} PNG frames)...')
    for state in states:
        make_animation(state, assets)
    print('Done!')


if __name__ == '__main__':
    main()
