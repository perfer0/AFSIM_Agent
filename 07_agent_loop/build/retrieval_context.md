## knowledge\afsim_snippets\eoir_platform_instance.md (score=8)

# EOIR Platform Instance Pattern

This snippet shows the AFSIM pattern for a UAV platform using an EOIR sensor.

```text
platform uav UAV
   side blue

   route
      position 34:30:00n 116:00w altitude 60000 ft speed 350 kts heading 0 deg
   end_route

   execute at_time 1 min relative
       BeginImaging("eoir", "", -90, 68000);
   end_execute
   execute at_time 4 min relative
       EndImaging();
   end_execute
end_platform
```

Key points:

- `platform uav UAV` creates a platform instance named `uav` from platform type `UAV`.
- `side blue` assigns force side.
- `route` defines initial position, altitude, speed, and heading.
- `execute at_time ... relative` calls scripts defined on the UAV platform type.

---

## knowledge\afsim_snippets\ground_site_targets.md (score=4)

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

---

## knowledge\afsim_snippets\event_output_sensor.md (score=2)

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