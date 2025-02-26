import pytest
from core.room import Room  # Corrected import

# Try to import ParallelGeneticAlgorithm, with fallback
try:
    from optimization.genetic import ParallelGeneticAlgorithm
except ImportError:
    # Define a mock class if the real one is not available
    class ParallelGeneticAlgorithm:
        def __init__(self, population_size=50, mutation_rate=0.3, max_workers=None):
            self.population_size = population_size
            self.mutation_rate = mutation_rate
            self.max_workers = max_workers

@pytest.fixture
def standard_room():
    """标准房间家具"""
    return Room(
        width=12,
        height=10,
        doors=[[5, 0, 2, 1]],
        windows=[[3, 9, 2, 1]]
    )

@pytest.fixture(scope="module")
def genetic_optimizer():
    """遗传算法家具"""
    return ParallelGeneticAlgorithm(
        population_size=50,
        mutation_rate=0.3
    )
