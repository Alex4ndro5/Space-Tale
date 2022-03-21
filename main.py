#Import
import arcade
import pathlib

#Game constants
#Window dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Dark Tale"

#Scaling constants
MAP_SCALING = 1.0

#Player constants
GRAVITY = 1.0
PLAYER_START_X = 65
PLAYER_START_Y = 256

#Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets"

class Platformer(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        #Sets of sprites
        self.coins = None
        self.background = None
        self.walls = None
        self.ladders = None
        self.goals = None
        self.enemies = None

        #Sprite for player
        self.player = None

        #Physics engine
        self.physics_engine = None

        #Score
        self.score = 0

        #Level number
        self.level = 1

        #Sounds
        self.coin_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "coin.wav")
        )
        self.jump_sound = arcade.load_sound(
            str(ASSETS_PATH / "sounds" / "jump.wav")
        )
        self.victory_sound = arcade.load_sound(

            str(ASSETS_PATH / "sounds" / "victory.wav")
        )
    def setup(self) -> None:
        map_name = f"platform_level_{self.level:02}.tmx"
        map_path = ASSETS_PATH / map_name

        #names of layers
        wall_layer = "ground"
        coin_layer = "coins"
        goal_layer = "goal"
        background_layer = "background"
        ladders_layer = "ladders"

        #load map
        game_map = arcade.tilemap.read_tmx(str(map_path))

        #load layers
        self.background = arcade.tilemap.proccess_layer(
            game_map, layer_name=background_layer, scaling=MAP_SCALING
        )
        self.goals = arcade.tilemap.proccess_layer(
            game_map, layer_name=goal_layer, scaling=MAP_SCALING
        )
        self.walls = arcade.tilemap.proccess_layer(
            game_map, layer_name=wall_layer, scaling=MAP_SCALING
        )
        self.ladders = arcade.tilemap.proccess_layer(
            game_map, layer_name=ladders_layer, scaling=MAP_SCALING
        )
        self.coins = arcade.tilemap.proccess_layer(
            game_map, layer_name=coin_layer, scaling=MAP_SCALING
        )

        #background color
        background_color = arcade.color.FRESH_AIR
        if game_map.background_color:
            background_color = game_map.background_color
        arcade.set_background_color(background_color)

        #player sprite
        if not self.player:
            self.player = self.create_player_sprite()

        #start cords
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.player.change_x = 0
        self.player.change_y = 0

        #physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            platforms=self.walls,
            gravity_constant=GRAVITY,
            ladders=self.ladders,
        )
    def create_player_sprite(self) -> arcade.AnimatedWalkingSprite:

        #location of player images
        texture_path = ASSETS_PATH / "images" / "player"

        #textures
        walking_paths = [
            texture_path / f"alienGreen_walk{x}.png" for x in (1, 2)
        ]
        climbing_paths = [
            texture_path / f"alienGreen_climb{x}.png" for x in (1, 2)
        ]
        standing_path = texture_path / "alienGreen_stand.png"

        #loading textures
        walking_right_textures = [
            arcade.load_texture(texture) for texture in walking_paths
        ]
        walking_left_textures = [
            arcade.load_texture(texture, mirrored=True) for texture in walking_paths
        ]

        walking_up_textures = [
            arcade.load_texture(texture) for texture in climbing_paths
        ]
        walking_down_textures = [
            arcade.load_texture(texture) for texture in climbing_paths
        ]

        standing_right_textures = [
            arcade.load_texture(standing_path)
        ]
        standing_left_textures = [
            arcade.load_texture(standing_path, mirrored=True)
        ]

        #create sprite
        player = arcade.AnimatedWalkingSprite()

        #player textures
        player.stand_left_textures = standing_left_textures
        player.stand_right_textures = standing_right_textures
        player.walk_left_textures = walking_left_textures
        player.walk_right_textures = walking_right_textures
        player.walk_up_textures = walking_up_textures
        player.walk_down_textures = walking_down_textures

        #player defaults
        player.center_x = PLAYER_START_X
        player.center_y = PLAYER_START_Y
        player.state = arcade.FACE_RIGHT

        #initial texture
        player.texture = player.stand_right_textures[0]

        return player

    #def on_key_press(self, symbol: int, modifiers: int):

    #def on_key_release(self, symbol: int, modifiers: int):

    #def on_update(self, delta_time: float):

    def on_draw(self) -> None:
        arcade.start_render()

        #draw sprites
        self.background.draw()
        self.walls.draw()
        self.coins.draw()
        self.goals.draw()
        self.ladders.draw()
        self.player.draw()

if __name__ == "__main__":
    window = Platformer()
    window.setup()
    arcade.run()
#nigga




