package com.watchdog.core.domain;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

/**
 * Domain model representing a single operational incident ticket.
 *
 * <p>The class intentionally remains persistence-agnostic. JPA-specific concerns live in
 * {@code TicketEntity}, while this type models the behavior the rest of the application depends on.
 * That separation keeps the orchestration layer easier to test and refactor.
 */
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

    /**
     * Creates a new open ticket using the minimum information needed by the current scaffold.
     *
     * <p>Prototype C will eventually create tickets from Kafka pointer events and enrichment payloads.
     * This factory remains the central path so later callers do not need to understand how timestamps
     * and initial state are derived.
     */
    public static Ticket open(String title, String description, String source, TicketType type, TicketPriority priority) {
        Instant now = Instant.now();
        return new Ticket(UUID.randomUUID(), title, description, source, type, priority, TicketStatus.OPEN, now, now);
    }

    /**
     * Rehydrates a ticket that was already persisted elsewhere.
     *
     * <p>This factory is primarily used by persistence adapters so they can rebuild a fully-populated
     * domain object without bypassing encapsulation via reflection.
     */
    public static Ticket rehydrate(
            UUID id,
            String title,
            String description,
            String source,
            TicketType type,
            TicketPriority priority,
            TicketStatus status,
            Instant createdAt,
            Instant updatedAt) {
        return new Ticket(id, title, description, source, type, priority, status, createdAt, updatedAt);
    }

    /**
     * Transitions the ticket to a new lifecycle state.
     *
     * <p>For now the method trusts callers to enforce valid state progressions. A future iteration can
     * move transition rules into this class if the lifecycle becomes more complex.
     */
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
