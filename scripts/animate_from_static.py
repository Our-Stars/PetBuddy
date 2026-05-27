#!/usr/bin/env python3
"""从静态图生成动画帧：基于原图施加细微变换（呼吸、摆动等）"""

import os, math, shutil
from PIL import Image

FRAMES = 24
FPS = 12
OUT_W, OUT_H = 400, 400


def apply_anim(img: Image.Image, state: str, t: float) -> Image.Image:
    """对原图施加动画变换，返回新帧"""
    w, h = img.size

    if state == 'idle':
        # 呼吸：轻微缩放
        scale = 1.0 + 0.03 * math.sin(t * 3)
        new_w = int(w * scale)
        new_h = int(h * scale)
        frame = img.resize((new_w, new_h), Image.LANCZOS)
    elif state == 'happy':
        # 弹跳 + 左右微摆
        scale = 1.0 + 0.05 * abs(math.sin(t * 6))
        rot = 3 * math.sin(t * 8)
        new_w = int(w * scale)
        new_h = int(h * scale)
        frame = img.resize((new_w, new_h), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
    elif state == 'hungry':
        # 微弱前后晃
        scale = 1.0 + 0.02 * math.sin(t * 2.5)
        rot = 2 * math.sin(t * 3)
        new_w = int(w * scale)
        new_h = int(h * scale)
        frame = img.resize((new_w, new_h), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
    elif state == 'studying':
        # 轻微点头
        scale = 1.0 + 0.02 * math.sin(t * 3)
        offset_y = int(5 * math.sin(t * 3))
        new_w = int(w * scale)
        new_h = int(h * scale)
        frame = img.resize((new_w, new_h), Image.LANCZOS)
        # 下移模拟点头
        shifted = Image.new('RGBA', (new_w + 10, new_h + 10 + abs(offset_y)), (0, 0, 0, 0))
        shifted.paste(frame, (5, 5 + max(0, offset_y)), frame)
        frame = shifted
    elif state == 'working':
        # 微微颤动
        scale = 1.0 + 0.015 * math.sin(t * 7)
        offset_x = int(2 * math.sin(t * 10))
        offset_y = int(2 * math.cos(t * 10))
        new_w = int(w * scale)
        new_h = int(h * scale)
        frame = img.resize((new_w, new_h), Image.LANCZOS)
        shifted = Image.new('RGBA', (new_w + 4, new_h + 4), (0, 0, 0, 0))
        shifted.paste(frame, (2 + offset_x, 2 + offset_y), frame)
        frame = shifted
    elif state == 'sleeping':
        # 深呼吸
        scale = 1.0 + 0.06 * math.sin(t * 3.5)
        new_w = int(w * scale)
        new_h = int(h * scale)
        frame = img.resize((new_w, new_h), Image.LANCZOS)
    else:
        frame = img.copy()

    # 居中裁剪/填充到固定输出尺寸
    fw, fh = frame.size
    canvas = Image.new('RGBA', (OUT_W, OUT_H), (0, 0, 0, 0))
    px = (OUT_W - fw) // 2
    py = (OUT_H - fh) // 2
    canvas.paste(frame, (px, py), frame if frame.mode == 'RGBA' else None)
    return canvas


def make_animation(state: str, src_path: str, out_dir: str):
    """读取静态图，生成帧序列"""
    img = Image.open(src_path).convert('RGBA')
    state_dir = os.path.join(out_dir, state)
    if os.path.exists(state_dir):
        shutil.rmtree(state_dir)
    os.makedirs(state_dir)

    for i in range(FRAMES):
        t = i / FPS
        frame = apply_anim(img, state, t)
        frame.save(os.path.join(state_dir, f'{i:03d}.png'), 'PNG')

    print(f'  {state:10s} → {state_dir}/  ({FRAMES} frames)')


def main():
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Original static image')
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')

    states = {
        'idle': 'pet_idle.png',
        'happy': 'pet_happy.png',
        'hungry': 'pet_hungry.png',
        'studying': 'pet_studying.png',
        'working': 'pet_working.png',
        'sleeping': 'pet_sleeping.png',
    }

    print(f'Generating animations from static images ({FRAMES} frames, {FPS}fps)...')
    for state, fname in states.items():
        src = os.path.join(src_dir, fname)
        if not os.path.exists(src):
            print(f'  SKIP {state}: {src} not found')
            continue
        # 清理旧帧
        old_dir = os.path.join(out_dir, state)
        if os.path.exists(old_dir):
            shutil.rmtree(old_dir)
        make_animation(state, src, out_dir)

    print('Done!')


if __name__ == '__main__':
    main()
