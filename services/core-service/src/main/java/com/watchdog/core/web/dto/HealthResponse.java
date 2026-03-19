package com.watchdog.core.web.dto;

import java.time.Instant;

public record HealthResponse(String service, String status, Instant timestamp) {
}
