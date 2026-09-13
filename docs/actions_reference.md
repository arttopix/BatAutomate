# BAT Automate Actions Reference Guide

This document provides a comprehensive specification of standard actions available in BAT Automate. Each action contains parameter specifications, return types, and concrete JSON examples for flow authoring.

---

## Table of Contents

1. [Web Automation (`web.*`)](#web-automation-web)
   - [web.open](#webopen)
   - [web.click](#webclick)
   - [web.type](#webtype)
   - [web.get_text](#webget_text)
   - [web.screenshot](#webscreenshot)
   - [web.close](#webclose)
2. [Data and Excel (`excel.*`)](#data-and-excel-excel)
   - [excel.read](#excelread)
   - [excel.write](#excelwrite)
3. [Control Flow and Logic (`logic.*`)](#control-flow-and-logic-logic)
   - [logic.set_variable](#logicset_variable)
   - [logic.delay](#logicdelay)
   - [logic.if](#logicif)
   - [logic.loop](#logicloop)
   - [logic.append](#logicappend)
4. [HTTP API Integration (`http.*`)](#http-api-integration-http)
   - [http.request](#httprequest)

---

## Web Automation (`web.*`)

Powered by Playwright with automatic browser binary installation.

### `web.open`
Launches a browser instance and navigates to a target URL.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | string | Yes | - | URL of the website to open |
| `headless` | boolean | No | `false` | Run browser in headless mode |
| `timeout` | number | No | `30000` | Navigation timeout in milliseconds |

**Example:**
```json
{
  "id": "step_open",
  "name": "Open Target Website",
  "action": "web.open",
  "parameters": {
    "url": "https://rpachallenge.com/",
    "headless": true
  }
}
```

---

### `web.click`
Clicks an element identified by CSS selector, XPath, or adjacent label text.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `selector` | string | Either | - | CSS selector or XPath expression |
| `label` | string | Either | - | Label text preceding the input element |

**Example:**
```json
{
  "id": "step_click_submit",
  "name": "Click Submit Button",
  "action": "web.click",
  "parameters": {
    "selector": "//input[@value='Submit']"
  }
}
```

---

### `web.type`
Fills text into an input or textarea element.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | Yes | `""` | Text to enter into the field |
| `selector` | string | Either | - | CSS selector or XPath expression |
| `label` | string | Either | - | Case-sensitive label text matching preceding element |

**Example:**
```json
{
  "id": "step_type_name",
  "name": "Fill First Name",
  "action": "web.type",
  "parameters": {
    "label": "First Name",
    "text": "${row.First Name}"
  }
}
```

---

### `web.get_text`
Extracts visible inner text from a target element.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `selector` | string | Either | - | CSS selector or XPath expression |
| `label` | string | Either | - | Label identifier |

**Example:**
```json
{
  "id": "step_read_score",
  "name": "Read Score Message",
  "action": "web.get_text",
  "parameters": {
    "selector": "//div[contains(@class, 'congratulations')]"
  },
  "output_var": "final_score"
}
```

---

### `web.screenshot`
Captures a screenshot of the current page.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | No | `"screenshot.png"` | Destination file path (relative to bundle or absolute) |
| `full_page` | boolean | No | `false` | Capture complete scrollable page |

**Example:**
```json
{
  "id": "step_capture",
  "name": "Capture Page Screenshot",
  "action": "web.screenshot",
  "parameters": {
    "path": "./assets/result.png",
    "full_page": false
  }
}
```

---

### `web.close`
Closes current page, browser context, and terminates Playwright session.

**Parameters:** None.

**Example:**
```json
{
  "id": "step_close_browser",
  "name": "Close Browser Session",
  "action": "web.close",
  "parameters": {}
}
```

---

## Data and Excel (`excel.*`)

Provides zero-license Excel reading and writing via Pandas and OpenPyXL.

### `excel.read`
Reads an Excel sheet into an in-memory list of dictionaries (records).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file_path` | string | Yes | - | Path to .xlsx or .xls file (relative paths resolved against bundle) |
| `sheet_name` | string / int | No | `0` | Sheet name or index to read |
| `clean_headers` | boolean | No | `true` | Strip leading and trailing whitespace from column names |

**Example:**
```json
{
  "id": "step_read_excel",
  "name": "Read Excel Data",
  "action": "excel.read",
  "parameters": {
    "file_path": "./assets/challenge.xlsx",
    "clean_headers": true
  },
  "output_var": "challenge_data"
}
```

---

### `excel.write`
Writes a list of dictionaries or single dictionary to an Excel spreadsheet.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file_path` | string | Yes | - | Output path for generated Excel workbook |
| `data` | list / dict | Yes | `[]` | List of dictionaries or data records to export |
| `sheet_name` | string | No | `"Sheet1"` | Destination sheet name |

**Example:**
```json
{
  "id": "step_save_audit",
  "name": "Save Non-Programmers Audit Report",
  "action": "excel.write",
  "parameters": {
    "file_path": "./assets/non_programmers_audit.xlsx",
    "data": "${non_programmers}",
    "sheet_name": "AuditReport"
  }
}
```

---

## Control Flow and Logic (`logic.*`)

Core orchestration primitives for variable manipulation, loops, and conditions.

### `logic.set_variable`
Assigns a value to a named execution context variable.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Variable name to create or update |
| `value` | any | Yes | Value or evaluated expression |

**Example:**
```json
{
  "id": "step_set_counter",
  "name": "Initialize Counter",
  "action": "logic.set_variable",
  "parameters": {
    "name": "processed_count",
    "value": 0
  }
}
```

---

### `logic.delay`
Pauses execution for a specified duration.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `seconds` | number | No | `1.0` | Sleep duration in seconds |

**Example:**
```json
{
  "id": "step_wait",
  "name": "Wait for Page Stabilization",
  "action": "logic.delay",
  "parameters": {
    "seconds": 2.5
  }
}
```

---

### `logic.if`
Conditionally branches execution into `sub_steps` (when condition evaluates to true) or `else_steps` (when false).

**Supported Operators:**
- `equals`, `==`, `eq`
- `not_equals`, `!=`, `neq`
- `greater_than`, `>`, `gt`
- `greater_than_or_equal`, `>=`, `gte`
- `less_than`, `<`, `lt`
- `less_than_or_equal`, `<=`, `lte`
- `contains`, `in`
- `not_contains`, `not_in`
- `starts_with`, `ends_with`
- `is_empty`, `is_not_empty`

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `left` | any | Yes* | Left-hand operand |
| `operator` | string | No (default: equals) | Comparison operator |
| `right` | any | No | Right-hand operand |
| `condition` | string | Yes* | Alternatively, single expression such as `"${val} == target"` |

*\*Note: Either `left` or `condition` parameter is required.*

**Example:**
```json
{
  "id": "sub_check_role",
  "name": "Check If Role is Programmer",
  "action": "logic.if",
  "parameters": {
    "left": "${row.Role in Company}",
    "operator": "equals",
    "right": "Programmer"
  },
  "sub_steps": [
    {
      "id": "fill_form",
      "name": "Fill Form",
      "action": "web.type",
      "parameters": { "label": "First Name", "text": "${row.First Name}" }
    }
  ],
  "else_steps": [
    {
      "id": "collect_audit",
      "name": "Append to Audit",
      "action": "logic.append",
      "parameters": {
        "target": "non_programmers",
        "item": { "First Name": "${row.First Name}", "Role": "${row.Role in Company}" }
      }
    }
  ]
}
```

---

### `logic.loop`
Iterates over an array or list of objects, binding each element to an item variable.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `items` | list / string | Yes | Array or variable reference `${var}` to iterate |
| `item_var` | string | No (default: item) | Context variable name representing the current iteration item |

**Example:**
```json
{
  "id": "step_loop_rows",
  "name": "Iterate Dataset Rows",
  "action": "logic.loop",
  "parameters": {
    "items": "${challenge_data}",
    "item_var": "row"
  },
  "sub_steps": [
    {
      "id": "process_row",
      "name": "Process Row Item",
      "action": "logic.if",
      "parameters": {
        "left": "${row.Status}",
        "operator": "equals",
        "right": "Active"
      }
    }
  ]
}
```

---

### `logic.append`
Appends an item, dictionary, or primitive value to a list in context variables. If the target variable does not exist, it initializes an empty list.

**Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `target` | string | Yes | Name of the list variable in context |
| `item` | any | Yes | Item or object to append |

**Example:**
```json
{
  "id": "append_record",
  "name": "Add Non-Programmer to List",
  "action": "logic.append",
  "parameters": {
    "target": "non_programmers",
    "item": {
      "First Name": "${row.First Name}",
      "Role in Company": "${row.Role in Company}"
    }
  }
}
```

---

## HTTP API Integration (`http.*`)

Enables direct REST API interaction without external browser overhead.

### `http.request`
Executes an HTTP request and outputs status code, response headers, and body.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | string | Yes | - | Request URL endpoint |
| `method` | string | No | `"GET"` | HTTP method (GET, POST, PUT, DELETE, PATCH) |
| `headers` | dict | No | `{}` | HTTP request headers |
| `payload` | dict / string | No | `null` | Request body (JSON dict or raw string) |
| `timeout` | number | No | `30` | Request timeout in seconds |

**Example:**
```json
{
  "id": "step_send_webhook",
  "name": "Notify Notification Webhook",
  "action": "http.request",
  "parameters": {
    "url": "https://api.example.com/v1/notify",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer ${env.API_KEY}"
    },
    "payload": {
      "status": "completed",
      "total_processed": 10
    }
  },
  "output_var": "api_response"
}
```
