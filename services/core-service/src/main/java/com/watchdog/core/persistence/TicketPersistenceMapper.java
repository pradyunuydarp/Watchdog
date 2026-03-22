package com.watchdog.core.persistence;

import com.watchdog.core.domain.Ticket;
import org.springframework.stereotype.Component;

/**
 * Maps between the persistence entity and the domain model.
 */
@Component
public class TicketPersistenceMapper {

    public TicketEntity toEntity(Ticket ticket) {
        return new TicketEntity(
                ticket.getId(),
                ticket.getTitle(),
                ticket.getDescription(),
                ticket.getSource(),
                ticket.getType(),
                ticket.getPriority(),
                ticket.getStatus(),
                ticket.getCreatedAt(),
                ticket.getUpdatedAt());
    }

    public Ticket toDomain(TicketEntity entity) {
        return Ticket.rehydrate(
                entity.getId(),
                entity.getTitle(),
                entity.getDescription(),
                entity.getSource(),
                entity.getType(),
                entity.getPriority(),
                entity.getStatus(),
                entity.getCreatedAt(),
                entity.getUpdatedAt());
    }
}
