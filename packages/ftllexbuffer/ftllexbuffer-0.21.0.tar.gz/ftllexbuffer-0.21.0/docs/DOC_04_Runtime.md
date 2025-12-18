---
spec_version: AFAD-v1
project_version: 0.21.0
context: RUNTIME
last_updated: 2025-12-16T00:00:00Z
maintainer: claude-opus-4-5
---

# Runtime Reference

---

## `number_format`

### Signature
```python
def number_format(
    value: int | float,
    locale_code: str = "en-US",
    *,
    minimum_fraction_digits: int = 0,
    maximum_fraction_digits: int = 3,
    use_grouping: bool = True,
    pattern: str | None = None,
) -> str:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `int \| float` | Y | Number to format. |
| `locale_code` | `str` | N | BCP 47 locale code. |
| `minimum_fraction_digits` | `int` | N | Minimum decimal places. |
| `maximum_fraction_digits` | `int` | N | Maximum decimal places. |
| `use_grouping` | `bool` | N | Use thousands separator. |
| `pattern` | `str \| None` | N | Custom Babel number pattern. |

### Constraints
- Return: Formatted number string.
- Raises: Never. Returns str(value) on error.
- State: None.
- Thread: Safe.

---

## `datetime_format`

### Signature
```python
def datetime_format(
    value: datetime | str,
    locale_code: str = "en-US",
    *,
    date_style: Literal["short", "medium", "long", "full"] = "medium",
    time_style: Literal["short", "medium", "long", "full"] | None = None,
    pattern: str | None = None,
) -> str:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `datetime \| str` | Y | Datetime or ISO string. |
| `locale_code` | `str` | N | BCP 47 locale code. |
| `date_style` | `Literal[...]` | N | Date format style. |
| `time_style` | `Literal[...] \| None` | N | Time format style. |
| `pattern` | `str \| None` | N | Custom Babel datetime pattern. |

### Constraints
- Return: Formatted datetime string.
- Raises: Never. Returns ISO format on error.
- State: None.
- Thread: Safe.

---

## `currency_format`

### Signature
```python
def currency_format(
    value: int | float,
    locale_code: str = "en-US",
    *,
    currency: str,
    currency_display: Literal["symbol", "code", "name"] = "symbol",
    pattern: str | None = None,
) -> str:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `value` | `int \| float` | Y | Monetary amount. |
| `locale_code` | `str` | N | BCP 47 locale code. |
| `currency` | `str` | Y | ISO 4217 currency code. |
| `currency_display` | `Literal[...]` | N | Display style. |
| `pattern` | `str \| None` | N | Custom CLDR currency pattern. |

### Constraints
- Return: Formatted currency string.
- Raises: Never. Returns "{currency} {value}" on error.
- State: None.
- Thread: Safe.

---

## `FunctionRegistry`

### Signature
```python
class FunctionRegistry:
    __slots__ = ("_functions",)

    def __init__(self) -> None: ...
    def register(
        self,
        func: Callable[..., str],
        *,
        ftl_name: str | None = None
    ) -> None: ...
    def get(self, name: str) -> Callable[..., str] | None: ...
    def get_callable(self, ftl_name: str) -> Callable[..., str] | None: ...
    def get_function_info(self, ftl_name: str) -> FunctionSignature | None: ...
    def copy(self) -> FunctionRegistry: ...
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|

### Constraints
- Return: Registry instance.
- State: Mutable registry dict.
- Thread: Unsafe for concurrent register().
- Memory: Uses __slots__ for reduced memory footprint.

---

## `FunctionRegistry.get_callable`

### Signature
```python
def get_callable(self, ftl_name: str) -> Callable[..., str] | None:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `ftl_name` | `str` | Y | FTL function name (e.g., "NUMBER"). |

### Constraints
- Return: Registered callable, or None if not found.
- State: Read-only access.
- Thread: Safe for reads.

---

## `FunctionRegistry.register`

### Signature
```python
def register(
    self,
    func: Callable[..., str],
    *,
    ftl_name: str | None = None,
    param_map: dict[str, str] | None = None,
) -> None:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `func` | `Callable[..., str]` | Y | Function to register. |
| `ftl_name` | `str \| None` | N | FTL name override (default: UPPERCASE of func name). |
| `param_map` | `dict[str, str] \| None` | N | Custom parameter mappings (overrides auto-generation). |

### Constraints
- Return: None.
- Raises: None.
- State: Mutates registry.
- Thread: Unsafe.

---

## `create_default_registry`

### Signature
```python
def create_default_registry() -> FunctionRegistry:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|

### Constraints
- Return: Fresh FunctionRegistry with NUMBER, DATETIME, CURRENCY registered.
- Raises: Never.
- State: Returns new isolated instance each call.
- Thread: Safe.
- Import: `from ftllexbuffer.runtime.functions import create_default_registry`

---

## `select_plural_category`

### Signature
```python
def select_plural_category(n: int | float, locale: str) -> str:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `n` | `int \| float` | Y | Number to categorize. |
| `locale` | `str` | Y | BCP 47 locale code. |

### Constraints
- Return: CLDR plural category (zero, one, two, few, many, other).
- Raises: Never. Returns "one" or "other" on invalid locale.
- State: None.
- Thread: Safe.

---

## FTL Function Name Mapping

| FTL Name | Python Function | Parameter Mapping |
|:---------|:----------------|:------------------|
| `NUMBER` | `number_format` | minimumFractionDigits -> minimum_fraction_digits |
| `DATETIME` | `datetime_format` | dateStyle -> date_style, timeStyle -> time_style |
| `CURRENCY` | `currency_format` | currencyDisplay -> currency_display |

---

## Custom Function Protocol

### Signature
```python
def CUSTOM_FUNCTION(
    positional_arg: FluentValue,
    *,
    keyword_arg: str = "default",
) -> str:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| First positional | `FluentValue` | Y | Primary input value. |
| Keyword args | `str` | N | Named options. |

### Constraints
- Return: Must return str.
- Raises: Should not raise. Return fallback on error.
- State: Should be stateless.
- Thread: Should be safe.

---

## `validate_resource`

### Signature
```python
def validate_resource(
    source: str,
    *,
    parser: FluentParserV1 | None = None,
) -> ValidationResult:
```

### Contract
| Parameter | Type | Req | Description |
|:----------|:-----|:----|:------------|
| `source` | `str` | Y | FTL file content. |
| `parser` | `FluentParserV1 \| None` | N | Parser instance (creates default if not provided). |

### Constraints
- Return: ValidationResult with errors and warnings.
- Raises: Never. Critical parse errors returned as ValidationError.
- State: None (creates isolated parser if not provided).
- Thread: Safe.
- Import: `from ftllexbuffer.validation import validate_resource`

---

## Module Constants

### `DEFAULT_CACHE_SIZE`

```python
DEFAULT_CACHE_SIZE: int = 1000
```

| Attribute | Value |
|:----------|:------|
| Type | `int` |
| Value | 1000 |
| Location | `ftllexbuffer.runtime.bundle` |

- Purpose: Default maximum cache entries for FluentBundle format results.
- Usage: Referenced by `FluentBundle.__init__`, `create()`, `for_system_locale()`.

---

### `UNICODE_FSI` / `UNICODE_PDI`

```python
UNICODE_FSI: str = "\u2068"  # U+2068 FIRST STRONG ISOLATE
UNICODE_PDI: str = "\u2069"  # U+2069 POP DIRECTIONAL ISOLATE
```

| Attribute | Value |
|:----------|:------|
| Type | `str` |
| Location | `ftllexbuffer.runtime.resolver` |

- Purpose: Unicode bidirectional isolation characters per Unicode TR9.
- Usage: Wraps interpolated values when `use_isolating=True`.

---

### `MAX_RESOLUTION_DEPTH`

```python
MAX_RESOLUTION_DEPTH: int = 100
```

| Attribute | Value |
|:----------|:------|
| Type | `int` |
| Value | 100 |
| Location | `ftllexbuffer.runtime.resolver` |

- Purpose: Maximum message reference chain depth.
- Usage: Prevents RecursionError from long non-cyclic reference chains.

---
