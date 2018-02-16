import kivy
kivy.require('1.10.0')  # replace with your current kivy version !

from kivy.base import EventLoop
from kivy.app import App
from kivy.clock import Clock

from kivy.properties import ObjectProperty

from kivy.uix.widget import Widget

from kivy.graphics import Rectangle
from kivy.atlas import Atlas

import map_tiles


class TileMap(Widget):
    atlas = None
    tiles = []

    def __init__(self, **kwargs):
        atlas_file = kwargs.pop('atlas_file')
        self.atlas = Atlas(atlas_file)
        self.map_array = kwargs.pop('map_array')
        self.map_array.reverse()

        super(TileMap, self).__init__(**kwargs)

    def create_map_tiles(self, tile_pos):
        with self.canvas:
            tile_size = [d * 2 for d in (8, 8)]

            for x in range(len(self.map_array[0])):
                for y in range(len(self.map_array)):
                    tile_pos = (x * 2 * 8, y * 2 * 8)

                    try:
                        texture = self.atlas[str(self.map_array[y][x])]
                        Rectangle(pos=tile_pos, size=tile_size,
                                  texture=texture)
                    except KeyError:
                        pass

    def map_value(self, coord):
        try:
            x, y = coord
            if x < 0 or y < 0:
                # off map, and we don't wrap
                return 0

            return self.map[x][y]
        except Exception:
            return 0


class TileMapGame(Widget):
    app = ObjectProperty(None)

    tile_map = None

    def update(self, _dt):
        if self.tile_map is None:
            self.tile_map = TileMap(atlas_file='map_tiles.atlas',
                                    map_array=map_tiles.map_array)
            self.add_widget(self.tile_map)
            self.tile_map.create_map_tiles((0, 0))


class TileMapApp(App):
    def build(self):
        EventLoop.ensure_window()
        self.window = EventLoop.window
        self.window.size = [d * 2 for d in (224, 288)]
        game = TileMapGame(app=self)

        Clock.schedule_interval(game.update, 1.0 / 60.0)

        return game


if __name__ == '__main__':
    TileMapApp().run()
