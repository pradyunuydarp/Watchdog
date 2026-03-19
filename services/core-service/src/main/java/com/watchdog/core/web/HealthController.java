package com.watchdog.core.web;

import com.watchdog.core.web.dto.HealthResponse;
import java.time.Instant;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/health")
public class HealthController {

    @GetMapping
    public ResponseEntity<HealthResponse> health() {
        return ResponseEntity.ok(new HealthResponse("watchdog-core-service", "UP", Instant.now()));
    }
}
