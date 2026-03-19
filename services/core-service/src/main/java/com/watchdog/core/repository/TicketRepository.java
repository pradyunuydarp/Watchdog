package com.watchdog.core.repository;

import com.watchdog.core.domain.Ticket;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface TicketRepository {

    Ticket save(Ticket ticket);

    Optional<Ticket> findById(UUID id);

    List<Ticket> findAll();
}
