package com.watchdog.core.repository;

import com.watchdog.core.domain.Ticket;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Application-facing abstraction for ticket persistence.
 *
 * <p>The implementation can be purely in-memory for local scaffolding or backed by PostgreSQL when the
 * service runs in a more realistic environment.
 */
public interface TicketRepository {

    Ticket save(Ticket ticket);

    Optional<Ticket> findById(UUID id);

    List<Ticket> findAll();
}
