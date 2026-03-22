package com.watchdog.core.orchestration;

import com.watchdog.core.domain.Ticket;
import com.watchdog.core.domain.TicketPriority;
import com.watchdog.core.domain.TicketType;
import com.watchdog.core.messaging.event.EnrichmentEvent;
import com.watchdog.core.messaging.event.PointerEvent;
import com.watchdog.core.service.TicketService;
import com.watchdog.core.web.dto.TicketCreateRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * Application service responsible for converting asynchronous operational signals into ticket actions.
 *
 * <p>The intent is to keep Kafka listeners thin. They should receive bytes/strings, parse them, and hand
 * off to this service so orchestration logic remains testable without the messaging runtime.
 */
@Service
public class TicketOrchestrationService {

    private static final Logger log = LoggerFactory.getLogger(TicketOrchestrationService.class);

    private final TicketService ticketService;

    public TicketOrchestrationService(TicketService ticketService) {
        this.ticketService = ticketService;
    }

    /**
     * Creates a lightweight reactive ticket from a pointer event.
     *
     * <p>The method intentionally does not dereference the raw payload. In Prototype C, the NLP service is
     * responsible for doing that work and sending an enrichment event later.
     */
    public Ticket handlePointerEvent(PointerEvent pointerEvent) {
        TicketCreateRequest request = new TicketCreateRequest(
                "Incident from " + pointerEvent.source(),
                buildPointerDescription(pointerEvent),
                pointerEvent.source(),
                TicketType.REACTIVE_CRASH,
                TicketPriority.MEDIUM);

        Ticket createdTicket = ticketService.createTicket(request);
        log.info("Created ticket {} from pointer event {}", createdTicket.getId(), pointerEvent.eventId());
        return createdTicket;
    }

    /**
     * Placeholder enrichment handler.
     *
     * <p>The current ticket model does not yet persist enrichment metadata, so the method logs the
     * information in a structured way and provides a single place to add persistence later.
     */
    public void handleEnrichmentEvent(EnrichmentEvent enrichmentEvent) {
        log.info(
                "Received enrichment event for source={} category={} severity={} confidence={} entities={}",
                enrichmentEvent.ticketSource(),
                enrichmentEvent.category(),
                enrichmentEvent.severity(),
                enrichmentEvent.confidence(),
                enrichmentEvent.entities());
    }

    private String buildPointerDescription(PointerEvent pointerEvent) {
        return "Pointer event received. payloadRef=%s, contentHash=%s, correlationId=%s"
                .formatted(pointerEvent.payloadRef(), pointerEvent.contentHash(), pointerEvent.correlationId());
    }
}
