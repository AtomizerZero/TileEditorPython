import os
import csv
import pygame as pg
import tkinter as tk
from tkinter import filedialog

# Constants
TILE_SIZE = 48  # Default size of tile on screen (actual tile size doesnt matter)
GRID_WIDTH = 10  # Default width for new maps
GRID_HEIGHT = 10  # Default height for new maps
PALETTE_HEIGHT = 2
# Constants for map size limits
MIN_GRID_SIZE = 3
MAX_GRID_WIDTH = 20
MAX_GRID_HEIGHT = 15

# Window dimensions
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
DARK_GRAY = (50, 50, 50)
SEMI_TRANSPARENT = (0, 0, 0, 128) 

'''
This dictionary maps tile IDs to their names.
You can add more tiles as needed.
0: "empty" is a special tile that represents no tile. 
    When you right click on a tile, it will be set to this ID.

Tiles are loaded from the "assets" directory as PNG images.    
'''
TILE_TYPES = {
    0: "empty",
    1: "grass",
    2: "water",
    3: "dirt"
}

class TileEditor:
    def __init__(self):
        pg.init()
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        
        # Fixed window size
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.screen = pg.display.set_mode((self.window_width, self.window_height))
        pg.display.set_caption("Tile Editor")
        
        # Camera/viewport variables
        self.camera_x = 0
        self.camera_y = 0
        self.zoom_level = 1.0
        self.viewport_width = self.window_width
        self.viewport_height = self.grid_height * TILE_SIZE * 2
        
        self.clock = pg.time.Clock()
        
        # Load tiles
        self.tiles = {}
        self.load_tiles()
        
        # Initialize map
        self.map_data = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Current selected tile
        self.current_tile = 1
        
        # Status message
        self.status_message = "Welcome to Tile Editor"
        self.status_timer = 0
        
        # Initialize tkinter for file dialogs but hide the main window
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()  # Hide the main tkinter window
        
        # Try to load existing map
        self.map_path = os.path.join("assets", "map.csv")
        self.try_load_map()
    
    def load_tiles(self):
        # Load tile images
        for tile_id, tile_name in TILE_TYPES.items():
            if tile_id == 0:  # Skip empty tile
                self.tiles[0] = None
                continue
                
            try:
                # Construct path to tile image
                tile_path = os.path.join("assets", f"{tile_name}.png")
                # Load image and scale it to TILE_SIZE
                tile_img = pg.image.load(tile_path).convert_alpha()
                tile_img = pg.transform.scale(tile_img, (TILE_SIZE, TILE_SIZE))
                self.tiles[tile_id] = tile_img
            except Exception:
                # Create a placeholder colored square
                tile_surface = pg.Surface((TILE_SIZE, TILE_SIZE))
                tile_surface.fill(self.get_color_for_tile(tile_id))
                self.tiles[tile_id] = tile_surface
    
    def get_color_for_tile(self, tile_id):
        # Generate a color based on tile_id for placeholder
        colors = {
            1: (0, 255, 0),    # Green for grass
            2: (0, 0, 255),    # Blue for water
            3: (139, 69, 19),  # Brown for dirt
            4: (128, 128, 128)  # Gray for stone
        }
        return colors.get(tile_id, (255, 0, 255))  # Default to magenta
    
    def try_load_map(self):
        try:
            self.load_map()
            self.set_status("Map loaded successfully")
        except Exception as e:
            self.set_status(f"Could not load map: {str(e)}")
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.map_path), exist_ok=True)
    
    def load_map(self):
        with open(self.map_path, 'r', newline='') as file:
            # First pass: determine map dimensions
            reader = csv.reader(file)
            rows = list(reader)  # Convert to list to read it twice
            
            if not rows:
                self.set_status("Empty map file, using default size")
                return
                
            # Determine map dimensions from the file
            map_height = len(rows)
            map_width = max(len(row) for row in rows)
            
            # Ensure minimum dimensions
            map_width = max(MIN_GRID_SIZE, map_width)
            map_height = max(MIN_GRID_SIZE, map_height)
            
            # Resize map if needed
            if map_width != self.grid_width or map_height != self.grid_height:
                self.resize_map(map_width, map_height)
                self.set_status(f"Map size detected: {map_width}x{map_height}")
            
            # Second pass: load the data
            for y, row in enumerate(rows):
                if y >= self.grid_height:
                    break
                for x, cell in enumerate(row):
                    if x >= self.grid_width:
                        break
                    try:
                        self.map_data[y][x] = int(cell)
                    except ValueError:
                        self.map_data[y][x] = 0
    
    def save_map(self):
        try:
            os.makedirs(os.path.dirname(self.map_path), exist_ok=True)
            with open(self.map_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(self.map_data)
            self.set_status(f"Map saved to {self.map_path}")
        except Exception as e:
            self.set_status(f"Error saving map: {str(e)}")
    
    def set_status(self, message, duration=3000):
        self.status_message = message
        self.status_timer = duration
    
    def resize_map(self, new_width, new_height):
        # Ensure dimensions are within limits
        new_width = max(MIN_GRID_SIZE, min(new_width, MAX_GRID_WIDTH))
        new_height = max(MIN_GRID_SIZE, min(new_height, MAX_GRID_HEIGHT))
        
        # If no change, return early
        if new_width == self.grid_width and new_height == self.grid_height:
            return
        
        # Create new map data with new dimensions
        new_map_data = [[0 for _ in range(new_width)] for _ in range(new_height)]
        
        # Copy existing data that fits in the new dimensions
        for y in range(min(self.grid_height, new_height)):
            for x in range(min(self.grid_width, new_width)):
                new_map_data[y][x] = self.map_data[y][x]
        
        # Update dimensions and map data
        self.grid_width = new_width
        self.grid_height = new_height
        self.map_data = new_map_data
        
        # Update status
        self.set_status(f"Map resized to {new_width}x{new_height}")
    
    def update_window_size(self):
        self.window_width = TILE_SIZE * self.grid_width * 2
        self.window_height = TILE_SIZE * (self.grid_height + PALETTE_HEIGHT) * 2
    
    def draw_grid(self):
        # Draw background
        self.screen.fill(BLACK)
        
        # Calculate the visible tiles based on zoom and camera position
        tile_size_zoomed = int(TILE_SIZE * self.zoom_level)
        visible_width = self.viewport_width // tile_size_zoomed + 1
        visible_height = self.viewport_height // tile_size_zoomed + 1
        
        # Calculate the range of tiles to draw
        start_x = self.camera_x
        start_y = self.camera_y
        end_x = min(start_x + visible_width, self.grid_width)
        end_y = min(start_y + visible_height, self.grid_height)
        
        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Calculate screen position
                screen_x = int((x - self.camera_x) * tile_size_zoomed)
                screen_y = int((y - self.camera_y) * tile_size_zoomed)
                
                tile_id = self.map_data[y][x]
                if tile_id != 0 and tile_id in self.tiles:
                    # Scale the tile to the current zoom level
                    scaled_tile = pg.transform.scale(
                        self.tiles[tile_id], 
                        (tile_size_zoomed, tile_size_zoomed)
                    )
                    self.screen.blit(scaled_tile, (screen_x, screen_y))
                else:
                    # Draw empty tile
                    pg.draw.rect(self.screen, LIGHT_GRAY, 
                               (screen_x, screen_y, tile_size_zoomed, tile_size_zoomed), 1)
        
        # Draw grid lines
        for x in range(start_x, end_x + 1):
            screen_x = int((x - self.camera_x) * tile_size_zoomed)
            pg.draw.line(self.screen, GRAY, 
                        (screen_x, 0), 
                        (screen_x, min(self.viewport_height, (end_y - start_y) * tile_size_zoomed)))
                        
        for y in range(start_y, end_y + 1):
            screen_y = int((y - self.camera_y) * tile_size_zoomed)
            pg.draw.line(self.screen, GRAY, 
                        (0, screen_y), 
                        (min(self.viewport_width, (end_x - start_x) * tile_size_zoomed), screen_y))
            
    def draw_ui(self):
        # Draw status bar
        status_y = self.window_height - 25
        pg.draw.rect(self.screen, BLACK, (0, status_y, self.window_width, 25))
        
        # Draw status message
        if self.status_timer > 0:
            font = pg.font.SysFont(None, 20)
            text = font.render(self.status_message, True, WHITE)
            self.screen.blit(text, (10, status_y + 5))
        
        # Draw map dimensions
        dimensions_text = f"Map Size: {self.grid_width}x{self.grid_height}"
        font = pg.font.SysFont(None, 20)
        dim_text = font.render(dimensions_text, True, WHITE)
        self.screen.blit(dim_text, (10, status_y - 25))
        
        # Draw help panel
        help_panel_height = 100  # Height of help panel
        help_y = status_y - help_panel_height
        
        # Draw panel background
        pg.draw.rect(self.screen, DARK_GRAY, (0, help_y, self.window_width, help_panel_height))
        pg.draw.rect(self.screen, WHITE, (0, help_y, self.window_width, help_panel_height), 1)  # Border
        
        # Draw help title
        title_font = pg.font.SysFont(None, 24, bold=True)
        title = title_font.render("CONTROLS:", True, WHITE)
        self.screen.blit(title, (10, help_y + 5))
        
        # Draw help text in multiple lines with larger font
        help_font = pg.font.SysFont(None, 22)
        help_lines = [
            "Mouse: Left click = place tile | Right click = remove tile | Wheel = zoom",
            "Map: CTRL+Arrows = resize map | Arrows = scroll map | +/- = zoom in/out",
            "Files: S = save map | L = load map | CTRL+O = open map | CTRL+N = new map | ESC = quit"
        ]
        
        line_y = help_y + 25
        for line in help_lines:
            help_text = help_font.render(line, True, WHITE)
            self.screen.blit(help_text, (20, line_y))
            line_y += 20
        
        # Draw palette on the right side
        self.draw_palette()
    
    def draw_palette(self):
        """Draw the tile palette on the right side of the screen in a grid layout"""
        # Palette area dimensions
        palette_width = TILE_SIZE * 3  # Width for tiles and labels
        palette_x = self.window_width - palette_width
        palette_height = self.window_height - 25  # Leave space for status bar
        
        # Draw palette background
        pg.draw.rect(self.screen, LIGHT_GRAY, (palette_x, 0, palette_width, palette_height))
        pg.draw.line(self.screen, WHITE, (palette_x, 0), (palette_x, palette_height), 2)
        
        # Draw palette title
        title_font = pg.font.SysFont(None, 24, bold=True)
        title = title_font.render("TILES", True, BLACK)
        title_width = title.get_width()
        self.screen.blit(title, (palette_x + (palette_width - title_width) // 2, 10))
        
        # Calculate grid layout - 2 columns
        tiles_per_row = 2
        row_height = TILE_SIZE + 25  # Tile height + space for label
        tile_spacing = 1  # 1px gap between tiles
        
        # Start position for the first tile
        start_y = 40  # Below the title
        
        # Organize tiles in a grid
        row, col = 0, 0
        for tile_id, tile_name in TILE_TYPES.items():
            if tile_id == 0:  # Skip empty tile
                continue
                
            if tile_id in self.tiles and self.tiles[tile_id] is not None:
                # Calculate position in the grid
                x = palette_x + col * (TILE_SIZE + tile_spacing) + 10
                y = start_y + row * row_height
                
                # Draw tile
                self.screen.blit(self.tiles[tile_id], (x, y))
                
                # Draw selection indicator
                if tile_id == self.current_tile:
                    pg.draw.rect(self.screen, RED, (x, y, TILE_SIZE, TILE_SIZE), 2)
                
                # Draw tile name below the tile
                font = pg.font.SysFont(None, 18)
                text = font.render(f"{tile_id}: {tile_name}", True, BLACK)
                text_width = text.get_width()
                # Center text under the tile
                self.screen.blit(text, (x + (TILE_SIZE - text_width) // 2, y + TILE_SIZE + 5))
                
                # Update grid position for next tile
                col += 1
                if col >= tiles_per_row:
                    col = 0
                    row += 1
    
    def handle_mouse_click(self, pos, button):
        x, y = pos
        
        # Check if click is in the palette area (right side)
        palette_width = TILE_SIZE * 3
        palette_x = self.window_width - palette_width
        
        if x >= palette_x:
            # Click is in the palette area
            # Calculate grid position
            tiles_per_row = 2
            row_height = TILE_SIZE + 25
            tile_spacing = 1
            start_y = 40
            
            # Adjust x and y relative to palette start
            rel_x = x - palette_x - 10
            rel_y = y - start_y
            
            # Calculate grid cell
            col = rel_x // (TILE_SIZE + tile_spacing)
            row = rel_y // row_height
            
            # Validate click is on a tile
            if 0 <= col < tiles_per_row and 0 <= rel_y % row_height < TILE_SIZE:
                # Calculate tile ID from position
                index = row * tiles_per_row + col
                # Skip the empty tile (0)
                tile_id = index + 1
                
                if tile_id in TILE_TYPES:
                    self.current_tile = tile_id
                    self.set_status(f"Selected tile: {TILE_TYPES[tile_id]}")
            
            return
            
        # Check if click is in the map area
        if y < self.viewport_height:
            # Convert screen coordinates to grid coordinates considering zoom and camera
            tile_size_zoomed = int(TILE_SIZE * self.zoom_level)
            grid_x = int(x / tile_size_zoomed) + self.camera_x
            grid_y = int(y / tile_size_zoomed) + self.camera_y
            
            if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                if button == 1:  # Left click
                    self.map_data[grid_y][grid_x] = self.current_tile
                elif button == 3:  # Right click
                    self.map_data[grid_y][grid_x] = 0  # Clear tile
    
    def create_new_map(self):
        """Create a new map with a user-defined name"""
        # Get map name from user
        map_name = self.show_text_input_dialog("Enter map name (without extension):")
        
        if not map_name:  # User cancelled
            return
            
        # Sanitize filename (replace spaces with underscores, remove invalid chars)
        map_name = ''.join(c for c in map_name if c.isalnum() or c in ' _-')
        map_name = map_name.replace(' ', '_')
        
        if not map_name:  # Name is empty after sanitization
            self.set_status("Invalid map name")
            return
            
        # Set the new map path
        self.map_path = os.path.join("assets", f"{map_name}.csv")
        
        # Reset the map to default size with empty tiles
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        self.map_data = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Reset camera position and update status
        self.camera_x = 0
        self.camera_y = 0
        self.set_status(f"Created new map: {map_name}")
    
    def show_text_input_dialog(self, prompt):
        """Show a text input dialog and return the entered text"""
        input_text = ""
        dialog_active = True
        
        # Create a semi-transparent surface for the dialog background
        dialog_surface = pg.Surface((self.window_width, self.window_height), pg.SRCALPHA)
        dialog_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Dialog box dimensions
        dialog_width = 400
        dialog_height = 150
        dialog_x = (self.window_width - dialog_width) // 2
        dialog_y = (self.window_height - dialog_height) // 2
        
        # Text input cursor properties
        cursor_visible = True
        cursor_timer = 0
        cursor_blink_time = 500  # milliseconds
        
        # Store the previous display state
        previous_screen = self.screen.copy()
        
        while dialog_active:
            # Handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return None
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        dialog_active = False
                    elif event.key == pg.K_ESCAPE:
                        input_text = ""
                        dialog_active = False
                    elif event.key == pg.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        # Only add printable characters
                        if event.unicode.isprintable():
                            input_text += event.unicode
            
            # Blink cursor
            cursor_timer += self.clock.get_time()
            if cursor_timer >= cursor_blink_time:
                cursor_visible = not cursor_visible
                cursor_timer = 0
            
            # Draw dialog
            self.screen.blit(previous_screen, (0, 0))
            self.screen.blit(dialog_surface, (0, 0))
            
            # Draw dialog box
            pg.draw.rect(self.screen, DARK_GRAY, (dialog_x, dialog_y, dialog_width, dialog_height))
            pg.draw.rect(self.screen, WHITE, (dialog_x, dialog_y, dialog_width, dialog_height), 2)
            
            # Draw prompt
            prompt_font = pg.font.SysFont(None, 24)
            prompt_text = prompt_font.render(prompt, True, WHITE)
            self.screen.blit(prompt_text, (dialog_x + 20, dialog_y + 20))
            
            # Draw input text with cursor
            input_font = pg.font.SysFont(None, 28)
            display_text = input_text
            if cursor_visible:
                display_text += "|"
            text_surface = input_font.render(display_text, True, WHITE)
            
            # Draw text box
            text_box_rect = (dialog_x + 20, dialog_y + 60, dialog_width - 40, 30)
            pg.draw.rect(self.screen, BLACK, text_box_rect)
            pg.draw.rect(self.screen, WHITE, text_box_rect, 1)
            self.screen.blit(text_surface, (text_box_rect[0] + 5, text_box_rect[1] + 5))
            
            # Draw OK/Cancel buttons
            ok_button_rect = (dialog_x + dialog_width - 150, dialog_y + dialog_height - 40, 60, 25)
            cancel_button_rect = (dialog_x + dialog_width - 80, dialog_y + dialog_height - 40, 60, 25)
            
            pg.draw.rect(self.screen, GRAY, ok_button_rect)
            pg.draw.rect(self.screen, GRAY, cancel_button_rect)
            
            button_font = pg.font.SysFont(None, 20)
            ok_text = button_font.render("OK", True, WHITE)
            cancel_text = button_font.render("Cancel", True, WHITE)
            
            # Center text on buttons
            self.screen.blit(ok_text, (ok_button_rect[0] + (ok_button_rect[2] - ok_text.get_width()) // 2,
                                       ok_button_rect[1] + (ok_button_rect[3] - ok_text.get_height()) // 2))
            self.screen.blit(cancel_text, (cancel_button_rect[0] + (cancel_button_rect[2] - cancel_text.get_width()) // 2,
                                           cancel_button_rect[1] + (cancel_button_rect[3] - cancel_text.get_height()) // 2))
            
            pg.display.flip()
            self.clock.tick(30)
        
        return input_text
    
    def open_map_file(self):
        """Open a map file using a file dialog"""
        # Use tkinter's file dialog to get the file path
        file_path = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.map_path),
            title="Open Map File",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        
        # If user canceled the dialog, return without doing anything
        if not file_path:
            return
        
        # Update the map path and try to load the map
        self.map_path = file_path
        try:
            self.load_map()
            self.set_status(f"Opened map: {os.path.basename(file_path)}")
        except Exception as e:
            self.set_status(f"Error loading map: {str(e)}")
    
    def handle_key_event(self, key, mods):
        # Handle tile selection with number keys
        if pg.K_0 <= key <= pg.K_9:
            tile_id = key - pg.K_0
            if tile_id in TILE_TYPES:
                self.current_tile = tile_id
                self.set_status(f"Selected tile: {TILE_TYPES[tile_id]}")
        
        # Save, load, and new map
        elif key == pg.K_s and not (mods & pg.KMOD_CTRL):
            self.save_map()
        elif key == pg.K_l and not (mods & pg.KMOD_CTRL):
            self.try_load_map()
        elif key == pg.K_n and (mods & pg.KMOD_CTRL):
            self.create_new_map()
        elif key == pg.K_o and (mods & pg.KMOD_CTRL):
            self.open_map_file()
            
        # Map resizing controls
        elif key == pg.K_RIGHT and (mods & pg.KMOD_CTRL):
            self.resize_map(self.grid_width + 1, self.grid_height)
        elif key == pg.K_LEFT and (mods & pg.KMOD_CTRL):
            self.resize_map(self.grid_width - 1, self.grid_height)
        elif key == pg.K_DOWN and (mods & pg.KMOD_CTRL):
            self.resize_map(self.grid_width, self.grid_height + 1)
        elif key == pg.K_UP and (mods & pg.KMOD_CTRL):
            self.resize_map(self.grid_width, self.grid_height - 1)
        
        # Zoom controls
        elif key == pg.K_PLUS or key == pg.K_EQUALS:
            self.zoom_in()
        elif key == pg.K_MINUS:
            self.zoom_out()        
            
        # Scroll controls (without modifier keys)
        elif key == pg.K_RIGHT and not mods:
            self.scroll(1, 0)
        elif key == pg.K_LEFT and not mods:
            self.scroll(-1, 0)
        elif key == pg.K_DOWN and not mods:
            self.scroll(0, 1)
        elif key == pg.K_UP and not mods:
            self.scroll(0, -1)
    
    def zoom_in(self):
        if self.zoom_level < 2.0:  # Limit max zoom
            self.zoom_level += 0.1
            self.set_status(f"Zoom level: {self.zoom_level:.1f}x")
    
    def zoom_out(self):
        if self.zoom_level > 0.5:  # Limit min zoom
            self.zoom_level -= 0.1
            self.set_status(f"Zoom level: {self.zoom_level:.1f}x")
    
    def scroll(self, dx, dy):
        # Adjust scroll speed based on zoom level
        scroll_speed = max(1, int(3 / self.zoom_level))
        dx *= scroll_speed
        dy *= scroll_speed
        
        # Update camera position
        self.camera_x += dx
        self.camera_y += dy
        
        # Ensure camera doesn't go out of bounds
        max_x = max(0, self.grid_width - int(self.viewport_width / (TILE_SIZE * self.zoom_level)))
        max_y = max(0, self.grid_height - int(self.viewport_height / (TILE_SIZE * self.zoom_level)))
        
        # Always allow scrolling if the map is bigger than the viewport
        self.camera_x = max(0, min(self.camera_x, max(0, self.grid_width - 1)))
        self.camera_y = max(0, min(self.camera_y, max(0, self.grid_height - 1)))
        
        # Update status for debugging
        self.set_status(f"Camera: ({self.camera_x}, {self.camera_y}) Zoom: {self.zoom_level:.1f}x", 1000)
    
    def run(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # Handle mouse wheel for zooming
                    if event.button == 4:  # Scroll up
                        self.zoom_in()
                    elif event.button == 5:  # Scroll down
                        self.zoom_out()
                    else:
                        self.handle_mouse_click(event.pos, event.button)
                elif event.type == pg.KEYDOWN:
                    self.handle_key_event(event.key, pg.key.get_mods())
                
            # Check held keys for smooth scrolling
            keys = pg.key.get_pressed()
            if keys[pg.K_ESCAPE]:
                running = False
            if keys[pg.K_RIGHT] and not (pg.key.get_mods() & pg.KMOD_CTRL):                self.scroll(1, 0)
            if keys[pg.K_LEFT] and not (pg.key.get_mods() & pg.KMOD_CTRL):
                self.scroll(-1, 0)
            if keys[pg.K_DOWN] and not (pg.key.get_mods() & pg.KMOD_CTRL):
                self.scroll(0, 1)
            if keys[pg.K_UP] and not (pg.key.get_mods() & pg.KMOD_CTRL):
                self.scroll(0, -1)
            
            # Update status timer
            if self.status_timer > 0:
                self.status_timer -= self.clock.get_time()
            
            # Draw everything
            self.draw_grid()
            self.draw_ui()
            
            pg.display.flip()
            self.clock.tick(60)
        
        pg.quit()

if __name__ == "__main__":
    editor = TileEditor()
    editor.run()