package com.watchdog.core.service;

import com.watchdog.core.domain.Ticket;
import com.watchdog.core.domain.TicketPriority;
import com.watchdog.core.domain.TicketType;
import com.watchdog.core.repository.TicketRepository;
import com.watchdog.core.web.dto.TicketCreateRequest;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;

/**
 * Basic ticket command/query service used by the current REST API.
 *
 * <p>Higher-level orchestration from Kafka events should delegate to this service instead of bypassing
 * it, so ticket creation logic remains centralized.
 */
@Service
public class TicketService {

    private final TicketRepository ticketRepository;

    public TicketService(TicketRepository ticketRepository) {
        this.ticketRepository = ticketRepository;
    }

    /**
     * Creates a ticket directly from a user/API request.
     */
    public Ticket createTicket(TicketCreateRequest request) {
        Ticket ticket = Ticket.open(
                request.title(),
                request.description(),
                request.source(),
                request.type(),
                request.priority());
        return ticketRepository.save(ticket);
    }

    /**
     * Returns all tickets in repository-defined sort order.
     */
    public List<Ticket> listTickets() {
        return ticketRepository.findAll();
    }

    /**
     * Loads a single ticket or throws a domain-specific not-found exception.
     */
    public Ticket getTicket(UUID id) {
        return ticketRepository.findById(id)
                .orElseThrow(() -> new TicketNotFoundException(id));
    }

    /**
     * Creates a simple placeholder ticket that can be used by wiring checks during early development.
     */
    public Ticket createOperationalPlaceholderTicket(String source) {
        TicketCreateRequest request = new TicketCreateRequest(
                "Placeholder incident",
                "Initial core-service boilerplate ticket",
                source,
                TicketType.PROACTIVE_ALERT,
                TicketPriority.MEDIUM);
        return createTicket(request);
    }
}
