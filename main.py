import pygame
import sys
import pickle
from constants import *
from sprites import Player, BotPlayer, Ball
from renderer import project_3d_to_2d, draw_field_3d
# from network import Network # Commented out for now to avoid crash if server not running

def draw_text(screen, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def main_menu(screen):
    while True:
        screen.fill(BLACK)
        draw_text(screen, "FOOTBALL GAME", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(screen, "1. Local 1v1", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "2. vs Bot", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        draw_text(screen, "3. Online (Experimental)", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return ("LOCAL", None)
                if event.key == pygame.K_2:
                    difficulty = difficulty_menu(screen)
                    return ("BOT", difficulty)
                if event.key == pygame.K_3:
                    return ("ONLINE", None)

def difficulty_menu(screen):
    while True:
        screen.fill(BLACK)
        draw_text(screen, "SELECT DIFFICULTY", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(screen, "1. Easy", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "2. Medium", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        draw_text(screen, "3. Hard", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "EASY"
                if event.key == pygame.K_2:
                    return "MEDIUM"
                if event.key == pygame.K_3:
                    return "HARD"

def online_lobby(screen):
    """Show online lobby and let player choose opponent"""
    from network import Network
    
    # Get player name
    player_name = f"Player{id(screen) % 1000}"
    
    try:
        net = Network(SERVER_IP, PORT)
        # Send player name to server
        net.client.send(pickle.dumps(player_name))
        
        selected_index = 0
        
        while True:
            # Receive lobby list from server
            lobby_data = pickle.loads(net.client.recv(2048))
            
            if lobby_data.get("type") == "lobby_list":
                players = lobby_data.get("players", [])
                
                screen.fill(BLACK)
                draw_text(screen, "ONLINE LOBBY", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
                
                if players:
                    draw_text(screen, "Available Players:", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
                    for i, p in enumerate(players):
                        color = YELLOW if i == selected_index else WHITE
                        draw_text(screen, f"{i+1}. {p}", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + i * 40, color)
                    draw_text(screen, "Use Arrow Keys to Select, Enter to Challenge", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
                else:
                    draw_text(screen, "No players available...", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    draw_text(screen, "Waiting for someone to join...", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
                
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return None
                    if event.type == pygame.KEYDOWN:
                        if players:
                            if event.key == pygame.K_UP:
                                selected_index = (selected_index - 1) % len(players)
                            elif event.key == pygame.K_DOWN:
                                selected_index = (selected_index + 1) % len(players)
                            elif event.key == pygame.K_RETURN:
                                # Challenge selected player
                                target = players[selected_index]
                                net.client.send(pickle.dumps({"type": "challenge", "target": target}))
                                
                                # Wait for match start
                                match_data = pickle.loads(net.client.recv(2048))
                                if match_data.get("type") == "match_start":
                                    return (net, match_data.get("player_num"))
            
            elif lobby_data.get("type") == "match_start":
                # We were challenged
                return (net, lobby_data.get("player_num"))
                
    except Exception as e:
        print(f"Lobby error: {e}")
        return None

def game_loop(screen, mode, difficulty=None):
    clock = pygame.time.Clock()

    # Create sprites
    player1 = Player(100, SCREEN_HEIGHT // 2, RED)
    
    if mode == "BOT":
        player2 = BotPlayer(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2, BLUE, difficulty or "MEDIUM")
    else:
        player2 = Player(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2, BLUE)
        
    ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player1, player2, ball)
    
    # Network setup
    net = None
    if mode == "ONLINE":
        from network import Network
        net = Network(SERVER_IP, PORT)
        # For simplicity in this demo, we'll just control player 1 and receive player 2
        # In a real game, we'd need to know which player we are (P1 or P2)
        # This is a simplified implementation

    # Score
    score1 = 0
    score2 = 0
    
    # Timer (5 minutes = 300 seconds)
    game_duration = 300  # seconds
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        # Calculate elapsed time
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Convert to seconds
        time_remaining = max(0, game_duration - elapsed_time)
        
        # Check if time is up
        if time_remaining == 0:
            running = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Jump / Kick high
                    if ball.z == 0:
                        ball.velocity_z = 10

        # Update
        keys = pygame.key.get_pressed()
        player1.update(keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)
        
        if mode == "LOCAL":
            player2.update(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
        elif mode == "BOT":
            player2.update(ball)
        elif mode == "ONLINE":
            # Send P1 pos, receive P2 pos
            if net:
                p2_pos = net.send((player1.rect.x, player1.rect.y))
                if p2_pos:
                    player2.rect.x, player2.rect.y = p2_pos

        ball.update()

        # Goal Detection
        if ball.rect.right < 0:
            # Goal for Player 2 (Blue)
            if GOAL_Y_TOP < ball.rect.centery < GOAL_Y_BOTTOM:
                score2 += 1
                # Reset
                ball.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                ball.velocity_x = 0
                ball.velocity_y = 0
                player1.rect.center = (100, SCREEN_HEIGHT // 2)
                player2.rect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
            else:
                # Out of bounds, just bounce or reset? 
                # For now, let's just bounce off the "side" walls if not in goal
                # But wait, we already have bounce logic in Ball.update for screen width
                # We need to override that or modify Ball class.
                # Actually Ball class keeps it inside SCREEN_WIDTH. 
                # We need to allow it to go out ONLY if it's in the goal Y range.
                pass

        # Simple collision
        for p in [player1, player2]:
            if pygame.sprite.collide_rect(p, ball):
                # Simple kick logic
                if p.rect.centerx < ball.rect.centerx:
                    ball.velocity_x = 10
                else:
                    ball.velocity_x = -10
                
                if p.rect.centery < ball.rect.centery:
                    ball.velocity_y = 10
                else:
                    ball.velocity_y = -10
        
        # Check for goals (Ball class constrains to screen, so we need to check if it hit the edge)
        # Actually, the Ball class in sprites.py prevents x < 0 or x > SCREEN_WIDTH.
        # We should modify Ball class to allow going out if it's a goal, OR check here.
        # Let's modify the check here to be based on the ball being AT the edge.
        
        if ball.rect.left <= 0:
            if GOAL_Y_TOP < ball.rect.centery < GOAL_Y_BOTTOM:
                 score2 += 1
                 ball.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                 ball.velocity_x = 0
                 ball.velocity_y = 0
                 player1.rect.center = (100, SCREEN_HEIGHT // 2)
                 player2.rect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
        
        if ball.rect.right >= SCREEN_WIDTH:
            if GOAL_Y_TOP < ball.rect.centery < GOAL_Y_BOTTOM:
                 score1 += 1
                 ball.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                 ball.velocity_x = 0
                 ball.velocity_y = 0
                 player1.rect.center = (100, SCREEN_HEIGHT // 2)
                 player2.rect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)

        # Draw
        screen.fill(BLACK) # Clear screen
        
        # Draw 3D Field
        draw_field_3d(screen)
        
        # Draw Score
        draw_text(screen, f"{score1} - {score2}", 48, SCREEN_WIDTH // 2, 50)
        
        # Draw Timer
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        timer_text = f"{minutes}:{seconds:02d}"
        draw_text(screen, timer_text, 32, SCREEN_WIDTH // 2, 100, YELLOW)
        
        # Draw Sprites in 3D
        # Sort by Y position for depth buffering (painters algorithm)
        sprites_list = sorted(all_sprites, key=lambda s: s.rect.centery)
        
        for sprite in sprites_list:
            # Project position
            z = 0
            if hasattr(sprite, 'z'):
                z = sprite.z
            
            sx, sy, scale = project_3d_to_2d(sprite.rect.centerx, sprite.rect.centery, z)
            
            # Scale sprite
            w = int(sprite.rect.width * scale)
            h = int(sprite.rect.height * scale)
            
            if w > 0 and h > 0:
                scaled_image = pygame.transform.scale(sprite.image, (w, h))
                screen.blit(scaled_image, (sx - w//2, sy - h//2))
                
                # Draw shadow
                shadow_sx, shadow_sy, _ = project_3d_to_2d(sprite.rect.centerx, sprite.rect.centery, 0)
                pygame.draw.ellipse(screen, (0, 0, 0, 100), (shadow_sx - w//2, shadow_sy - h//4, w, h//2))

        pygame.display.flip()
        clock.tick(FPS)
    
    # Game Over Screen
    game_over_start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - game_over_start < 5000:  # Show for 5 seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        screen.fill(BLACK)
        draw_text(screen, "FULL TIME!", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text(screen, f"Final Score: {score1} - {score2}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
        
        if score1 > score2:
            winner = "Red Wins!"
        elif score2 > score1:
            winner = "Blue Wins!"
        else:
            winner = "Draw!"
        draw_text(screen, winner, 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, YELLOW)
        
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].upper()
        difficulty = sys.argv[2].upper() if len(sys.argv) > 2 else "MEDIUM"
    else:
        mode, difficulty = main_menu(screen)
    
    # Handle online mode differently
    if mode == "ONLINE":
        lobby_result = online_lobby(screen)
        if lobby_result:
            net, player_num = lobby_result
            # Start online game (simplified for now)
            draw_text(screen, f"Match starting! You are Player {player_num}", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            pygame.display.flip()
            pygame.time.wait(2000)
    else:
        game_loop(screen, mode, difficulty)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
