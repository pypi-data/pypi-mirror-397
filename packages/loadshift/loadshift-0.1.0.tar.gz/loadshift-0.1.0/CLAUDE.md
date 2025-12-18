# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Load-shift-optimizer is a demand response optimization system that models flexible energy consumption as a "virtual storage" problem. It uses Mixed Integer Linear Programming (MILP) to optimize when energy should be purchased based on dynamic pricing, while respecting physical constraints like maximum advance/delay times and transfer rates.

## Development Commands

### Environment Setup
```bash
# Install dependencies (uses uv package manager)
uv sync

# Install with Gurobi support (commercial solver, requires license)
uv sync --extra gurobi
```

### Testing
```bash
# Run all tests (includes coverage report by default)
uv run pytest

# Run a single test file
uv run pytest tests/test_virtual_storage.py

# Run a specific test function
uv run pytest tests/test_virtual_storage.py::test_function_name

# Run tests without coverage report
uv run pytest --no-cov

# Run tests with both MIP and Gurobi solvers
# Note: Tests automatically parametrize across available solvers via conftest.py
```

### Linting and Formatting
```bash
# Run ruff linter (auto-fixes enabled in pyproject.toml)
uv run ruff check .

# Format code
uv run ruff format .
```

### Building
```bash
# Build package
uv build
```

## Architecture Overview

### Core Abstraction: Transfer Matrix

The system's key innovation is modeling demand flexibility as a **transfer matrix** T[i,j] where:
- Rows (i) represent when energy is originally demanded
- Columns (j) represent when energy is actually purchased
- T[i,j] represents the amount of energy originally demanded at hour i but purchased at hour j

This abstraction naturally captures temporal flexibility and makes constraints intuitive to express.

### Main Components

#### VirtualStorage (`src/loadshift/virtual_storage.py`)
The core optimization engine. Formulates and solves MILP problems to find optimal demand shifting patterns.

**Key responsibilities:**
- Creates transfer matrix optimization model
- Manages constraints (advance/delay windows, rate limits, purchase limits)
- Supports reserve market participation (upregulation/downregulation)
- Handles spillover between optimization periods

**Important parameters:**
- `max_demand_advance`: How many hours energy purchase can be advanced
- `max_demand_delay`: How many hours energy purchase can be delayed
- `max_rate`: Maximum energy transfer rate per hour (MW or similar units)
- `max_hourly_purchase`: Maximum energy that can be purchased in any single hour
- `enforce_charge_direction`: Whether to enforce mutual exclusivity between charging/discharging (adds binary variables)

#### MovingHorizon (`src/loadshift/moving_horizon.py`)
Orchestrates optimization over multiple rolling time windows.

**Key responsibilities:**
- Creates optimization horizons based on daily decision points
- Coordinates multiple VirtualStorage optimizations
- Propagates spillover effects between consecutive horizons
- Handles daylight saving time transitions

**Important constraint:** Horizons must be ≥24 hours to ensure proper lookahead.

#### SolverAdapters (`src/loadshift/solver_adapters.py`)
Provides unified interface for different MILP solvers using the adapter pattern.

**Supported solvers:**
- `GurobiAdapter`: Commercial Gurobi solver (high performance, requires license)
- `MipAdapter`: Open-source python-mip/CBC solver (free, slower)
- `"auto"`: Auto-detects and falls back (Gurobi → MIP)

#### TimeRanges (`src/loadshift/time_ranges.py`)
Manages dual indexing system for moving-horizon optimization.

**Two coordinate systems:**
- Local time: Relative indices [0, n_lookahead_hours-1] for current optimization
- Global index: Absolute position [0, total_hours-1] including historical data

#### TransferIndices (`src/loadshift/transfer_indices.py`)
Determines which energy transfers T[i,j] are structurally allowed based on timing constraints.

**Enforces:**
- Advance/delay windows (can't move energy too far in time)
- Historical period constraints (can only transfer forward from past)
- No self-transfers (T[i,i] = 0)

### Data Flow

```
Input: price + demand + config
    ↓
moving_horizon()
    ↓
For each horizon:
    ↓
    1. Extract price/demand slice
    2. Create VirtualStorage instance
    3. Build TimeRanges & TransferIndices
    4. Create MILP model with SolverAdapter
    5. Add decision variables (transfer matrix, purchases, deviations)
    6. Add constraints (spillover, control period, charge direction)
    7. Set objective (minimize cost including deviations)
    8. Solve optimization
    9. Extract results & spillover for next horizon
    ↓
Aggregate results → optimized demand timeseries
```

### Key Design Patterns

**No Explicit Storage Level**: The system uses implicit constraints through advance/delay/rate limits rather than modeling explicit state-of-charge. This simplifies the model while achieving equivalent results.

**Spillover Mechanism**: Energy transfers that extend beyond the control period are tracked as "spillover" and constrained in the next optimization window. This maintains temporal consistency across rolling horizons.

**Builder Pattern**: TimeRanges and TransferIndices use builders:
```python
time_ranges = TimeRanges(n_lookback_hours=3)
ranges = time_ranges.build(n_control_hours=5, n_lookahead_hours=9)
```

## Testing Architecture

Tests use automatic parametrization (via `conftest.py`) to run with both MIP and Gurobi solvers. Key test categories:

- **Unit tests**: Individual components (TimeRanges, TransferIndices)
- **Integration tests**: VirtualStorage with various scenarios
- **System tests**: Full moving_horizon workflows including DST transitions

All constraint verification and cost optimization tests use concrete example matrices from docstrings.

## Important Notes

**Python Version**: Requires Python ≥3.12

**Solver Selection**: The package works out-of-the-box with the free MIP solver. For better performance on large problems, install Gurobi (requires license):
```bash
uv sync --extra gurobi
```

**Time Zones**: MovingHorizon uses pandas DatetimeIndex with timezone awareness to correctly handle DST transitions (23-hour and 25-hour days).

**Reserve Markets**: VirtualStorage supports optional `up_price`, `down_price`, and `reference` parameters for modeling participation in upregulation/downregulation markets beyond simple spot market optimization.

**Examples**: See `examples/load_shift_example.ipynb` for usage patterns and visualizations.
