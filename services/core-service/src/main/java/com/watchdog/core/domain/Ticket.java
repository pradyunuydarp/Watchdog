package com.watchdog.core.domain;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

public class Ticket {

    private final UUID id;
    private final String title;
    private final String description;
    private final String source;
    private final TicketType type;
    private final TicketPriority priority;
    private TicketStatus status;
    private final Instant createdAt;
    private Instant updatedAt;

    private Ticket(
            UUID id,
            String title,
            String description,
            String source,
            TicketType type,
            TicketPriority priority,
            TicketStatus status,
            Instant createdAt,
            Instant updatedAt) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.source = source;
        this.type = type;
        this.priority = priority;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public static Ticket open(String title, String description, String source, TicketType type, TicketPriority priority) {
        Instant now = Instant.now();
        return new Ticket(UUID.randomUUID(), title, description, source, type, priority, TicketStatus.OPEN, now, now);
    }

    public Ticket transitionTo(TicketStatus nextStatus) {
        this.status = Objects.requireNonNull(nextStatus, "nextStatus");
        this.updatedAt = Instant.now();
        return this;
    }

    public UUID getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getDescription() {
        return description;
    }

    public String getSource() {
        return source;
    }

    public TicketType getType() {
        return type;
    }

    public TicketPriority getPriority() {
        return priority;
    }

    public TicketStatus getStatus() {
        return status;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
