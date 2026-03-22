package com.watchdog.core.repository;

import com.watchdog.core.domain.Ticket;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

@Component
@Profile({"local", "test"})
public class InMemoryTicketRepository implements TicketRepository {

    private final Map<UUID, Ticket> tickets = new ConcurrentHashMap<>();

    @Override
    public Ticket save(Ticket ticket) {
        tickets.put(ticket.getId(), ticket);
        return ticket;
    }

    @Override
    public Optional<Ticket> findById(UUID id) {
        return Optional.ofNullable(tickets.get(id));
    }

    @Override
    public List<Ticket> findAll() {
        return tickets.values().stream()
                .sorted(Comparator.comparing(Ticket::getCreatedAt).reversed())
                .toList();
    }

    /**
     * Seeds repository state for demos and tests.
     *
     * <p>The method copies the input list to avoid accidental concurrent modifications while loading
     * development fixtures.
     */
    public void seed(List<Ticket> seedTickets) {
        for (Ticket ticket : new ArrayList<>(seedTickets)) {
            tickets.put(ticket.getId(), ticket);
        }
    }
}
