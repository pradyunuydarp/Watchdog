package com.watchdog.core.messaging.event;

import java.util.List;
import java.util.Map;

/**
 * Representation of the enrichment event consumed from Kafka.
 *
 * <p>The structure mirrors the logical contract documented in the architecture work. It is intentionally
 * lightweight so the service can evolve even before protobuf-generated Java types are introduced.
 */
public record EnrichmentEvent(
        String eventId,
        String correlationId,
        String ticketSource,
        String category,
        String severity,
        double confidence,
        List<String> entities,
        Map<String, String> attributes) {
}
