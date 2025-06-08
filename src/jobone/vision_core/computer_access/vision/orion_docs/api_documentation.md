# Orion Vision Core API

**Version:** 2.0.0  
**Generated:** 2025-06-05T19:39:19.772682

Harika API Documentation for Orion Vision Core

## API Endpoints

### GET /api/status

**Description:** Get current Orion system status

Returns:
    Dict containing system status information

**Parameters:**

**Returns:** typing.Dict[str, typing.Any]

---

### POST /api/process

**Description:** Process user input through Orion system

Args:
    user_input: The user's input text
    context: Optional context information

Returns:
    Processing result dictionary

**Parameters:**
- `user_input` (<class 'str'>) - Required
- `context` (typing.Optional[typing.Dict]) - Optional (default: None)

**Returns:** typing.Dict[str, typing.Any]

---

### GET /api/metrics

**Description:** Get system performance metrics

Returns:
    Dictionary of performance metrics

**Parameters:**

**Returns:** typing.Dict[str, float]

---

