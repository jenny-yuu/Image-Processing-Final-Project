import pyglet
import sys

# 禁止 Pyglet 2.0 的陰影視窗功能
pyglet.options['shadow_window'] = False

from pyglet.gl import *
from pyglet.window import key
import os
import glob
import math
import random

# === 設定參數 ===
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
DATA_DIR = 'processed_data'

print("啟動視覺修復版展示器...")


# --- 魔法粉塵 ---
class MagicDust:
    def __init__(self, count=200):
        self.particles = []
        for _ in range(count):
            self.reset_p()

    def reset_p(self):
        # 限制在球體內部 (半徑 < 1.3)
        while True:
            x = (random.random() - 0.5) * 2.4
            y = (random.random() - 0.5) * 2.4
            z = (random.random() - 0.5) * 2.4
            if x * x + y * y + z * z < 1.5: break
        self.particles.append([x, y, z, random.random() * 0.005])

    def draw(self):
        # 金色光點
        glColor4f(1.0, 1.0, 0.6, 0.8)
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for p in self.particles:
            p[1] += p[3]
            if p[1] > 1.2: p[1] = -1.2
            glVertex3f(p[0], p[1], p[2])
        glEnd()


class CrystalWindow(pyglet.window.Window):
    def __init__(self):
        # 自動適應版本
        config = None
        if pyglet.version.startswith("2"):
            try:
                config = Config(major_version=2, minor_version=1, depth_size=16, double_buffer=True)
            except:
                pass

        try:
            super().__init__(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, caption='Fixed Crystal Ball', config=config)
        except:
            super().__init__(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, caption='Fixed Crystal Ball (Basic)')

        self.batch = pyglet.graphics.Batch()

        # 讀取圖片
        if not os.path.exists(DATA_DIR):
            self.files = []
            print(f"錯誤：找不到 {DATA_DIR}")
        else:
            self.files = sorted(glob.glob(os.path.join(DATA_DIR, '*_fg.png')))
            print(f"找到 {len(self.files)} 張圖片")

        self.idx = 0
        self.rot_y = 0
        self.zoom = -4.5  # 拉遠一點，避免穿模
        self.dust = MagicDust(200)

        self.fg_tex = None
        self.bg_tex = None

        if self.files: self.load_content()

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def load_content(self):
        if not self.files: return
        try:
            f = self.files[self.idx]
            print(f"Loading: {os.path.basename(f)}")

            img = pyglet.image.load(f)
            self.fg_tex = img.get_texture()

            bg_path = f.replace('_fg.png', '_bg.jpg')
            if os.path.exists(bg_path):
                bg_img = pyglet.image.load(bg_path)
                self.bg_tex = bg_img.get_texture()
            else:
                self.bg_tex = None
        except Exception as e:
            print(f"讀取錯誤: {e}")

    def update(self, dt):
        self.rot_y += 0.3

    def on_draw(self):
        self.clear()

        # 3D 投影設定
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width / self.height, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom)
        glRotatef(15, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)

        # === 關鍵修復：啟用混合模式 ===
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # 1. 繪製內部圖片 (關閉深度寫入，避免黑框)
        glDepthMask(GL_FALSE)

        # (A) 背景圖
        if self.bg_tex:
            glColor4f(1, 1, 1, 0.9)  # 稍微透明一點
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.bg_tex.id)
            self.draw_rect(z=-0.3, size=1.8)  # 縮小一點，避免穿出球體
            glDisable(GL_TEXTURE_2D)

        # (B) 前景主角
        if self.fg_tex:
            glColor4f(1, 1, 1, 1)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.fg_tex.id)
            self.draw_rect(z=0.2, size=1.3)
            glDisable(GL_TEXTURE_2D)

        # (C) 粒子
        self.dust.draw()

        # 2. 最後繪製玻璃球 (開啟深度測試，但關閉寫入，讓它看起來是透的)
        self.draw_crystal_sphere()

        # 恢復深度寫入，以免影響下一次繪製
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

    def draw_rect(self, z, size):
        h = size / 2
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0);
        glVertex3f(-h, -h, z)
        glTexCoord2f(1, 0);
        glVertex3f(h, -h, z)
        glTexCoord2f(1, 1);
        glVertex3f(h, h, z)
        glTexCoord2f(0, 1);
        glVertex3f(-h, h, z)
        glEnd()

    def draw_crystal_sphere(self):
        # 玻璃材質設定
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # 光源位置
        glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(5, 5, 10, 1))

        glEnable(GL_COLOR_MATERIAL)
        # 顏色：偏白的藍色，透明度 0.15 (很透)
        glColor4f(0.9, 0.95, 1.0, 0.15)

        # 半徑設大一點 (1.6)，確保包住圖片
        self.manual_sphere(radius=1.6)

        glDisable(GL_LIGHTING)

    def manual_sphere(self, radius):
        lats, longs = 36, 36  # 增加網格密度讓球更圓
        for i in range(lats):
            lat0 = math.pi * (-0.5 + (i - 1) / lats)
            z0 = math.sin(lat0) * radius
            zr0 = math.cos(lat0) * radius
            lat1 = math.pi * (-0.5 + i / lats)
            z1 = math.sin(lat1) * radius
            zr1 = math.cos(lat1) * radius

            glBegin(GL_QUAD_STRIP)
            for j in range(longs + 1):
                lng = 2 * math.pi * (j - 1) / longs
                x = math.cos(lng)
                y = math.sin(lng)

                # 法線與頂點
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0, y * zr0, z0)
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.rot_y += dx * 0.5

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.zoom += scroll_y * 0.2

    def on_key_press(self, symbol, modifiers):
        if not self.files: return
        if symbol == key.RIGHT:
            self.idx = (self.idx + 1) % len(self.files)
            self.load_content()
        elif symbol == key.LEFT:
            self.idx = (self.idx - 1) % len(self.files)
            self.load_content()


if __name__ == "__main__":
    try:
        win = CrystalWindow()
        pyglet.app.run()
    except Exception as e:
        print(f"錯誤: {e}")
        input("按 Enter 離開")