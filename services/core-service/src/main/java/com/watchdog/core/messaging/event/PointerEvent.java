package com.watchdog.core.messaging.event;

import java.time.Instant;
import java.util.Map;

/**
 * Pointer event emitted by the watcher service in Prototype C.
 *
 * <p>The event contains metadata plus a reference to the raw payload location. The core service does not
 * need the full raw log body to open a placeholder/reactive ticket, which keeps Kafka messages small and
 * cheap to replay.
 */
public record PointerEvent(
        String eventId,
        String correlationId,
        String source,
        Instant occurredAt,
        String payloadRef,
        String contentHash,
        Map<String, String> attributes) {
}
