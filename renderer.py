import pygame
from constants import *

def project_3d_to_2d(x, y, z):
    """
    Projects 3D world coordinates (x, y, z) to 2D screen coordinates.
    We assume the camera is looking down the field (along Y axis) or from a side.
    For a simple "Mode 7" style or perspective effect:
    x: horizontal position on field
    y: depth into the screen (distance from camera)
    z: height above ground
    """
    # Simple perspective projection
    # Adjust y to be relative to camera
    # We'll treat screen y as depth for simplicity in this top-down-ish view conversion
    
    # Let's assume standard top-down coordinates where y is "down" the screen.
    # To make it look 3D, we can scale things based on y.
    
    scale = FOV / (FOV + y)
    screen_x = (x - SCREEN_WIDTH / 2) * scale + SCREEN_WIDTH / 2
    screen_y = y * scale * 0.5 + SCREEN_HEIGHT / 4 # Compress Y to look like ground plane
    
    # Adjust for height (z) - things higher up are drawn higher on screen (lower y value)
    screen_y -= z * scale
    
    return int(screen_x), int(screen_y), scale

def draw_field_3d(screen):
    # Draw a trapezoid for the field to simulate depth
    # Top width is smaller than bottom width
    
    # Horizon / Far end
    far_y = 0
    near_y = SCREEN_HEIGHT
    
    # We can use the project function to find corners
    tl_x, tl_y, _ = project_3d_to_2d(0, 0, 0)
    tr_x, tr_y, _ = project_3d_to_2d(SCREEN_WIDTH, 0, 0)
    bl_x, bl_y, _ = project_3d_to_2d(0, SCREEN_HEIGHT, 0)
    br_x, br_y, _ = project_3d_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT, 0)
    
    # Draw grass
    pygame.draw.polygon(screen, GREEN, [(tl_x, tl_y), (tr_x, tr_y), (br_x, br_y), (bl_x, bl_y)])
    
    # Draw outline
    pygame.draw.polygon(screen, WHITE, [(tl_x, tl_y), (tr_x, tr_y), (br_x, br_y), (bl_x, bl_y)], 2)
    
    # Center line (approximate)
    mid_l_x, mid_l_y, _ = project_3d_to_2d(0, SCREEN_HEIGHT/2, 0)
    mid_r_x, mid_r_y, _ = project_3d_to_2d(SCREEN_WIDTH, SCREEN_HEIGHT/2, 0)
    pygame.draw.line(screen, WHITE, (mid_l_x, mid_l_y), (mid_r_x, mid_r_y), 2)
