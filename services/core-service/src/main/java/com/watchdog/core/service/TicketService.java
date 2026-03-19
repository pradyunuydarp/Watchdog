package com.watchdog.core.service;

import com.watchdog.core.domain.Ticket;
import com.watchdog.core.domain.TicketPriority;
import com.watchdog.core.domain.TicketType;
import com.watchdog.core.repository.TicketRepository;
import com.watchdog.core.web.dto.TicketCreateRequest;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class TicketService {

    private final TicketRepository ticketRepository;

    public TicketService(TicketRepository ticketRepository) {
        this.ticketRepository = ticketRepository;
    }

    public Ticket createTicket(TicketCreateRequest request) {
        Ticket ticket = Ticket.open(
                request.title(),
                request.description(),
                request.source(),
                request.type(),
                request.priority());
        return ticketRepository.save(ticket);
    }

    public List<Ticket> listTickets() {
        return ticketRepository.findAll();
    }

    public Ticket getTicket(UUID id) {
        return ticketRepository.findById(id)
                .orElseThrow(() -> new TicketNotFoundException(id));
    }

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
