# ARVVI Test Suite

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python tests/test_rvv_parser.py

# Run with coverage
python -m pytest tests/ --cov=arvvi --cov-report=html
```

## Test Structure

- `test_rvv_parser.py` - Tests for RVV instruction pattern matching and parsing
- `sample_test.s` - Sample RISC-V assembly for integration testing
- `expected_results.json` - Expected analysis results for validation

## Creating Test Cases

To add a new test case:

1. Create a RISC-V assembly file in `tests/`
2. Define expected instruction counts in comments
3. Add validation in test script

Example:
```assembly
# Expected: 5 RVV instructions
# - vsetvli: 1
# - vle32: 2
# - vadd: 1
# - vse32: 1

.section .data
vector_add:
    vsetvli zero, a0, e32, m1
    vle32.v v1, (a1)
    vle32.v v2, (a2)
    vadd.vv v3, v1, v2
    vse32.v v3, (a3)
```
