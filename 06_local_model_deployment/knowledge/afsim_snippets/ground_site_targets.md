# Ground Site Target Pattern

This snippet shows the AFSIM pattern for simple red ground targets.

```text
platform sr_target_01 GROUND_SITE
   side red
   position 34:45:00n 116:45w
end_platform
```

Key points:

- `GROUND_SITE` is a platform type.
- Each target is a platform instance.
- Static targets can use `position` instead of `route`.
