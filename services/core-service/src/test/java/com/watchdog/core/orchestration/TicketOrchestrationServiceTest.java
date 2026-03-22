package com.watchdog.core.orchestration;

import static org.assertj.core.api.Assertions.assertThat;

import com.watchdog.core.domain.Ticket;
import com.watchdog.core.messaging.event.PointerEvent;
import com.watchdog.core.repository.InMemoryTicketRepository;
import com.watchdog.core.service.TicketService;
import java.time.Instant;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the orchestration layer that converts Kafka pointer events into tickets.
 */
class TicketOrchestrationServiceTest {

    @Test
    void handlePointerEventCreatesReactiveTicketFromSourceMetadata() {
        InMemoryTicketRepository repository = new InMemoryTicketRepository();
        TicketService ticketService = new TicketService(repository);
        TicketOrchestrationService orchestrationService = new TicketOrchestrationService(ticketService);

        PointerEvent event = new PointerEvent(
                "evt-123",
                "corr-123",
                "payments",
                Instant.parse("2026-03-21T10:15:30Z"),
                "s3://bucket/raw-log.json",
                "sha256:abc123",
                Map.of("environment", "local"));

        Ticket created = orchestrationService.handlePointerEvent(event);

        assertThat(created.getSource()).isEqualTo("payments");
        assertThat(created.getTitle()).contains("payments");
        assertThat(created.getDescription()).contains("s3://bucket/raw-log.json");
        assertThat(repository.findAll()).hasSize(1);
    }
}
