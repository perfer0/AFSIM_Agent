# Sensor Event Output Pattern

This snippet shows sensor event output configuration.

```text
event_output
   file output/eoir_demo.evt
   enable SENSOR_DETECTION_ATTEMPT
   enable SENSOR_DETECTION_CHANGED
   enable SENSOR_MODE_ACTIVATED
   enable SENSOR_MODE_DEACTIVATED
   enable SENSOR_TRACK_INITIATED
   enable SENSOR_TRACK_DROPPED
   enable SENSOR_TURNED_ON
   enable SENSOR_TURNED_OFF
end_event_output
```

Key points:

- `event_output` controls event file output.
- Sensor event switches are useful for EOIR detection and tracking review.
