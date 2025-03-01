import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1800,1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Volleyball")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
SAND = (238, 214, 175)
SKY_BLUE = (135, 206, 235)

# Game settings
FPS = 60
GRAVITY = 0.4
NET_HEIGHT = 200
NET_WIDTH = 10
PLAYER_SPEED = 7
PLAYER_JUMP = 12
BALL_RADIUS = 50

# Player dimensions
PLAYER_WIDTH = 150
PLAYER_HEIGHT = 150

class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.color = color
        self.vel_y = 0
        self.is_jumping = False
        self.score = 0
        # Controls: left, right, jump
        self.controls = controls
    
    def move(self, keys):
        # Horizontal movement
        if keys[self.controls[0]]:  # Move left
            self.x -= PLAYER_SPEED
        if keys[self.controls[1]]:  # Move right
            self.x += PLAYER_SPEED
        
        # Apply boundaries based on which side of the net the player is on
        if self.color == BLUE:  # Left player
            if self.x < 0:
                self.x = 0
            if self.x > WIDTH // 2 - NET_WIDTH // 2 - self.width:
                self.x = WIDTH // 2 - NET_WIDTH // 2 - self.width
        else:  # Right player
            if self.x < WIDTH // 2 + NET_WIDTH // 2:
                self.x = WIDTH // 2 + NET_WIDTH // 2
            if self.x > WIDTH - self.width:
                self.x = WIDTH - self.width
        
        # Jumping
        if keys[self.controls[2]] and not self.is_jumping:
            self.vel_y = -PLAYER_JUMP
            self.is_jumping = True
        
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Floor collision
        if self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.vel_y = 0
            self.is_jumping = False
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 4
        # Random initial velocity
        angle = random.uniform(math.pi/4, 3*math.pi/4)
        speed = 5
        self.vel_x = speed * math.cos(angle)
        self.vel_y = speed * math.sin(angle)
        # Random direction (left or right)
        if random.choice([True, False]):
            self.vel_x = -self.vel_x
    
    def update(self, player1, player2):
        # Apply gravity
        self.vel_y += GRAVITY * 0.7  # Reduced gravity for ball
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Wall collisions
        if self.x - BALL_RADIUS < 0:
            self.x = BALL_RADIUS
            self.vel_x = -self.vel_x * 0.9  # Bounce with some energy loss
        
        if self.x + BALL_RADIUS > WIDTH:
            self.x = WIDTH - BALL_RADIUS
            self.vel_x = -self.vel_x * 0.9  # Bounce with some energy loss
        
        # Ceiling collision
        if self.y - BALL_RADIUS < 0:
            self.y = BALL_RADIUS
            self.vel_y = -self.vel_y * 0.9  # Bounce with some energy loss
        
        # Floor collision - score point
        if self.y + BALL_RADIUS > HEIGHT:
            if self.x < WIDTH // 2:
                player2.score += 1
            else:
                player1.score += 1
            self.reset()
            return True
        
        # Net collision (top part)
        net_rect = pygame.Rect(WIDTH // 2 - NET_WIDTH // 2, HEIGHT - NET_HEIGHT, NET_WIDTH, NET_HEIGHT)
        ball_rect = pygame.Rect(self.x - BALL_RADIUS, self.y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
        
        if ball_rect.colliderect(net_rect):
            # Detect which side of the net was hit
            if self.x < WIDTH // 2 - NET_WIDTH // 2:  # Hit from left
                self.x = WIDTH // 2 - NET_WIDTH // 2 - BALL_RADIUS
                self.vel_x = -abs(self.vel_x) * 0.9
            elif self.x > WIDTH // 2 + NET_WIDTH // 2:  # Hit from right
                self.x = WIDTH // 2 + NET_WIDTH // 2 + BALL_RADIUS
                self.vel_x = abs(self.vel_x) * 0.9
            else:  # Hit from top
                self.y = HEIGHT - NET_HEIGHT - BALL_RADIUS
                self.vel_y = -abs(self.vel_y) * 0.9
        
        # Player collisions
        p1_rect = pygame.Rect(player1.x, player1.y, player1.width, player1.height)
        p2_rect = pygame.Rect(player2.x, player2.y, player2.width, player2.height)
        
        # Helper function for player collision
        def handle_player_collision(player_rect, player_vel_y):
            # Calculate collision angle based on where the ball hits the player
            relative_x = (self.x - (player_rect.x + player_rect.width / 2)) / (player_rect.width / 2)
            angle = relative_x * (math.pi / 4)  # Maximum 45 degree angle
            speed = math.sqrt(self.vel_x**2 + self.vel_y**2) * 1.1  # Slightly increase speed
            
            # Set new velocity based on collision angle
            self.vel_x = speed * math.sin(angle)
            self.vel_y = -speed * math.cos(angle) - player_vel_y * 0.2  # Add some of player's y velocity
            
            # Ensure the ball goes in the correct direction
            if player_rect.x < WIDTH // 2:  # Left player, ball should go right
                self.vel_x = abs(self.vel_x)
            else:  # Right player, ball should go left
                self.vel_x = -abs(self.vel_x)
        
        if ball_rect.colliderect(p1_rect):
            handle_player_collision(p1_rect, player1.vel_y)
        
        if ball_rect.colliderect(p2_rect):
            handle_player_collision(p2_rect, player2.vel_y)
        
        return False
    
    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BALL_RADIUS)

def main():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 74)
    
    # Create players: (x, y, color, [left_key, right_key, jump_key])
    player1 = Player(
        WIDTH // 4 - PLAYER_WIDTH // 2, 
        HEIGHT - PLAYER_HEIGHT, 
        BLUE, 
        [pygame.K_a, pygame.K_d, pygame.K_w]
    )
    
    player2 = Player(
        3 * WIDTH // 4 - PLAYER_WIDTH // 2, 
        HEIGHT - PLAYER_HEIGHT, 
        RED, 
        [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP]
    )
    
    ball = Ball()
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:  # Reset game
                    player1.score = 0
                    player2.score = 0
                    ball.reset()
        
        keys = pygame.key.get_pressed()
        
        # Move players
        player1.move(keys)
        player2.move(keys)
        
        # Update ball
        point_scored = ball.update(player1, player2)
        
        # Draw everything
        # Sky
        screen.fill(SKY_BLUE)
        # Sand
        pygame.draw.rect(screen, SAND, (0, HEIGHT - 50, WIDTH, 50))
        
        # Net
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - NET_WIDTH // 2, HEIGHT - NET_HEIGHT, NET_WIDTH, NET_HEIGHT))
        
        # Draw players and ball
        player1.draw()
        player2.draw()
        ball.draw()
        
        # Draw scores
        score_text = f"{player1.score}   {player2.score}"
        score_surface = font.render(score_text, True, BLACK)
        screen.blit(score_surface, (WIDTH // 2 - score_surface.get_width() // 2, 20))
        
        # Draw controls info
        info_font = pygame.font.SysFont(None, 24)
        p1_controls = info_font.render("Player 1: A/D/W", True, BLACK)
        p2_controls = info_font.render("Player 2: ←/→/↑", True, BLACK)
        reset_info = info_font.render("Press R to reset | ESC to quit", True, BLACK)
        
        screen.blit(p1_controls, (20, 20))
        screen.blit(p2_controls, (WIDTH - p2_controls.get_width() - 20, 20))
        screen.blit(reset_info, (WIDTH // 2 - reset_info.get_width() // 2, 60))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
