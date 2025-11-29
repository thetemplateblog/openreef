# Memory Optimization Guide

## Memory Allocation Failed Error

If you see "memory allocation failed", the PyBadge is running out of RAM (192 KB total). Here's how to fix it:

## Solution 1: Motor Features Use Lazy Loading (Already Implemented)

The motor controller and screen are **NOT loaded on startup**. They only load when you:
1. Select a motor from the menu
2. Press RIGHT to enter motor control mode

This saves ~20-30 KB of RAM until you actually need motor control.

## Solution 2: Disable Motor Features Completely

If you don't need motor control, disable it to save even more memory:

**Edit `src/colorimeter.py` line 142:**

```python
self.motor_enabled = False  # Changed from True to False
```

This removes motor menu items entirely and prevents any motor code from loading.

## Solution 3: Reduce Other Memory Usage

### Remove Unused Calibrations

Edit `calibrations.json` and remove test types you don't use:

```json
{
  "Phosphate API": { ... },
  // Remove these if not needed:
  // "Nitrate API": { ... },
  // "Nitrite API": { ... }
}
```

### Simplify Fonts

The display font libraries use memory. If needed, use smaller fonts.

## Solution 4: Check CircuitPython Version

CircuitPython 9.x vs 10.x may have different memory footprints. If issues persist, try the other version.

## Memory Usage Breakdown (Approximate)

| Component | RAM Usage |
|-----------|-----------|
| Base firmware | ~50 KB |
| Display screens | ~30 KB |
| Light sensor | ~10 KB |
| Calibrations | ~5-10 KB |
| Motor controller (lazy) | 0 KB (until activated) |
| Motor screen (lazy) | 0 KB (until activated) |
| Motor modules (when active) | ~25 KB |

## How to Check Free Memory

Add to your code:

```python
import gc
gc.collect()
print(f"Free memory: {gc.mem_free()} bytes")
```

## Still Having Issues?

If memory errors persist:

1. **Disable motors**: Set `motor_enabled = False`
2. **Remove unused imports**: Check for libraries you don't use
3. **Simplify calibrations**: Fewer test types = less memory
4. **Consider hardware upgrade**: ESP32-S3 based boards have more RAM

## Trade-offs

- **Motors Disabled**: More memory for measurements, no motor control
- **Motors Lazy-Loaded**: Memory efficient, slight delay on first motor use
- **Motors Always Loaded**: Fastest motor access, uses most memory

Current implementation uses **lazy loading** for best balance.
