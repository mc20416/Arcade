"""
This is a Platformer Game built using the Arcade library in Python.
"""

# Import the arcade library
import arcade

# Define constants for the screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Define constants for scaling the sprites in the game
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5

# Define constants for the player's movement speed
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
ACCELERATION = 1

class MyGame(arcade.Window):
    """
    This is the main application class for our platformer game.
    """

    def __init__(self):
        """
        This is the constructor method which initializes the game window and game variables.
        """

        # Call the parent class's constructor to set up the game window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Initialize the Tile Map object
        self.tile_map = None

        # Initialize the Scene object
        self.scene = None

        # Initialize the player sprite
        self.player_sprite = None

        # Initialize the physics engine
        self.physics_engine = None

        # Initialize the game and GUI cameras
        self.camera = None
        self.gui_camera = None

        # Initialize the state of the keys pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Initialize the score
        self.score = 0

        # Load the sound effects
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        # Set the background color of the game window
        arcade.set_background_color(arcade.csscolor.DARK_GREY)

    def setup(self):
        """
        This method sets up the game. It is used to restart the game.
        """

        # Set up the game and GUI cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Define the name of the map file to load
        map_name = ":resources:tiled_maps/map.json"

        # Define layer specific options in a dictionary
        # This will enable spatial hashing for the platforms layer
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        # Load the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize the Scene with our TileMap
        # This will automatically add all layers from the map as SpriteLists in the scene
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Reset the score
        self.score = 0

        # Set up the player sprite and add it to the scene
        image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        # Set the background color if it is defined in the tile map
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

    def on_draw(self):
        """
        This method renders the screen.
        """

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw the scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw the current score on the screen at the top left corner
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.WHITE,
            18,
        )

    def update_player_vertical_speed(self):
        """
        This method updates the player's speed based on the keys pressed.
        """

        # Update the player's speed based on the keys pressed
        if self.up_pressed:
            self.up_pressed = False
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        else:
            self.player_sprite.change_y = min(self.player_sprite.change_y, 0)
    
    def update_player_horizontal_speed(self):

        if self.left_pressed and not self.right_pressed:
            # Update the player's horizontal speed based on the keys pressed
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED    
        elif self.right_pressed == self.left_pressed:
            # Reset the player's speed
            self.player_sprite.change_x = 0
            

    def on_key_press(self, key, modifiers):
        """
        This method is called whenever a key is pressed.
        It updates the state of the keys and the player's speed.
        """

        # If the UP key is pressed, make the player jump if it can
        if key == arcade.key.UP:
            self.up_pressed = True
            if self.physics_engine.can_jump():
                self.update_player_vertical_speed()
        # If the LEFT key is pressed, make the player move left
        elif key == arcade.key.LEFT:
            self.left_pressed = True
            self.update_player_horizontal_speed()
        # If the RIGHT key is pressed, make the player move right
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
            self.update_player_horizontal_speed()

    def on_key_release(self, key, modifiers):
        """
        This method is called when the user releases a key.
        It updates the state of the keys and the player's speed.
        """

        # If the UP or DOWN key is released, stop the player's vertical movement
        if key == arcade.key.UP:
            self.up_pressed = False
            self.update_player_vertical_speed()

        # If the LEFT or RIGHT key is released, stop the player's horizontal movement
        elif key == arcade.key.LEFT:
            self.left_pressed = False
            self.update_player_horizontal_speed()
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
            self.update_player_horizontal_speed()

    def on_update(self):
        print('hi')

    def center_camera_to_player(self):
        """
        This method centers the camera to the player.
        It calculates the center of the screen based on the player's position and moves the camera to that position.
        """

        # Calculate the center of the screen based on the player's position
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Make sure the camera does not go beyond the left or bottom edge of the screen
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        # Calculate the position to center the player
        player_centered = screen_center_x, screen_center_y

        # Move the camera to the calculated position
        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """
        This method contains the game logic that is updated every frame.
        It moves the player, checks for collisions with coins, and positions the camera.
        """

        # Move the player using the physics engine
        self.physics_engine.update()

        # Check if the player has collided with any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        # For each coin the player has hit, remove the coin, play a sound, and increase the score
        for coin in coin_hit_list:
            # Remove the coin from the sprite lists
            coin.remove_from_sprite_lists()
            # Play the sound of collecting a coin
            arcade.play_sound(self.collect_coin_sound)
            # Increase the score by one
            self.score += 1

        # Position the camera to center the player
        self.center_camera_to_player()


def main():
    """
    This is the main function that creates an instance of the game window, sets up the game, and starts the game loop.
    """

    # Create an instance of the game window
    window = MyGame()
    # Set up the game
    window.setup()
    # Start the game loop
    arcade.run()


# This line checks if this file is the main module and runs the main function if it is
if __name__ == "__main__":
    main()

