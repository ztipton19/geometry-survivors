"""Shared configuration for the Clone Protocol prototype."""

WIDTH, HEIGHT = 1100, 700
FPS = 120

BG = (0, 0, 0)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_GREEN = (0, 255, 120)
NEON_YELLOW = (255, 255, 0)
NEON_BLUE = (80, 140, 255)
NEON_ORANGE = (255, 150, 0)
WHITE = (240, 240, 240)
RED = (255, 60, 60)


def get_ship_selection_colors() -> dict[str, tuple[int, int, int]]:
    """Return the active ship/UI palette (placeholder until ship selection exists)."""
    return {
        "ship_fill": (140, 120, 0),
        "ship_outline": NEON_YELLOW,
        "ship_tip": NEON_YELLOW,
        "ui_primary": (140, 120, 0),
        "ui_text": (220, 200, 60),
        "xp_bar": NEON_YELLOW,
    }

PLAYER_SPEED = 37.125  # Reduced from 396 for slower movement
PLAYER_RADIUS = 12
PLAYER_MAX_HP = 100

# Ship physics tuning (player only - enemies use simple homing)
ROTATION_SPEED = 150  # deg/sec - lower top spin for control
ROTATION_ACCEL = 300  # deg/sec^2 - smoother turn buildup

THRUST_POWER = 73.125  # Balanced speed increase
STRAFE_POWER = 64.35  # Balanced speed increase
MAX_SPEED = 56.25  # Balanced speed increase
MIN_SPEED = 0  # Can stop completely

FRICTION = 0.98  # Slow natural deceleration
DRIFT_FACTOR = 0.992  # Slightly stronger angular drag for easier stabilization

REVERSE_POWER = 49.5  # Balanced speed increase
THROTTLE_STEP_PER_SEC = 0.9
BOOST_FORCE = 173.25  # Balanced speed increase
BOOST_DURATION = 0.28
BOOST_RECHARGE_TIME = 4.0
HURDLE_IMPULSE = 34.65  # Balanced speed increase
HURDLE_COOLDOWN = 1.8

BULLET_SPEED = 900.0
BULLET_RADIUS = 3
BULLET_DAMAGE = 12
BULLET_LIFETIME = 1.2

ROCKET_SPEED = 520.0
ROCKET_LIFETIME = 2.2
LASER_LIFETIME = 0.12
LASER_WIDTH = 6
EMP_PULSE_LIFETIME = 0.25

FIRE_COOLDOWN_START = 0.14
FIRE_COOLDOWN_MIN = 0.04

ENEMY_BASE_SPEED = 19.40625  # Balanced speed increase
ENEMY_RADIUS = 12
ENEMY_SPAWN_INTERVAL_START = 0.75
ENEMY_SPAWN_INTERVAL_MIN = 0.18
ENEMY_SPAWN_INTERVAL_DECAY = 0.0028
ENEMY_SPEED_PER_SEC = 0.18
ENEMY_SPEED_MAX_BONUS = 15.75
ENEMY_HP_BASE = 22.0
ENEMY_HP_PER_SEC = 0.32
ENEMY_HP_MAX_BONUS = 70.0
ENEMY_DAMAGE_BASE = 22.0
ENEMY_DAMAGE_PER_SEC = 0.025
ENEMY_DAMAGE_MAX_BONUS = 16.0
ENEMY_XP_BASE = 7.0
ENEMY_XP_PER_HP = 0.32

XP_BASE = 90
XP_GROWTH = 1.22
XP_LINEAR_BONUS = 12

ROUND_SECONDS = 15 * 60
