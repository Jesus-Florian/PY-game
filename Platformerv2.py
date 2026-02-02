import os
import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Run Away! JF"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 6
GRAVITY = 1.5
PLAYER_JUMP_SPEED = 18

# Starting position of the player
PLAYER_START_X = 128
PLAYER_START_Y = 800

# Threshold Y position below which the game ends
GAME_OVER_Y_THRESHOLD = -100

# Layer Names from our TileMap
LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_LADDERS = "Ladder"
LAYER_NAME_TREASURE_CHEST = "Treasure Chest"
LAYER_NAME_FLAG = "Flag"
LAYER_NAME_ENEMIES = "Enemies"


class Enemy(arcade.Sprite):
    """Enemy class to follow the player."""

    def __init__(self, image, scaling):
        super().__init__(image, scaling)
        self.speed = 4  # Speed of the enemy

    def follow_player(self, player_sprite):
        """Move towards the player sprite."""
        if self.center_x < player_sprite.center_x:
            self.change_x = self.speed  # Move right
        elif self.center_x > player_sprite.center_x:
            self.change_x = -self.speed  # Move left
        else:
            self.change_x = 0  # Stop moving horizontally

        if self.center_y < player_sprite.center_y:
            self.change_y = self.speed  # Move up
        elif self.center_y > player_sprite.center_y:
            self.change_y = -self.speed  # Move down
        else:
            self.change_y = 0  # Stop moving vertically


class MyGame(arcade.Window):
    """Main application class."""

    def __init__(self):
        # Initialize the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the path to start with this program
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Initialize game-related variables
        self.tile_map = None
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.game_over = False
        self.game_won = False  # Add variable to track if the player won
        self.elapsed_time = 0  # Timer for the game
        self.end_of_map = 0
        self.enemy_sprite = None  # Add enemy sprite

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over_sound = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.win_sound = arcade.load_sound(":resources:sounds/upgrade1.wav")  # Sound for winning

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.game_over = False
        self.game_won = False  # Reset the win condition
        self.score = 0
        self.elapsed_time = 0  # Reset timer

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Load the map
        map_name = "LEVEL_1.json"
        layer_options = {
            LAYER_NAME_PLATFORMS: {"use_spatial_hash": True},
            LAYER_NAME_MOVING_PLATFORMS: {"use_spatial_hash": False},
            LAYER_NAME_LADDERS: {"use_spatial_hash": True},
            LAYER_NAME_COINS: {"use_spatial_hash": True},
            LAYER_NAME_ENEMIES: {"use_spatial_hash": True},  # Use spatial hash for enemies
        }
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set up the player
        image_source = "robot_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite("Player", self.player_sprite)

        # Create the enemy
        self.enemy_sprite = Enemy("saw.png", CHARACTER_SCALING)
        self.enemy_sprite.center_x = 0  # Starting position of enemy
        self.enemy_sprite.center_y = 900  # Starting position of enemy
        self.scene.add_sprite(LAYER_NAME_ENEMIES, self.enemy_sprite)

        # Calculate the right edge of the map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # Set the background color from the tile map, if specified
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the physics engine, including ladders and platforms
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=GRAVITY,
            ladders=self.scene[LAYER_NAME_LADDERS],
            walls=self.scene[LAYER_NAME_PLATFORMS]
        )

    def on_draw(self):
        """Render the screen."""
        self.clear()

        # If the game is over, display Game Over message
        if self.game_over:
            arcade.draw_text(
                "Game Over",
                self.width // 2,
                self.height // 2,
                arcade.color.RED,
                54,
                anchor_x="center"
            )
            arcade.draw_text(
                "Press R to Restart",
                self.width // 2,
                self.height // 2 - 60,
                arcade.color.WHITE,
                24,
                anchor_x="center",
            )
            return

        # If the player won, display Win message
        if self.game_won:
            arcade.draw_text(
                "You Win!",
                self.width // 2,
                self.height // 2,
                arcade.color.GREEN,
                54,
                anchor_x="center"
            )
            arcade.draw_text(
                "Press R to Restart",
                self.width // 2,
                self.height // 2 - 60,
                arcade.color.WHITE,
                24,
                anchor_x="center",
            )
            return

        # Activate the game camera and draw the scene
        self.camera.use()
        self.scene.draw()

        # Activate the GUI camera to draw the score and timer
        self.gui_camera.use()
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)

        # Draw the timer
        timer_text = f"Time: {int(self.elapsed_time)} seconds"
        arcade.draw_text(timer_text, 10, 40, arcade.csscolor.WHITE, 18)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if self.game_over or self.game_won:
            # Restart game if "R" is pressed
            if key == arcade.key.R:
                self.setup()
            return

        # Jump and move left/right
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key in [arcade.key.UP, arcade.key.DOWN, arcade.key.W, arcade.key.S]:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = 0
        elif key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def update(self, delta_time):
        """Movement and game logic"""
        if self.game_over or self.game_won:
            return

        # Move the player with the physics engine
        self.physics_engine.update()

        # Update the enemy's position to follow the player
        self.enemy_sprite.follow_player(self.player_sprite)
        self.enemy_sprite.update()

        # Check for collision between player and enemy
        if arcade.check_for_collision(self.player_sprite, self.enemy_sprite):
            arcade.play_sound(self.game_over_sound)
            self.game_over = True
            return

        # Update the timer
        self.elapsed_time += delta_time

        # Check if player falls below the threshold Y position
        if self.player_sprite.center_y < GAME_OVER_Y_THRESHOLD:
            arcade.play_sound(self.game_over_sound)
            self.game_over = True
            return

        # Check for collisions with coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_COINS]
        )
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        # Check for collision with the flag
        flag_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_FLAG]
        )
        if flag_hit_list:
            self.game_won = True
            arcade.play_sound(self.win_sound)

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
