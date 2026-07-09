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
