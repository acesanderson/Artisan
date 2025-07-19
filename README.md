# Artisan: LLM-Powered Developer Commands - Design Specification

## Project Overview

Artisan is a suite of specialized Neovim commands that leverage LLMs to perform focused development tasks. The system provides context-aware code analysis, generation, and modification capabilities that complement existing tools (Copilot, LSPs) rather than replace them.

## Core Architecture

### Command Pattern
Each Artisan command follows a consistent pattern:
1. **Context Gathering**: Extract relevant code and project context
2. **Prompt Application**: Apply specialized prompts with user customization
3. **LLM Processing**: Generate response using the Chain/Model system
4. **Output Handling**: Display results or modify files appropriately

### Shared Components
- **PromptLoader**: Manages specialized prompt templates for each command type
- **Context Engine**: Gathers project-wide context (flattening, dependency analysis)
- **Chain/Model System**: Handles LLM orchestration and response processing
- **Neovim Integration**: Consistent command interface and argument parsing

## Command Specifications

### 1. `:Critique [question]`

**Purpose**: Flexible code analysis with user-defined focus areas

**Input Arguments**:
- `question` (required): Custom analysis question or focus area
- Optional: `--scope` (selection|function|file|module) - defaults to current selection

**Context Gathering**:
- Target code (based on scope)
- Full project structure for architectural understanding
- Related functions/classes for dependency analysis

**Prompt Strategy**:
- Base critique template with code analysis framework
- User question injected as specific focus directive
- Project context provided for informed recommendations

**Output**:
- Display analysis in Neovim split/buffer (read-only)
- No file modifications

**Example Usage**:
```
:Critique Is my error handling robust enough?
:Critique Are there any performance bottlenecks here?
:Critique Does this follow project conventions?
```

**Example Input/Output**:
```python
# Input code:
def process_user_data(user_id):
    user = get_user(user_id)
    return user.email.upper()

# Command: :Critique Is my error handling robust enough?
# Output display:
"""
ARTISAN CRITIQUE: Error Handling Analysis

ISSUES IDENTIFIED:
1. No validation of user_id parameter - could be None, wrong type, or malformed
2. get_user() call has no error handling - will crash if user doesn't exist
3. No null check on user.email - will fail if email is None
4. No exception handling for .upper() method

RECOMMENDATIONS:
- Add input validation for user_id
- Wrap get_user() in try/except to handle UserNotFound scenarios  
- Add null checks before calling methods on user.email
- Consider returning None or raising custom exceptions for error cases

SEVERITY: High - Multiple crash points with common edge cases
"""
```

### 2. `:Test_code`

**Purpose**: Generate test files for functions, classes, or modules

**Input Arguments**:
- Optional: `--line` (line number for specific function/class)
- Optional: `--type` (unit|integration|memory) - defaults to unit
- Optional: `--output` (path) - defaults to `test/test_{filename}.py`

**Context Gathering**:
- Target code element (function, class, or entire file)
- Existing test patterns in the project
- Import dependencies and project structure
- Related code for comprehensive test scenarios

**Prompt Strategy**:
- Test generation template specialized by test type
- Analyze code behavior and edge cases
- Follow project's testing conventions and frameworks
- Generate realistic test data and scenarios

**Output**:
- Create new test file in specified location
- Handle existing file conflicts (append vs overwrite)
- Ensure proper imports and test structure

**Example Usage**:
```
:Test_code                          " Generate tests for current file
:Test_code --line 45               " Generate tests for function at line 45
:Test_code --type integration      " Generate integration tests
:Test_code --type memory           " Generate in-memory tests (no file I/O)
```

**Example Input/Output**:
```python
# Input code (in user_service.py):
def calculate_user_score(user_activities, bonus_multiplier=1.0):
    if not user_activities:
        return 0
    
    base_score = sum(activity.points for activity in user_activities)
    return int(base_score * bonus_multiplier)

# Command: :Test_code --line 15
# Output file (test/test_user_service.py):
import pytest
from unittest.mock import Mock
from user_service import calculate_user_score

class TestCalculateUserScore:
    def test_empty_activities_returns_zero(self):
        """Test that empty activities list returns 0."""
        result = calculate_user_score([])
        assert result == 0
        
    def test_none_activities_returns_zero(self):
        """Test that None activities returns 0."""
        result = calculate_user_score(None)
        assert result == 0
        
    def test_single_activity_calculation(self):
        """Test calculation with single activity."""
        activity = Mock(points=100)
        result = calculate_user_score([activity])
        assert result == 100
        
    def test_multiple_activities_sum(self):
        """Test sum of multiple activity points."""
        activities = [Mock(points=50), Mock(points=75), Mock(points=25)]
        result = calculate_user_score(activities)
        assert result == 150
        
    def test_bonus_multiplier_applied(self):
        """Test that bonus multiplier is properly applied."""
        activity = Mock(points=100)
        result = calculate_user_score([activity], bonus_multiplier=1.5)
        assert result == 150
        
    def test_result_is_integer(self):
        """Test that result is converted to integer."""
        activity = Mock(points=100)
        result = calculate_user_score([activity], bonus_multiplier=1.7)
        assert isinstance(result, int)
        assert result == 170
```

### 3. `:Docstring` (Enhanced)

**Purpose**: Generate contextual docstrings at various granularity levels

**Input Arguments**:
- Optional: `--line` (line number) - 0/1 for file-level, specific line for function/class
- Optional: `--style` (google|numpy|sphinx) - defaults to project convention

**Context Gathering**:
- Target element (project/module/function/class)
- Full project context for understanding purpose and relationships
- Existing docstring patterns in the codebase

**Prompt Strategy**:
- Specialized templates for each docstring level
- Analyze code purpose, parameters, return values, and exceptions
- Consider element's role within the larger system

**Output**:
- Insert docstring at appropriate location
- Handle existing docstring replacement

**Example Usage**:
```
:Docstring                    " Generate docstring for current function/file
:Docstring --line 0          " Generate module-level docstring
:Docstring --style numpy     " Use NumPy docstring format
```

**Example Input/Output**:
```python
# Input code:
def fetch_user_recommendations(user_id, category=None, limit=10):
    user_prefs = get_user_preferences(user_id)
    if category:
        items = filter_by_category(get_all_items(), category)
    else:
        items = get_all_items()
    
    scored_items = score_items_for_user(items, user_prefs)
    return sorted(scored_items, key=lambda x: x.score, reverse=True)[:limit]

# Command: :Docstring
# Output (inserted into function):
def fetch_user_recommendations(user_id, category=None, limit=10):
    """Fetch personalized item recommendations for a user.
    
    Retrieves user preferences and generates scored recommendations from available
    items, optionally filtered by category. Items are ranked by relevance score
    and returned in descending order of preference match.
    
    Args:
        user_id: Unique identifier for the user requesting recommendations
        category: Optional category filter to limit recommendation scope  
        limit: Maximum number of recommendations to return (default: 10)
        
    Returns:
        List of recommended items sorted by relevance score, limited to
        specified count. Each item includes computed preference score.
        
    Raises:
        UserNotFoundError: If user_id does not exist in the system
        ValidationError: If limit is negative or exceeds maximum allowed
    """
    user_prefs = get_user_preferences(user_id)
    # ... rest of function
```

### 4. `:Add_logs`

**Purpose**: Insert appropriate logging statements throughout code

**Input Arguments**:
- Optional: `--level` (debug|info|warning|error) - defaults to info
- Optional: `--strategy` (entry_exit|errors|key_points) - defaults to key_points
- Optional: `--scope` (function|file) - defaults to current function

**Context Gathering**:
- Target code scope
- Existing logging patterns and configuration in project
- Function parameters, return values, and exception handling
- Critical decision points and data transformations

**Prompt Strategy**:
- Analyze code flow to identify optimal logging points
- Generate contextual log messages with relevant variable information
- Follow project's logging conventions and formats
- Avoid over-logging while capturing essential information

**Output**:
- Modify file with logging statements inserted
- Preview changes before applying

**Example Usage**:
```
:Add_logs                           " Add logging to current function
:Add_logs --level debug            " Add debug-level logging
:Add_logs --strategy entry_exit    " Log function entry/exit only
:Add_logs --scope file             " Add logging throughout entire file
```

**Example Input/Output**:
```python
# Input code:
def process_payment(user_id, amount, payment_method):
    user = get_user(user_id)
    if user.account_balance < amount:
        raise InsufficientFundsError()
    
    transaction = create_transaction(user_id, amount, payment_method)
    result = payment_gateway.charge(payment_method, amount)
    
    if result.success:
        user.account_balance -= amount
        transaction.status = 'completed'
        save_user(user)
        save_transaction(transaction)
        send_receipt_email(user.email, transaction)
        return transaction
    else:
        transaction.status = 'failed'
        save_transaction(transaction)
        raise PaymentFailedError(result.error_message)

# Command: :Add_logs --strategy key_points
# Output:
import logging

logger = logging.getLogger(__name__)

def process_payment(user_id, amount, payment_method):
    logger.info(f"Processing payment: user_id={user_id}, amount={amount}, method={payment_method}")
    
    user = get_user(user_id)
    logger.debug(f"Retrieved user: {user_id}, balance={user.account_balance}")
    
    if user.account_balance < amount:
        logger.warning(f"Insufficient funds: user_id={user_id}, balance={user.account_balance}, required={amount}")
        raise InsufficientFundsError()
    
    transaction = create_transaction(user_id, amount, payment_method)
    logger.info(f"Created transaction: {transaction.id}")
    
    result = payment_gateway.charge(payment_method, amount)
    logger.debug(f"Payment gateway response: success={result.success}")
    
    if result.success:
        user.account_balance -= amount
        transaction.status = 'completed'
        save_user(user)
        save_transaction(transaction)
        logger.info(f"Payment completed successfully: transaction_id={transaction.id}, new_balance={user.account_balance}")
        send_receipt_email(user.email, transaction)
        return transaction
    else:
        transaction.status = 'failed'
        save_transaction(transaction)
        logger.error(f"Payment failed: transaction_id={transaction.id}, error={result.error_message}")
        raise PaymentFailedError(result.error_message)
```

## Implementation Architecture

### Directory Structure
```
artisan/
├── commands/
│   ├── __init__.py
│   ├── critique.py
│   ├── test_generation.py
│   ├── docstring.py
│   └── logging.py
├── logs/
│   └── logging_config
├── prompts/
│   ├── critique
│   ├── test_generation
│   ├── docstring
│   └── logging
├── core/
│   ├── context_engine.py
│   └── prompt_loader
└── main.py
```

### Core Components

**Context Engine** (`core/context_engine.py`):
- Responsible for gathering relevant code context
- Methods: `get_project_context()`, `get_function_context()`, `get_file_context()`
- Handles code parsing, dependency analysis, and context formatting

**Enhanced Prompt Loader** (`core/prompt_loader.py`):
- Manages prompt templates with variable substitution
- Supports prompt composition (base + specialization)
- Handles user customization parameters

**Neovim Interface** (`core/neovim_interface.py`):
- Parses command arguments consistently
- Handles cursor position and selection detection
- Manages output formatting and file modifications

**Command Classes** (`commands/*.py`):
- Each command implements a standard interface
- Handles command-specific logic and validation
- Coordinates between context gathering, prompt processing, and output

### Error Handling Strategy

**Graceful Degradation**:
- If full project context is too large, fall back to local context
- If LLM request fails, provide helpful error messages
- If file modifications fail, preserve original files

**Validation**:
- Validate command arguments before processing
- Check file permissions before modifications
- Verify generated code syntax when possible

**User Feedback**:
- Progress indicators for long-running operations
- Clear error messages with suggested fixes
- Preview capabilities for destructive operations

## Testing Strategy

**Unit Tests**:
- Test each command's context gathering logic
- Mock LLM responses to test output formatting
- Validate argument parsing and error handling

**Integration Tests**:
- Test complete command workflows with real codebases
- Verify Neovim integration works correctly
- Test prompt template rendering and variable substitution

**Quality Assurance**:
- Test commands on various Python project structures
- Verify generated content quality and relevance
- Ensure commands work with different coding styles

## Future Extensibility

**Plugin Architecture**:
- Commands are self-contained modules
- Easy to add new commands following the established pattern
- Prompt templates can be user-customized

**Configuration System**:
- Project-specific settings (test frameworks, logging patterns)
- User preferences (default arguments, output formats)
- LLM model selection and parameters

**TBD Commands** (*Future Consideration*):
- `:Modernize` - Update legacy code to modern Python practices
- `:Refactor` - Suggest and apply refactoring improvements
- `:Optimize` - Analyze and improve performance bottlenecks

## Success Metrics

**Developer Productivity**:
- Reduction in time spent writing boilerplate (tests, docs, logs)
- Improved code quality through AI-assisted analysis
- Faster onboarding to new codebases via critique functionality

**Code Quality**:
- Consistent documentation and testing coverage
- Better error handling and logging practices
- Adherence to project conventions and best practices

**System Reliability**:
- Commands complete successfully >95% of the time
- Generated content requires minimal manual editing
- No data loss or file corruption from command usage
