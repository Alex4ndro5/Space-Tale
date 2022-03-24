"""
Platformer Game
"""
import arcade
from pathlib import Path

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Space Tale"
ASSETS_PATH = Path(__file__).absolute().parent / "assets"

# Constants used to scale sprites
CHARACTER_SCALING = 0.5
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# Player starting position
PLAYER_START_X = 64
PLAYER_START_Y = 225

# Layer Names from our TileMap
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_DONT_TOUCH = "Don't Touch"
LAYER_NAME_GOALS = "Goal"
LAYER_NAME_LADDERS = "Ladders"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # TileMap Object
        self.tile_map = None

        # Scene Object
        self.scene = None

        # Variable that holds the player sprite
        self.player_sprite = None

        # Physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score = 0

        # Keep track of level
        self.level = 1

        # Edge of the map
        self.end_of_map = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(ASSETS_PATH / "sounds" / "coin.mp3")
        self.jump_sound = arcade.load_sound(ASSETS_PATH / "sounds" / "jump.mp3")
        self.victory_sound = arcade.load_sound(ASSETS_PATH / "sounds" / "victory.mp3")

        arcade.set_background_color(arcade.csscolor.AQUA)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Name of map file to load
        map_name = ASSETS_PATH / "tiled" / f"platform_level_{self.level}.json"

        # Layer Specific Options for the Tilemap
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DONT_TOUCH: {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Keep track of the score
        self.score = 0

        # Makes foreground appear before player
        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        # Sets up the player, specifically placing it at these coordinates.
        image_source = ASSETS_PATH / "images" / "player"
        self.player_sprite = arcade.Sprite(image_source / "alienGreen_stand.png", CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite("Player", self.player_sprite)

        # Sets the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Creates the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene[LAYER_NAME_PLATFORMS]
        )

    def on_draw(self):
        """Render the screen."""

        # Clears the screen to the background color
        self.clear()

        # Activates the game camera
        self.camera.use()

        # Draws Scene
        self.scene.draw()

        # Activates the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draws score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.BLACK,
            18,
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Moves the player with the physics engine
        self.physics_engine.update()

        goals_hit = arcade.check_for_collision_with_list(
            sprite=self.player_sprite, sprite_list=self.scene[LAYER_NAME_GOALS]
        )
        # Fall out of map protection
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y

        # Player collision with trap/enemy
        if arcade.check_for_collision_with_list(
                self.player_sprite, self.scene[LAYER_NAME_DONT_TOUCH]
        ):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
        if goals_hit:
            # Play the victory sound
            self.victory_sound.play()

            # Set up the next level
            self.level += 1
            self.setup()

        # Sees if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_COINS]
        )

        # Loops through each coin we hit (if any) and removes it
        for coin in coin_hit_list:
            # Removes the coin
            coin.remove_from_sprite_lists()
            # Plays a sound
            arcade.play_sound(self.collect_coin_sound)
            # Adds one to the score
            self.score += int(coin.properties["point_value"])

        # Positions the camera
        self.center_camera_to_player()

        # Calculate the right edge of the map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # Stops player form leaving map
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0

        if self.player_sprite.right >= self.end_of_map:
            self.player_sprite.right = self.end_of_map


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()