"""
This is a Platformer Game built using the Arcade library in Python.
"""

# Import the arcade library
import arcade
import os

# Define constants for the screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Define constants for scaling the sprites in the game
CHARACTER_SCALING = 0.25
TILE_SCALING = 0.25
COIN_SCALING = 0.5

# Define constants for the player's movement speed
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 0.7
PLAYER_JUMP_SPEED = 12
ACCELERATION_RATE = 0.1
DECELERATION_RATE = 0.1

MAIN_PATH = os.path.dirname(os.path.abspath(__file__))

def load_texture(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return arcade.load_texture(filename),


class PlayerCharacter(arcade.Sprite):
    
    def __init__(self):

        super().__init__()

        self.jumping = False
        self.jump_state = 1

        self.jump_textures = []
        for i in range(1, 13):
            texture = load_texture(f"{MAIN_PATH}/squish_{i}.png")
            self.jump_textures.append(texture)

        # Set the initial texture
        self.texture = self.jump_textures[0][0]
        self.hit_box = self.texture.hit_box_points

        self.scale = CHARACTER_SCALING

        self.down = False

        self.up_pressed = False

        self.jumping = False

    def update_animation(self, delta_time: float = 1 / 60):
        if self.up_pressed:
            self.jumping = True
        else:
            self.jumping = False
        if self.jump_state == 6:
            self.change_y = PLAYER_JUMP_SPEED
            self.jump_state = 1
        if self.jumping:
            if self.jump_state <= 6 and self.change_y == 0:
                self.jump_state += 1
                self.texture = self.jump_textures[self.jump_state - 1][0]   
                self.hit_box = self.texture.hit_box_points
        elif self.change_y != 0:
            self.down = False
            self.jump_state = 1
            self.texture = self.jump_textures[self.jump_state - 1][0]
            self.hit_box = self.texture.hit_box_points


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
        self.down_pressed = False

        # Initialize the score
        self.score = 0

        self.acceleration = 0

        self.frame = 0

        # Load the sound effects
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)


    def setup(self):
        """
        This method sets up the game. It is used to restart the game.
        """

        # Set up the game and GUI cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Define the name of the map file to load
        map_name = f"{MAIN_PATH}/test_real.tmx"

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
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = 80
        self.player_sprite.center_y = 96
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
    
    def update_player_horizontal_speed(self):

        if self.left_pressed and not self.right_pressed:
            # Update the player's horizontal speed based on the keys pressed
            self.player_sprite.change_x = max(-PLAYER_MOVEMENT_SPEED, min(PLAYER_MOVEMENT_SPEED*self.acceleration, PLAYER_MOVEMENT_SPEED*0.5*(self.acceleration-1)))
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = min(PLAYER_MOVEMENT_SPEED, max(PLAYER_MOVEMENT_SPEED*self.acceleration, PLAYER_MOVEMENT_SPEED*0.5*(self.acceleration+1)))
        elif self.right_pressed == self.left_pressed:
            # Reset the player's speed
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED*self.acceleration
            

    def on_key_press(self, key, modifiers):
        """
        This method is called whenever a key is pressed.
        It updates the state of the keys and the player's speed.
        """

        # If the UP key is pressed, make the player jump if it can
        if key == arcade.key.UP:
            self.player_sprite.up_pressed = True
            self.player_sprite.jump_state = 1
        # If the LEFT key is pressed, make the player move left
        elif key == arcade.key.LEFT:
            self.left_pressed = True

        # If the RIGHT key is pressed, make the player move right
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """
        This method is called when the user releases a key.
        It updates the state of the keys and the player's speed.
        """

        # If the UP key is released, stop the player's vertical movement
        if key == arcade.key.UP:
            self.player_sprite.up_pressed = False
            if self.player_sprite.jump_state != 6 and self.physics_engine.can_jump():
                self.player_sprite.jump_state =  6

        # If the LEFT or RIGHT key is released, stop the player's horizontal movement
        if key == arcade.key.LEFT:
            self.left_pressed = False

        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def center_camera_to_player(self):
        """
        This method centers the camera to the player.
        It calculates the center of the screen based on the player's position and moves the camera to that position.
        """

        # Calculate the center of the screen based on the player's position
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Make sure the camera does not go beyond the left or bottom edge of the screen
        if screen_center_x < 32:
            screen_center_x = 32
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

        # Updates the frame counter
        self.frame += 1

        # Loop will only activate if acceleration is within the accepted parameters
        if self.acceleration >= -1 and self.acceleration <= 1:
            # Left and right acceleration is changed if the correct input is given
            if self.right_pressed and not self.left_pressed:
                self.acceleration = min(self.acceleration + ACCELERATION_RATE, 1)
            elif self.left_pressed and not self.right_pressed:
                self.acceleration = max(self.acceleration - ACCELERATION_RATE, -1)
            # This handles the deceleration if no input is given or if both left and right are pressed
            else:
                if self.acceleration < 0:
                    self.acceleration = min(self.acceleration + DECELERATION_RATE, 0)
                else:
                    self.acceleration = max(self.acceleration - DECELERATION_RATE, 0)

        if self.physics_engine.can_jump():
            self.scene.update_animation(delta_time)

        # Update the player's horizontal speed based on acceleration
        self.update_player_horizontal_speed()

        self.player_sprite.center_x = round(self.player_sprite.center_x)

        # Move the player using the physics engine
        self.physics_engine.update()

        # Check if the player has collided with any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        #if arcade.check_for_collision_with_list(self.player_sprite, self.scene["Platforms"]) != []:
            #self.player_sprite.center_x -= self.player_sprite.center_x % 32

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

        print(self.player_sprite.center_x)

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