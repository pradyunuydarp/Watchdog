package com.watchdog.core.web;

import com.watchdog.core.domain.Ticket;
import com.watchdog.core.service.TicketService;
import com.watchdog.core.web.dto.TicketCreateRequest;
import com.watchdog.core.web.dto.TicketResponse;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/tickets")
public class TicketController {

    private final TicketService ticketService;

    public TicketController(TicketService ticketService) {
        this.ticketService = ticketService;
    }

    @PostMapping
    public ResponseEntity<TicketResponse> createTicket(@Valid @RequestBody TicketCreateRequest request) {
        Ticket ticket = ticketService.createTicket(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(toResponse(ticket));
    }

    @GetMapping
    public List<TicketResponse> listTickets() {
        return ticketService.listTickets().stream()
                .map(this::toResponse)
                .toList();
    }

    @GetMapping("/{id}")
    public TicketResponse getTicket(@PathVariable UUID id) {
        return toResponse(ticketService.getTicket(id));
    }

    private TicketResponse toResponse(Ticket ticket) {
        return new TicketResponse(
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
}
