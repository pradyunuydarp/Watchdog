package com.watchdog.core.web.dto;

import com.watchdog.core.domain.TicketPriority;
import com.watchdog.core.domain.TicketStatus;
import com.watchdog.core.domain.TicketType;
import java.time.Instant;
import java.util.UUID;

public record TicketResponse(
        UUID id,
        String title,
        String description,
        String source,
        TicketType type,
        TicketPriority priority,
        TicketStatus status,
        Instant createdAt,
        Instant updatedAt) {
}
