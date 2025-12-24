import numpy as np

# ==========================================
# Step-0: Base Infrastructure
# ==========================================

class Space:
    """
    Minimal Base Space class.
    """
    def __init__(self, shape=None, dtype=None, seed=None):
        self._shape = shape
        self._dtype = dtype
        self._np_random = None
        if seed is not None:
            self.seed(seed)

    @property
    def np_random(self):
        if self._np_random is None:
            self.seed()
        return self._np_random

    def seed(self, seed=None):
        self._np_random = np.random.default_rng(seed)

    def sample(self):
        raise NotImplementedError

    def contains(self, x):
        raise NotImplementedError

    def __contains__(self, x):
        return self.contains(x)


class Discrete(Space):
    """
    Discrete Space: {0, 1, ..., n-1}
    """
    def __init__(self, n, seed=None):
        super().__init__(shape=(), dtype=np.int64, seed=seed)
        self.n = n

    def sample(self):
        return self.np_random.integers(0, self.n)

    def contains(self, x):
        if isinstance(x, int) or isinstance(x, np.integer):
            return 0 <= x < self.n
        return False

    def __repr__(self):
        return f"Discrete({self.n})"


class Box(Space):
    """
    Box Space: Minimal implementation for continuous intervals.
    """
    def __init__(self, low, high, shape=None, dtype=np.float32, seed=None):
        super().__init__(shape=shape, dtype=dtype, seed=seed)
        self.low = np.array(low, dtype=dtype)
        self.high = np.array(high, dtype=dtype)
        # Verify shape against low/high if needed, skipping for minimal implementation
        if shape is None:
             self._shape = self.low.shape

    def sample(self):
        return self.np_random.uniform(low=self.low, high=self.high, size=self._shape).astype(self._dtype)

    def contains(self, x):
        return x.shape == self._shape and np.all(x >= self.low) and np.all(x <= self.high)

    def __repr__(self):
        return f"Box({self.low}, {self.high}, {self._shape}, {self._dtype})"


class BaseEnv:
    """
    Custom Base Environment (Gym-Independent).
    Mimics Gym's API.
    """
    
    # Metadata for rendering
    metadata = {"render_modes": [], "render_fps": None}

    def __init__(self):
        self.np_random = None
        self.action_space = None
        self.observation_space = None
        # Initialize random state
        self.seed()

    def seed(self, seed=None):
        """
        Sets the seed for this env's random number generator(s).
        """
        self.np_random = np.random.default_rng(seed)
        return [seed]

    def reset(self, seed=None, options=None):
        """
        Resets the environment to an initial state.
        Args:
            seed (int): Seed for the PRNG.
            options (dict): Additional options.
        Returns:
            observation, info
        """
        if seed is not None:
            self.seed(seed)
            
        # If spaces have random states, we might want to seed them too, 
        # but typically env.reset(seed) seeds the env's main RNG.
        
        # Subclasses should implement the logic, but we return None, {} 
        # so super().reset() calls don't crash
        return None, {}

    def step(self, action):
        """
        Run one timestep of the environment's dynamics.
        Args:
            action: An action provided by the agent.
        Returns:
            observation, reward, terminated, truncated, info
        """
        raise NotImplementedError

    def render(self, mode="human"):
        """
        Render the environment.
        """
        raise NotImplementedError

    def close(self):
        """
        Clean up resources.
        """
        pass
        
    def __str__(self):
        return f"<{self.__class__.__name__} instance>"


# ==========================================
# Step-1 extension: FrozenLake Environment
# ==========================================

class FrozenLakeEnv(BaseEnv):
    """
    FrozenLake Environment inheriting from custom BaseEnv.
    """
    
    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, render_mode=None):
        super().__init__()
        
        # 4x4 Grid dimensions
        self.nrow = 4
        self.ncol = 4
        
        # Action space: 0:Left, 1:Down, 2:Right, 3:Up
        self.action_space = Discrete(4)
        
        # Observation space: 0 to 15
        self.observation_space = Discrete(self.nrow * self.ncol)
        
        self.render_mode = render_mode
        
        # Fixed 4x4 map
        self.desc = np.asarray([
            ["S", "F", "F", "F"],
            ["F", "H", "F", "H"],
            ["F", "F", "F", "H"],
            ["H", "F", "F", "G"]
        ], dtype="c")
        
        self.row = 0
        self.col = 0
        
    def reset(self, seed=None, options=None):
        # Call BaseEnv reset to handle seeding
        super().reset(seed=seed)
        
        self.row = 0
        self.col = 0
        
        observation = self._get_observation()
        info = {}
        
        if self.render_mode == "human":
            self.render()
            
        return observation, info

    def step(self, action):
        # Validate action using custom space
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action {action} for {self.action_space}")
            
        new_row, new_col = self.row, self.col
        
        if action == 0: # Left
            new_col = max(self.col - 1, 0)
        elif action == 1: # Down
            new_row = min(self.row + 1, self.nrow - 1)
        elif action == 2: # Right
            new_col = min(self.col + 1, self.ncol - 1)
        elif action == 3: # Up
            new_row = max(self.row - 1, 0)
            
        self.row = new_row
        self.col = new_col
        
        current_tile = self.desc[self.row, self.col].decode("utf-8")
        
        reward = 0.0
        terminated = False
        truncated = False
        
        if current_tile == "G":
            reward = 1.0
            terminated = True
        elif current_tile == "H":
            reward = 0.0
            terminated = True
            
        observation = self._get_observation()
        info = {}
        
        if self.render_mode == "human":
            self.render()
            
        return observation, reward, terminated, truncated, info

    def render(self, mode="human"):
        # We only support human for now or None
        if self.render_mode is None:
            return
            
        print("\n" + "="*10)
        for r in range(self.nrow):
            row_str = ""
            for c in range(self.ncol):
                tile = self.desc[r, c].decode("utf-8")
                if r == self.row and c == self.col:
                    row_str += f"[{tile}]"
                else:
                    row_str += f" {tile} "
            print(row_str)
        print("="*10 + "\n")

    def _get_observation(self):
        return self.row * self.ncol + self.col
