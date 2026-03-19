package com.watchdog.core.persistence;

import com.watchdog.core.domain.TicketPriority;
import com.watchdog.core.domain.TicketStatus;
import com.watchdog.core.domain.TicketType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "tickets")
public class TicketEntity {

    @Id
    private UUID id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false, length = 2000)
    private String description;

    @Column(nullable = false)
    private String source;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TicketType type;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TicketPriority priority;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TicketStatus status;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected TicketEntity() {
    }

    public TicketEntity(
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
