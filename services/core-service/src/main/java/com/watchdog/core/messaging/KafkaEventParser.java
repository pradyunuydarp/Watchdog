package com.watchdog.core.messaging;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.watchdog.core.messaging.event.EnrichmentEvent;
import com.watchdog.core.messaging.event.PointerEvent;
import org.springframework.stereotype.Component;

/**
 * Converts raw Kafka payloads into typed event records.
 *
 * <p>The listeners intentionally consume strings first. That keeps the scaffolding resilient while topic
 * contracts are still being finalized and avoids coupling the consumer to Kafka-specific serializer setup.
 */
@Component
public class KafkaEventParser {

    private final ObjectMapper objectMapper;

    public KafkaEventParser(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public PointerEvent parsePointerEvent(String payload) {
        return parse(payload, PointerEvent.class);
    }

    public EnrichmentEvent parseEnrichmentEvent(String payload) {
        return parse(payload, EnrichmentEvent.class);
    }

    private <T> T parse(String payload, Class<T> type) {
        try {
            return objectMapper.readValue(payload, type);
        } catch (JsonProcessingException exception) {
            throw new IllegalArgumentException("Failed to parse Kafka payload into " + type.getSimpleName(), exception);
        }
    }
}
