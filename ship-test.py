import pygame
from pygame import Vector2
import sys

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Belter Ship Design Test")
clock = pygame.time.Clock()

# Font for labels
font = pygame.font.Font(None, 24)


# Ship drawing functions
def draw_belter_hauler(screen, pos, angle, color=(150, 150, 100)):
    """
    Boxy mining hauler - asymmetric, industrial, looks jury-rigged
    Think: space forklift with guns welded on
    """
    # Main cargo container (off-center, chunky)
    body = [
        Vector2(-10, -15),
        Vector2(8, -15),
        Vector2(8, 15),
        Vector2(-10, 15),
    ]

    # Mining arm/crane (sticks out the side)
    arm = [
        Vector2(-10, -10),
        Vector2(-18, -10),
        Vector2(-18, 5),
        Vector2(-15, 5),
    ]

    # Thruster block (small, back)
    thruster = [
        Vector2(-5, 15),
        Vector2(5, 15),
        Vector2(5, 20),
        Vector2(-5, 20),
    ]

    # Cockpit window (small viewport)
    cockpit = [
        Vector2(-3, -15),
        Vector2(3, -15),
        Vector2(3, -10),
        Vector2(-3, -10),
    ]

    # Draw all parts
    for shape in [body, arm, thruster]:
        rotated = [
            (pos[0] + point.rotate(-angle).x, pos[1] + point.rotate(-angle).y)
            for point in shape
        ]
        pygame.draw.polygon(screen, color, rotated, 0)
        pygame.draw.polygon(screen, (200, 200, 150), rotated, 1)

    # Cockpit brighter
    rotated_cockpit = [
        (pos[0] + point.rotate(-angle).x, pos[1] + point.rotate(-angle).y)
        for point in cockpit
    ]
    pygame.draw.polygon(screen, (100, 150, 200), rotated_cockpit, 0)


def draw_belter_tug(screen, pos, angle, color=(120, 100, 80)):
    """
    Small utility tug - compact, sturdy, looks repurposed
    """
    # Main hull (short and wide)
    body = [
        Vector2(-12, -8),
        Vector2(12, -8),
        Vector2(12, 12),
        Vector2(-12, 12),
    ]

    # Twin engine pods (small rectangles on sides)
    left_engine = [
        Vector2(-12, 5),
        Vector2(-16, 5),
        Vector2(-16, 12),
        Vector2(-12, 12),
    ]

    right_engine = [
        Vector2(12, 5),
        Vector2(16, 5),
        Vector2(16, 12),
        Vector2(12, 12),
    ]

    # Front "nose" (for direction clarity)
    nose = [
        Vector2(-4, -8),
        Vector2(4, -8),
        Vector2(0, -12),
    ]

    # Draw
    all_shapes = [body, left_engine, right_engine, nose]
    for shape in all_shapes:
        rotated = [
            (pos[0] + point.rotate(-angle).x, pos[1] + point.rotate(-angle).y)
            for point in shape
        ]
        pygame.draw.polygon(screen, color, rotated, 0)
        pygame.draw.polygon(screen, (180, 160, 120), rotated, 1)


def draw_belter_prospector(screen, pos, angle, color=(100, 120, 100)):
    """
    H-shaped mining ship - central cockpit with equipment pods
    Think: space drill rig
    """
    # Central corridor
    spine = [
        Vector2(-3, -15),
        Vector2(3, -15),
        Vector2(3, 15),
        Vector2(-3, 15),
    ]

    # Left equipment pod
    left_pod = [
        Vector2(-12, -10),
        Vector2(-5, -10),
        Vector2(-5, 5),
        Vector2(-12, 5),
    ]

    # Right equipment pod
    right_pod = [
        Vector2(5, -10),
        Vector2(12, -10),
        Vector2(12, 5),
        Vector2(5, 5),
    ]

    # Cockpit (front of spine)
    cockpit = [
        Vector2(-3, -15),
        Vector2(3, -15),
        Vector2(0, -18),
    ]

    # Draw
    for shape in [spine, left_pod, right_pod]:
        rotated = [
            (pos[0] + point.rotate(-angle).x, pos[1] + point.rotate(-angle).y)
            for point in shape
        ]
        pygame.draw.polygon(screen, color, rotated, 0)
        pygame.draw.polygon(screen, (150, 170, 150), rotated, 1)

    # Cockpit window
    rotated_cockpit = [
        (pos[0] + point.rotate(-angle).x, pos[1] + point.rotate(-angle).y)
        for point in cockpit
    ]
    pygame.draw.polygon(screen, (150, 200, 220), rotated_cockpit, 0)


def draw_oba_catamaran(screen, pos, angle, color=(90, 130, 160)):
    """
    Outer Belt Alliance twin-hull catamaran
    Two parallel pontoons connected by a wide base, with engine exhausts
    Based on excalidraw design in clone-protocol.excalidraw
    """
    # Left pontoon (tall, narrow)
    left_hull = [
        Vector2(-15, -20),
        Vector2(-7, -20),
        Vector2(-7, 4),
        Vector2(-15, 4),
    ]

    # Right pontoon (tall, narrow)
    right_hull = [
        Vector2(7, -20),
        Vector2(15, -20),
        Vector2(15, 4),
        Vector2(7, 4),
    ]

    # Connecting base (overlaps bottom of pontoons)
    base = [
        Vector2(-15, 0),
        Vector2(15, 0),
        Vector2(15, 14),
        Vector2(-15, 14),
    ]

    # Left engine nozzle (simplified from freedraw exhaust curves)
    left_engine = [
        Vector2(-12, 14),
        Vector2(-8, 14),
        Vector2(-6, 20),
        Vector2(-14, 20),
    ]

    # Right engine nozzle (simplified from freedraw exhaust curves)
    right_engine = [
        Vector2(8, 14),
        Vector2(12, 14),
        Vector2(14, 20),
        Vector2(6, 20),
    ]

    # Draw hull and base
    for shape in [base, left_hull, right_hull]:
        rotated = [
            (pos[0] + point.rotate(-angle).x, pos[1] + point.rotate(-angle).y)
            for point in shape
        ]
        pygame.draw.polygon(screen, color, rotated, 0)
        pygame.draw.polygon(screen, (140, 180, 210), rotated, 1)

    # Draw engine nozzles with darker glow
    for engine in [left_engine, right_engine]:
        rotated = [
            (pos[0] + point.rotate(-angle).x, pos[1] + point.rotate(-angle).y)
            for point in engine
        ]
        pygame.draw.polygon(screen, (60, 100, 140), rotated, 0)
        pygame.draw.polygon(screen, (140, 180, 210), rotated, 1)


def draw_belter_triangle(screen, pos, angle, color=(120, 110, 90)):
    """
    Keep triangle but make it chunky and asymmetric
    Add visual details that say "mining ship"
    """
    # Main triangle (chunky, not sleek)
    body = [
        Vector2(0, -15),
        Vector2(-10, 12),
        Vector2(10, 12),
    ]

    # Weld marks / reinforcement struts (just lines)
    struts = [
        (Vector2(-5, 0), Vector2(5, 0)),
        (Vector2(0, -8), Vector2(0, 8)),
    ]

    # Asymmetric thruster block (off-center = jury-rigged)
    thruster = [
        Vector2(-6, 12),
        Vector2(4, 12),
        Vector2(4, 16),
        Vector2(-6, 16),
    ]

    # Draw main body
    rotated_body = [
        (pos[0] + point.rotate(-angle).x, pos[1] + point.rotate(-angle).y) for point in body
    ]
    pygame.draw.polygon(screen, color, rotated_body, 0)
    pygame.draw.polygon(screen, (180, 170, 140), rotated_body, 2)

    # Draw struts
    for start, end in struts:
        rot_start = (pos[0] + start.rotate(-angle).x, pos[1] + start.rotate(-angle).y)
        rot_end = (pos[0] + end.rotate(-angle).x, pos[1] + end.rotate(-angle).y)
        pygame.draw.line(screen, (80, 70, 60), rot_start, rot_end, 1)

    # Draw thruster
    rotated_thruster = [
        (pos[0] + point.rotate(-angle).x, pos[1] + point.rotate(-angle).y)
        for point in thruster
    ]
    pygame.draw.polygon(screen, (100, 90, 70), rotated_thruster, 0)


# Main loop
running = True
rotation = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Clear screen
    screen.fill((20, 20, 30))

    # Title
    title = font.render(
        "Belter Ship Designs - Which looks most 'mining ship'?", True, (200, 200, 200)
    )
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Row 1: Static (facing up)
    label_y = 80
    static_y = 150

    # Hauler
    label1 = font.render("1. Hauler (Asymmetric Box)", True, (150, 150, 100))
    screen.blit(label1, (50, label_y))
    draw_belter_hauler(screen, (120, static_y), 0)

    # Tug
    label2 = font.render("2. Tug (Compact)", True, (120, 100, 80))
    screen.blit(label2, (260, label_y))
    draw_belter_tug(screen, (330, static_y), 0)

    # Prospector
    label3 = font.render("3. Prospector (H-Shape)", True, (100, 120, 100))
    screen.blit(label3, (440, label_y))
    draw_belter_prospector(screen, (530, static_y), 0)

    # Triangle
    label4 = font.render("4. Industrial Triangle", True, (120, 110, 90))
    screen.blit(label4, (650, label_y))
    draw_belter_triangle(screen, (730, static_y), 0)

    # OBA Catamaran
    label5 = font.render("5. OBA Catamaran", True, (90, 130, 160))
    screen.blit(label5, (880, label_y))
    draw_oba_catamaran(screen, (960, static_y), 0)

    # Row 2: Rotating (to see profile)
    rotation_label = font.render("Rotating view:", True, (200, 200, 200))
    screen.blit(rotation_label, (20, 280))

    rotating_y = 380
    draw_belter_hauler(screen, (120, rotating_y), rotation)
    draw_belter_tug(screen, (330, rotating_y), rotation)
    draw_belter_prospector(screen, (530, rotating_y), rotation)
    draw_belter_triangle(screen, (730, rotating_y), rotation)
    draw_oba_catamaran(screen, (960, rotating_y), rotation)

    # Row 3: At 45 degrees (diagonal movement view)
    diagonal_label = font.render(
        "45° angle (common view during gameplay):", True, (200, 200, 200)
    )
    screen.blit(diagonal_label, (20, 480))

    diagonal_y = 580
    draw_belter_hauler(screen, (120, diagonal_y), 45)
    draw_belter_tug(screen, (330, diagonal_y), 45)
    draw_belter_prospector(screen, (530, diagonal_y), 45)
    draw_belter_triangle(screen, (730, diagonal_y), 45)
    draw_oba_catamaran(screen, (960, diagonal_y), 45)

    # Instructions
    instruction = font.render("ESC to quit | Rotation auto-animates", True, (150, 150, 150))
    screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT - 30))

    # Update rotation
    rotation += 1
    if rotation >= 360:
        rotation = 0

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
