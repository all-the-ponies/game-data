from concurrent.futures import Future, ThreadPoolExecutor
import ctypes
import ctypes.util
import os
from pathlib import Path
import math
import shutil

import cairo
import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango
from gi.repository import PangoCairo

from ..GameDataTypes import CollectionEntry, GameData, Language
from ..console import console, track

font_config = ctypes.CDLL(ctypes.util.find_library("fontconfig"))


class CollectionImageGenerator:
    TEMPLATE_PATH = 'assets/collections/og-image-template.png'

    FONTS = {
        'Celestia Redux': 'CelestiaRedux.ttf',
        'Eunjin': 'Eunjin.ttf',
        'Noto Sans JP': 'NotoSansJPBold.ttf',
        'Quark': 'QuarkBold.ttf',
        'Tajawal': 'TajawalBold.ttf',
        'WenQuanYi Micro Hei': 'Wqymicrohei.ttf',
    }

    LANGUAGE_FONTS: dict[Language, str] = {
        'english': 'Celestia Redux',
        'french': 'Celestia Redux',
        'german': 'Celestia Redux',
        'italian': 'Celestia Redux',
        'spanish': 'Celestia Redux',
        'japanese': 'Noto Sans JP',
        'korean': 'Eunjin',
        'chinese': 'WenQuanYi Micro Hei',
        'brazilian portuguese': 'Celestia Redux',
        'russian': 'Celestia Redux',
        'turkish': 'Celestia Redux',
        'arabic': 'Tajawal',
        'thai': 'Quark',
    }

    PORTRAIT_SIZE = (200, 160)
    GRID_CENTER = (430, 365)

    def __init__(
        self,
        game_data: GameData,
        dist_folder: str | Path,
    ) -> None:
        self.game_data = game_data
        self.dist_folder = Path(dist_folder)
        self.assets_folder = Path('assets')
        self.base_output = self.dist_folder/'images/collections'
        shutil.rmtree(self.base_output, ignore_errors = True)

        self.load_fonts()

        self.image_encode_threader = ThreadPoolExecutor()
        self.image_futures: list[Future] = []

        self.template = cairo.ImageSurface.create_from_png(self.TEMPLATE_PATH)
        self.create_images()

    
    def load_fonts(self):
        base = self.assets_folder/'fonts'
        
        for font in self.FONTS.values():
            font_config.FcConfigAppFontAddFile(None, str(base / font).encode('utf-8'))
    

    def create_images(self):
        try:
            for collection in track(
                self.game_data.collection_data.collections.values(),
                description = 'Generating collection images...',
            ):
                self.draw_collection(collection)

            for future in track(self.image_futures, description = 'Finishing writing files'):
                future.result()
            
        except KeyboardInterrupt:
            self.image_encode_threader.shutdown(cancel_futures = True, wait = True)
            raise
        finally:
            self.image_encode_threader.shutdown(wait = True)

        self.image_futures.clear()
        
    

    def draw_collection(self, collection: CollectionEntry):
        base_surface = self.draw_collection_base(collection)
        width, height = base_surface.get_width(), base_surface.get_height()

        reward = self.game_data.get_object(collection.reward.main.item)

        for language, path in collection.image.items():
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(surface)

            ctx.set_source_surface(base_surface)
            ctx.paint()

            font_family = 'Celestia Redux'

            if (self.LANGUAGE_FONTS[language] != font_family):
                font_family += f', {self.LANGUAGE_FONTS[language]}'

            
            self.draw_text(
                ctx,
                collection.name[language],
                font_family,
                50,
                width / 2,
                120,
                width,
                center = True,
                color = (255, 255, 255, 1),
                shadow_color = (0,0,0,0.3),
                shadow_offset = (0, 3),
            )

            if reward is not None:
                self.draw_text(
                    ctx,
                    reward.name[language], # type: ignore
                    font_family,
                    30,
                    959,
                    270,
                    360,
                    center = True,
                    color = (255, 255, 255, 1),
                    shadow_color = (0,0,0,0.3),
                    shadow_offset = (0, 3),
                )
            
            output = self.dist_folder/path
            output.parent.mkdir(parents = True, exist_ok = True)

            collection.image[language] = output.relative_to(self.dist_folder).as_posix()
            
            self.image_futures.append(self.image_encode_threader.submit(surface.write_to_png, output))
        
        base_surface.finish()
    
    def draw_collection_base(self, collection: CollectionEntry):
        width, height = self.template.get_width(), self.template.get_height()

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.set_source_surface(self.template, 0, 0)
        ctx.paint()

        portraits: list[cairo.ImageSurface] = []

        for item in collection.ponies:
            pony = self.game_data.game_objects.pony.objects[item.item]
            path = self.dist_folder/pony.image['portrait'].path
            portraits.append(cairo.ImageSurface.create_from_png(path))
        
        self.draw_image_grid(ctx, portraits, self.PORTRAIT_SIZE, (15, 15), self.GRID_CENTER)

        reward = self.game_data.get_object(collection.reward.main.item)
        if reward is not None:
            reward_image = cairo.ImageSurface.create_from_png(self.dist_folder/reward.image['main'].path)
            self.draw_scaled_centered(ctx, reward_image, 960, 400, (170, 170))

            if collection.reward.main.amount > 1:
                self.draw_text(
                    ctx,
                    str(collection.reward.main.amount),
                    'Celestia Redux',
                    30,
                    1020,
                    470,
                    color = (255, 255, 255, 1),
                    center = True,
                    shadow_color = (0,0,0,0.3),
                    shadow_offset = (0, 3),
                )
        else:
            console.print(f'[red]Could not find reward: {collection.reward.main.item}[/]')
        
        return surface
        

    def get_grid_size(self, n: int) -> tuple[int, int]:
        if n <= 2:
            return 2, 1
        else:
            return math.ceil(n / 2), 2
    
    def compute_grid_positions(
        self,
        n: int,
        cell_size: tuple[float, float],
        spacing: tuple[float, float],
        center: tuple[float, float],
    ) -> list[tuple[float, float]]:
        cols, rows = self.get_grid_size(n)

        total_width = cols * cell_size[0] + (cols - 1) * spacing[0]
        total_height = rows * cell_size[1] + (rows - 1) * spacing[1]

        grid_left = center[0] - total_width / 2
        grid_top = center[1] - total_height / 2

        positions: list[tuple[float, float]] = []
        remaining = n
        col = 0
        while remaining > 0:
            items_in_col = min(rows, remaining)
            col_x = grid_left + col * (cell_size[0] + spacing[1])

            for row in range(items_in_col):
                y = grid_top + row * (cell_size[1] + spacing[0])
                positions.append((col_x + cell_size[0] / 2, y + cell_size[1] / 2))

            remaining -= items_in_col
            col += 1

        return positions

    def draw_scaled_centered(
        self,
        ctx: cairo.Context,
        image_surface: cairo.ImageSurface,
        x: float,
        y: float,
        size: tuple[float, float],
    ) -> None:
        img_w = image_surface.get_width()
        img_h = image_surface.get_height()

        scale = min(size[0] / img_w, size[1] / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale

        offset_x = x - draw_w / 2
        offset_y = y - draw_h / 2


        # self.draw_box(ctx, offset_x, offset_y, draw_w, draw_h)

        ctx.save()
        ctx.translate(offset_x, offset_y)
        ctx.scale(scale, scale)
        ctx.set_source_surface(image_surface)
        ctx.paint()
        ctx.restore()

    def draw_box(self, ctx: cairo.Context, left: float, top: float, width: float, height: float):
        """Draw a box on a given context."""
        ctx.save()
        ctx.rectangle(left, top, width, height)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        ctx.rectangle(left, top, width, height)
        ctx.set_source_rgb(0, 0, 0)
        ctx.stroke()
        ctx.restore()

    def draw_image_grid(
        self,
        ctx: cairo.Context,
        image_surfaces: list[cairo.ImageSurface],
        cell_size: tuple[float, float],
        spacing: tuple[float, float],
        center: tuple[float, float],
    ) -> None:
        n = len(image_surfaces)
        positions = self.compute_grid_positions(n, cell_size, spacing, center)

        for surface, (x, y) in zip(image_surfaces, positions):
            self.draw_scaled_centered(ctx, surface, x, y, cell_size)

    def draw_text(
        self,
        ctx: cairo.Context,
        text: str,
        font_family: str,
        font_size: int,
        x: float,
        y: float,
        max_width: float | None = None,
        center: bool = True,
        color: tuple[float, float, float, float] = (0, 0, 0, 1),
        shadow_color: tuple[float, float, float, float] | None = None,
        shadow_offset: tuple[float, float] = (0, 3),
    ):
        layout = PangoCairo.create_layout(ctx)
        font_desc = Pango.FontDescription()
        font_desc.set_family(font_family)
        font_desc.set_size(font_size * Pango.SCALE)

        layout.set_font_description(font_desc)
        if center:
            layout.set_alignment(Pango.Alignment.CENTER)

        if max_width is not None:
            layout.set_width(int(max_width * Pango.SCALE))
            layout.set_wrap(Pango.WrapMode.WORD_CHAR)

        layout.set_text(text)  # Pango handles RTL/bidi automatically per-script

        ink, logical = layout.get_pixel_extents()

        if center:
            draw_x = x - logical.width / 2 - logical.x
            draw_y = y - logical.height / 2 - logical.y
        else:
            draw_x, draw_y = x, y
        
        if shadow_color is not None:
            offset_x, offset_y = shadow_offset
            ctx.save()
            ctx.set_source_rgba(*shadow_color)
            ctx.translate(draw_x + offset_x, draw_y + offset_y)
            PangoCairo.show_layout(ctx, layout)
            ctx.restore()

        ctx.save()
        ctx.set_source_rgba(*color)
        ctx.translate(draw_x, draw_y)
        PangoCairo.show_layout(ctx, layout)
        ctx.restore()
