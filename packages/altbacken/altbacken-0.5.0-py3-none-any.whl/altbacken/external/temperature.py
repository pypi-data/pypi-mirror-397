from collections.abc import Iterable, Sequence, Generator
from itertools import count
from math import log


class PredefinedTemperature:
    """
    Represents a predefined sequence of temperature values.

    This class allows storing a predefined series of temperatures and provides
    functionality to iterate over these temperatures in a generator-like fashion.
    It ensures the sequence is not empty upon instantiation.

    Attributes:
        temperature (Sequence[float]): Immutable sequence of predefined
            temperature values.
    """
    def __init__(self, temperature: Iterable[float]):
        self._temperature: Sequence[float] = tuple(temperature)
        if not self._temperature:
            raise ValueError("Temperature sequence must not be empty")

    def __call__(self) -> Generator[float, None, None]:
        yield from self._temperature


class ExponentialCooling:
    """
    Handles exponential cooling calculations.

    This class provides functionality for simulating exponential cooling.
    It calculates decreasing temperature values based on an initial
    temperature and a specified cooling rate. The `ExponentialCooling`
    class can be used in optimization problems such as simulated annealing.

    Attributes:
        initial_temperature (float): The starting temperature for the
            cooling process.
        cooling_rate (float): The rate at which the temperature decreases
            in each step. It must be a value in the range (0, 1).
    """
    def __init__(self, initial_temperature: float, cooling_rate: float = 0.9):
        if initial_temperature <= 0:
            raise ValueError("Initial temperature must be positive")
        if cooling_rate <= 0 or cooling_rate >= 1:
            raise ValueError("Cooling rate must be in (0, 1)")
        self._initial_temperature = initial_temperature
        self._cooling_rate = cooling_rate

    def __call__(self) -> Generator[float, None, None]:
        return (
            self._initial_temperature * (self._cooling_rate ** i) for i in count()
        )


class LogarithmicCooling:
    """
    Implements a logarithmic cooling schedule generator.

    The class provides a cooling schedule based on a logarithmic function. It is
    used commonly in simulated annealing or other optimization algorithms to
    introduce a gradually decreasing parameter (like temperature). The
    logarithmic cooling ensures a steady and slow decrease in the temperature
    value over iterations, making it suitable for problems requiring fine-tuning
    during optimization.

    Attributes:
        initial_temperature (float): The starting temperature value for the cooling
            schedule.
        shift (float): A shift factor added to the logarithm denominator to avoid
            division errors and regulate the cooling rate.
    """
    def __init__(self, initial_temperature: float, shift: float = 1):
        if shift < 1:
            raise ValueError("Shift must be at least 1")
        if initial_temperature <= 0:
            raise ValueError("Initial temperature must be positive")
        self._initial_temperature: float = initial_temperature
        self._shift: float = shift

    def __call__(self) -> Generator[float, None, None]:
        return (
            self._initial_temperature / log(i + self._shift) for i in count(1)
        )


class LinearCooling:
    def __init__(self, initial_temperature: float, step: float):
        if step <= 0:
            raise ValueError("Step must be positive")
        if initial_temperature <= 0:
            raise ValueError("Initial temperature must be positive")
        self._initial_temperature: float = initial_temperature
        self._step: float = step

    def __call__(self) -> Generator[float, None, None]:
        return (
            max(self._initial_temperature - i * self._step, 0) for i in count()
        )