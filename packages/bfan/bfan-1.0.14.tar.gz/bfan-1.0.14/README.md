# BFAN - Binary Functional Automated Testing Framework

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Test Structure](#test-structure)
- [Configuration](#configuration)
- [Actions Reference](#actions-reference)
- [Filters](#filters)
- [Environment Variables](#environment-variables)
- [Advanced Features](#advanced-features)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

BFAN (Binary Functional Automated Testing) is a comprehensive Python-based testing framework designed for executing, validating, and managing functional tests for binary executables. It provides a YAML-based test definition system with support for:

- Multi-step test execution
- Background process management
- Output comparison with reference files
- Flexible filtering system
- Test tagging and conditional execution
- Environment variable management
- Parallel test execution
- JUnit XML report generation
- Multiple output formats (compact, summary, JSON)

**Version:** 1.0.14

---

## Installation

### Requirements
- Python 3.6+
- Required Python packages:
  - pyyaml
  - docopt
  - psutil
  - mako

### Install from PyPI
```bash
pip install bfan
```

### Install from source
```bash
cd bfan
pip install --upgrade build
python -m build
pip install dist/bfan-*.whl
```

---

## Quick Start

### 1. Create a Test Directory Structure

```
mytest.btest/
├── def.yaml              # Test definition file
├── source/               # Source files to be copied to result directory
│   └── test.py
└── reference/            # Reference output files for comparison
    └── transcript.step1
```

### 2. Create a Test Definition (def.yaml)

```yaml
tags: regression,smoke
steps:
  - step1:
      - run: python test.py
      - diff: result/transcript.step1 reference/transcript.step1
```

### 3. Run the Test

```bash
bfan run mytest.btest
```

---

## Command Reference

### Run Tests
```bash
bfan run [OPTIONS] [<path>...]
```

**Options:**
- `--image=<path or name>` - Specify container/image path
- `--view=(compact|summary|jsonSummary)` - Output format
  - `compact` - Detailed per-test output (default for single test)
  - `summary` - Aggregated summary (default for multiple tests)
  - `jsonSummary` - JSON formatted output for CI integration
- `--env=<env1=val1,env2=val2>` - Set environment variables
- `--clearPassed` - Remove result directories of passed tests
- `--stdout` - Echo test output to stdout
- `--genXml` - Generate JUnit XML report
- `--outputName=<name>` - Custom name for XML report (default: "report")
- `--arch=<binArch>` - Specify binary architecture
- `--tags=<equation>` - Filter tests by tag expression
- `--step=<stepName1,stepName2>` - Run only specific steps in the test
- `--noclean` - Skip cleaning the result directory before running tests
- `<path>...` - Paths to test directories or test list files

**Examples:**
```bash
# Run all tests in current directory
bfan run

# Run specific test
bfan run tests/mytest.btest

# Run with architecture and environment
bfan run --arch=x86_64 --env=DEBUG=1,TIMEOUT=300

# Run tests matching tag expression
bfan run --tags="(regression or smoke) and not slow"

# Generate XML report
bfan run --genXml --outputName=test_results tests/

# Run only specific steps
bfan run --step step1,step2 tests/mytest.btest

# Skip cleaning the result directory (useful for debugging)
bfan run --noclean tests/mytest.btest
```

### Clean Test Results
```bash
bfan clean [<path>...]
```

Removes `result/` directories from test cases.

**Example:**
```bash
bfan clean tests/
```

### Show Differences
```bash
bfan diff [<path>...]
```

Displays differences between result and reference files without running tests.

**Example:**
```bash
bfan diff tests/mytest.btest
```

### Update Reference Files
```bash
bfan update [<path>...]
```

Copies result files to reference directory, updating expected outputs.

**Example:**
```bash
bfan update tests/mytest.btest
```

---

## Test Structure

### Directory Layout

```
testname.btest/
├── def.yaml              # Test definition (required)
├── source/               # Files copied to result/ before test (optional)
│   ├── input.txt
│   └── config.json
├── reference/            # Reference files for comparison
│   ├── transcript.step1
│   └── output.txt
├── filters/              # Test-specific filters (optional)
│   └── custom_filter.py
└── result/               # Generated during test execution
    ├── transcript.step1
    ├── transcript.background
    └── output.txt
```

### Test Definition File (def.yaml)

```yaml
# Optional: Tags for filtering tests
tags: regression,smoke,long

# Required: Test steps
steps:
  - stepName1:
      - action1: specification
      - action2: specification
  
  - stepName2:
      - action1: specification
      - diff: result/file reference/file | filter1 | filter2
```

---

## Configuration

### Global Configuration

Create configuration files in `~/.bfan/`:

```
~/.bfan/
├── config.yaml           # Global configuration
├── bfan.json             # Binary environment settings
├── filters/              # Global filters
│   └── global_filter.py
└── suites/               # Suite-specific configurations
    └── btest/
        ├── config.yaml
        └── filters/
```

### Configuration File Format (config.yaml)

```yaml
env:
  variables:
    MY_VAR: "value"
    PATH_VAR: "${base}/bin:${libbase}/lib"

prefix:
  - "product/product1-${version}/${arch}/bin"
  - "product/product2-1.2.3/${arch}/bin"
```

### Binary Environment (bfan.json)

Place in binary directory:

```json
{
  "env": {
    "variables": {
      "LD_LIBRARY_PATH": "${PWD}/../lib",
      "CONFIG_PATH": "${dist}/config"
    }
  }
}
```

---

## Actions Reference

Actions are executed within test steps. They are reordered automatically:
1. `skip` actions execute first
2. Regular actions execute in order
3. `diff` actions execute last

### run
Executes a command and captures output.

```yaml
- run: python test.py
- run: ./myapp --option value
```

**Features:**
- Captures stdout and stderr to transcript file
- Checks exit code (0 = success by default)
- Supports variable substitution
- Timeout: 1200s default

### background
Starts a process in the background.

```yaml
- background: python server.py
- background: 0 ./service --daemon    # With ID for later reference
```

**Features:**
- Process runs concurrently with subsequent actions
- Output captured to `result/transcript.background`
- Can be killed with `kill` action
- Automatically terminated at test end
- Optional numeric ID for selective killing

### kill
Terminates a specific background process by ID.

```yaml
- kill: 0    # Kills background process with ID 0
```

### shell
Executes a shell command (similar to run, but with shell=True).

```yaml
- shell: echo $HOME > output.txt
```

### diff
Compares result file with reference file, optionally applying filters.

```yaml
- diff: result/output.txt reference/output.txt
- diff: result/transcript.step1 reference/transcript.step1 | filter1 | filter2
```

**Format:** `result_file reference_file | filter1 | filter2 | ...`

**Features:**
- Generates unified diff output
- Filters applied to both files
- Creates `.diff` file on mismatch
- Creates `.sfiltered` and `.rfiltered` files showing filtered content

### exitCode
Sets expected exit code for next `run` command.

```yaml
- exitCode: 1
- run: ./failing_command    # Expected to exit with code 1
```

**Default:** 0 (success)

### timeout
Sets timeout (in seconds) for next `run` command.

```yaml
- timeout: 60
- run: ./long_running_process
```

**Default:** 1200 seconds (20 minutes)

### skip
Skips remaining actions in the step.

```yaml
- skip: "Not implemented yet"
- run: this_will_not_execute
```

---

## Filters

Filters process output line-by-line before comparison. They can remove, modify, or buffer lines.

### Filter Locations (in order of precedence)
1. Test directory: `testname.btest/filters/`
2. Suite directory: `~/.bfan/suites/btest/filters/`
3. Global directory: `~/.bfan/filters/`

### Creating a Custom Filter

Create a Python file with a `Filter` class:

```python
# my_filter.py
class Filter():
    def __init__(self, out):
        self.out = out
    
    def write(self, line):
        # Modify or filter line
        if line.startswith("IGNORE:"):
            return None    # Skip this line
        
        # Modify line
        line = line.replace("sensitive_data", "REDACTED")
        
        # Pass to next filter
        return self.out.write(line)
    
    def close(self):
        # Optional: return buffered lines
        return self.out.close()
```

### Built-in Filter

The framework includes a built-in filter that removes lines starting with `[bfan]>` (framework messages).

### Filter Chain Example

```yaml
- diff: result/output.txt reference/output.txt | timestamps | sort | unique
```

Filters are applied in order: timestamps → sort → unique

---

## Environment Variables

### BFAN Environment Variables

Set via `--env` or system environment (prefix with `BFAN_`):

```bash
export BFAN_DEBUG=1
export BFAN_BASE=/opt/product
export BFAN_LIBBASE=/opt/libs
bfan run
```

Or via command line:
```bash
bfan run --env=DEBUG=1,BASE=/opt/product
```

### Variable Substitution

Variables can be used in configuration files with `${variable}` syntax:

**Available variables:**
- `${base}` - Value of `BFAN_BASE`
- `${libbase}` - Value of `BFAN_LIBBASE` (defaults to `${base}`)
- `${arch}` - Binary architecture from `--arch`
- `${PWD}` - Current working directory
- `${dist}` - Distribution path (same as `${base}`)
- `${configPath}` - Path to `.bfan` config directory
- `${suite}` - Test suite name (e.g., "btest")

**Example:**
```yaml
env:
  variables:
    MY_PATH: "${base}/bin:${libbase}/lib"
    CONFIG: "${configPath}/suites/${suite}/config.json"
```

### System Environment Variables

Standard shell variables are also substituted:

```yaml
- run: echo $HOME    # Uses system HOME variable
```

### Environment Variable Precedence

Environment variables are merged in this order (later overrides earlier):
1. System environment
2. Global config (`~/.bfan/config.yaml`)
3. Suite config (`~/.bfan/suites/<suite>/config.yaml`)
4. Binary config (`bfan.json` in executable directory)
5. Background process environments (accumulated)
6. Command-line `--env` parameters

---

## Advanced Features

### Tag-Based Test Filtering

Use boolean expressions to filter tests:

```yaml
# In def.yaml
tags: regression,smoke,gen4,slow
```

```bash
# Run only regression tests
bfan run --tags=regression

# Run tests that are (regression OR smoke) AND NOT slow
bfan run --tags="(regression or smoke) and not slow"

# Run gen4 or gen5 tests
bfan run --tags="gen4 or gen5"
```

**Operators:** `and`, `or`, `not`, parentheses `()`

### Background Process Management

```yaml
steps:
  - startServer:
      - background: 0 python server.py --port 8080
      - run: sleep 2    # Wait for server startup
  
  - testServer:
      - run: curl http://localhost:8080/api/test
      - diff: result/transcript.testServer reference/transcript.testServer
  
  - stopServer:
      - kill: 0    # Stop the server
```

**Features:**
- Automatic process cleanup on test completion
- Child process tracking and cleanup
- Output captured separately to `transcript.background`
- Environment variables persist across steps

### Running Specific Steps

When developing or debugging tests, you can run just specific steps:

```bash
# Run a single step
bfan run --step mySpecificStep tests/mytest.btest

# Run multiple steps
bfan run --step step1,step2,step3 tests/mytest.btest
```

**Features:**
- Skips cleanup of result directory by default
- Only executes specified steps
- Useful for iterative development
- All setup/background processes from previous steps are skipped

**Note:** The steps must exist in the test definition, otherwise an error is shown with available steps.

### Skipping Result Directory Cleanup

By default, BFAN cleans the result directory before running tests. You can skip this cleanup:

```bash
bfan run --noclean tests/mytest.btest
```

**Use cases:**
- Debugging: preserve files from previous runs
- Iterative development: avoid re-copying large source files
- Manual test setup: keep manually created files in result directory
- Performance: skip cleanup when running tests repeatedly

**Note:** The result directory will still be created if it doesn't exist, and source files will still be copied to it.

### Stdin Redirection

Redirect file content to command stdin using pipe syntax:

```yaml
- run: input.txt | python3 interactive_script.py
```

The file content is written line-by-line to the process stdin.

### JUnit XML Report Generation

```bash
bfan run --genXml --outputName=results --arch=x86_64 tests/
```

Generates `results.x86_64.xml` with:
- Test results (pass/fail)
- Execution times
- Error messages
- Step details
- Diff file references

**XML Structure:**
```xml
<testsuites>
  <testsuite name="btest.x86_64" tests="5" time="120.5">
    <testcase name="test1" classname="test1" time="10.2">
      <system-out>
        Step details and output...
      </system-out>
      <!-- <failure> element if test failed -->
    </testcase>
  </testsuite>
</testsuites>
```

### Post-Test Hook

Define a command to run after each test:

```bash
export BFAN_POSTRUNHOOK="python cleanup.py"
bfan run
```

The hook runs as an additional step after all defined steps, with the same environment.

### Parallel Test Execution

BFAN internally supports concurrent test preparation and execution:
- Tests are executed sequentially but with concurrent I/O
- Background processes run concurrently within tests
- Thread-safe listeners aggregate results

### Test List Files

Create a file listing test paths:

```
# tests.txt
tests/test1.btest
tests/test2.btest
tests/subdir/test3.btest
```

Run all tests from the list:
```bash
bfan run tests.txt
```

### Recursive Test Discovery

```bash
# Run all tests in directory tree
bfan run tests/
```

Searches for all `def.yaml` files recursively.

---

## Examples

### Example 1: Simple Command Test

```yaml
# def.yaml
steps:
  - executeCommand:
      - run: echo "Hello World"
      - diff: result/transcript.executeCommand reference/transcript.executeCommand
```

### Example 2: Multi-Step Test with Background Process

```yaml
# def.yaml
tags: integration,server
steps:
  - startServer:
      - background: 0 python server.py --port 8080
      - run: sleep 3
  
  - testEndpoint:
      - run: curl -X GET http://localhost:8080/api/status
      - diff: result/transcript.testEndpoint reference/transcript.testEndpoint | timestamps
  
  - testPost:
      - run: curl -X POST -d '{"key":"value"}' http://localhost:8080/api/data
      - diff: result/transcript.testPost reference/transcript.testPost | timestamps
  
  - cleanup:
      - kill: 0
```

### Example 3: Error Handling Test

```yaml
# def.yaml
steps:
  - testSuccess:
      - run: python script.py --valid-input
  
  - testFailure:
      - exitCode: 1
      - run: python script.py --invalid-input
      - exitCode: 0    # Reset to default
```

### Example 4: Timeout Test

```yaml
# def.yaml
steps:
  - quickTest:
      - timeout: 5
      - run: python fast_script.py
  
  - longTest:
      - timeout: 300
      - run: python slow_script.py
```

### Example 5: Complex Filtering

```yaml
# def.yaml
steps:
  - generateOutput:
      - run: python test_generator.py
      - diff: result/output.txt reference/output.txt | remove_timestamps | sort | unique
      - diff: result/errors.log reference/errors.log | filter_paths
```

### Example 6: Conditional Execution with Skip

```yaml
# def.yaml
steps:
  - platformSpecific:
      - skip: "Windows only test"    # Skips on other platforms
      - run: windows_specific_command.exe
  
  - crossPlatform:
      - run: python cross_platform.py
```

### Example 7: Using Environment Variables

```yaml
# config.yaml
env:
  variables:
    APP_HOME: "${base}/myapp"
    LIB_PATH: "${libbase}/lib"
    DATA_DIR: "${PWD}/data"
```

```yaml
# def.yaml
steps:
  - runWithEnv:
      - run: myapp --config ${APP_HOME}/config.yaml
      - diff: result/transcript.runWithEnv reference/transcript.runWithEnv
```

### Example 8: Full CI Integration

```bash
#!/bin/bash
# ci_test.sh

export BFAN_BASE=/opt/product
export BFAN_LIBBASE=/opt/libs

bfan run \
  --genXml \
  --outputName=ci_results \
  --arch=linux_x64 \
  --tags="regression and not slow" \
  --view=jsonSummary \
  --clearPassed \
  tests/ | tee test_output.json

exit ${PIPESTATUS[0]}
```

---

## Troubleshooting

### Common Issues

#### 1. "Could not read file: 'def.yaml'"
**Solution:** Ensure test directory contains `def.yaml` file.

#### 2. "Error: unable to find executable"
**Solution:** 
- Check executable exists and has correct permissions
- Verify `prefix` configuration in config.yaml
- Set `BFAN_BASE` environment variable
- Use absolute paths or ensure executable is in PATH

#### 3. "Unable to process variable settings"
**Solution:** 
- Check Mako template syntax in config files
- Verify all referenced variables are defined
- Check for syntax errors in `${variable}` expressions

#### 4. "Timeout" error
**Solution:**
- Increase timeout: `- timeout: 3600`
- Check if process is actually hanging
- Review process dependencies (e.g., background services not started)

#### 5. Diff fails unexpectedly
**Solution:**
- Run `bfan diff` to see actual differences
- Check filter implementations
- Verify reference files exist
- Look at `.sfiltered` and `.rfiltered` files to see filtered output

#### 6. Background process not terminating
**Solution:**
- Ensure proper cleanup with `kill` action
- Check child process spawning
- Review background process logs in `transcript.background`

#### 7. "The background process has been closed unexpectedly"
**Solution:**
- Process crashed - check `transcript.background` for errors
- Add error handling in background process
- Increase startup delay before dependent steps

#### 8. Environment variables not working
**Solution:**
- Prefix with `BFAN_` for system env: `export BFAN_MYVAR=value`
- Or use `--env=MYVAR=value`
- Check variable substitution syntax: `${var}` in YAML, `$VAR` in commands

### Debug Mode

Enable detailed output:

```bash
bfan run --stdout tests/mytest.btest
```

This shows all command output in real-time.

### Verbose Diff Output

```bash
bfan diff tests/mytest.btest
```

Shows full diff output without running test.

### Checking Test Structure

```bash
# Validate test directory
ls -la tests/mytest.btest/

# Should contain:
# - def.yaml (required)
# - reference/ (if using diff actions)
# - source/ (optional)
```

### Examining Generated Files

After test execution:
```bash
cd tests/mytest.btest/result/

# View transcripts
cat transcript.step1
cat transcript.background

# View filtered versions
cat output.txt.sfiltered    # Source filtered
cat output.txt.rfiltered    # Reference filtered

# View diff
cat output.txt.diff
```

---

## Best Practices

### 1. Test Organization
- Use descriptive test and step names
- Group related tests in subdirectories
- Use meaningful tags for filtering

### 2. Reference Files
- Keep reference files minimal and focused
- Update reference files carefully using `bfan update`
- Version control reference files

### 3. Filters
- Create reusable filters for common patterns
- Place shared filters in global directory
- Document filter behavior

### 4. Environment Management
- Use configuration files for environment setup
- Keep sensitive data out of test definitions
- Use variable substitution for portability

### 5. Background Processes
- Always use IDs for background processes you'll need to kill
- Add appropriate delays after starting services
- Clean up background processes explicitly

### 6. Timeouts
- Set realistic timeouts
- Use shorter timeouts for quick-fail scenarios
- Document long-running operations

### 7. Error Messages
- Include context in skip messages
- Make diff files reviewable
- Log important test phases

### 8. CI Integration
- Use `--genXml` for report generation
- Use `--tags` to run appropriate test suites
- Use `--clearPassed` to save space
- Use `jsonSummary` view for parsing

---

## Architecture Notes

### Design Principles
- YAML-based declarative test definitions
- Modular action system
- Pluggable filter architecture
- Thread-safe execution listeners
- Process lifecycle management

### Key Components

1. **TestExecutor**: Executes individual test actions
2. **TestRunner**: Manages overall test execution
3. **CMDExecutor**: Handles command execution and process management
4. **TranscriptWriterListener**: Records test execution details
5. **Filters**: Process and transform output
6. **Listeners**: Receive test events (start, end, errors)

### Process Management
- Uses `psutil` for process tracking
- Monitors child processes recursively
- Handles SIGTERM/SIGKILL for cleanup
- Thread-based stream readers for stdout/stderr

### File Organization
- `source/` → copied to `result/` before test
- `result/` → working directory for test execution
- `reference/` → expected output files
- `filters/` → test-specific filters

---

## Appendix: Action Quick Reference

| Action | Purpose | Example |
|--------|---------|---------|
| `run` | Execute command | `- run: python test.py` |
| `background` | Start background process | `- background: 0 server.py` |
| `kill` | Stop background process | `- kill: 0` |
| `shell` | Execute shell command | `- shell: echo $VAR > file` |
| `diff` | Compare files | `- diff: result/a ref/a \| filter` |
| `exitCode` | Set expected exit code | `- exitCode: 1` |
| `timeout` | Set command timeout | `- timeout: 60` |
| `skip` | Skip remaining actions | `- skip: "reason"` |

---

## Support and Contributing

### Reporting Issues
Include:
- BFAN version
- Test definition (def.yaml)
- Command used
- Full error output
- Environment details

### Feature Requests
Describe:
- Use case
- Expected behavior
- Example test definition

---

## License

MIT License

## Author

Piotr Sydow (sydow@wp.pl)

## Version History

- **1.0.14** - Current version
- Support for tag-based filtering
- Background process management
- JUnit XML reports
- Multiple output formats

---

*This documentation covers BFAN v1.0.14. For the latest updates, see the project repository.*

