package com.watchdog.core.web.dto;

import com.watchdog.core.domain.TicketPriority;
import com.watchdog.core.domain.TicketType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * Request payload for manual ticket creation.
 */
public record TicketCreateRequest(
        @NotBlank @Size(max = 160) String title,
        @NotBlank @Size(max = 2000) String description,
        @NotBlank @Size(max = 120) String source,
        @NotNull TicketType type,
        @NotNull TicketPriority priority) {
}
