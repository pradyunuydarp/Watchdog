package com.watchdog.core.persistence;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Thin Spring Data repository for {@link TicketEntity}.
 */
public interface SpringDataTicketRepository extends JpaRepository<TicketEntity, UUID> {
}
