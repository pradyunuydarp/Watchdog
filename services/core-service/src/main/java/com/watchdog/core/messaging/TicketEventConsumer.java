package com.watchdog.core.messaging;

import com.watchdog.core.orchestration.TicketOrchestrationService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Kafka listeners for the core service.
 *
 * <p>Listeners are disabled by default in local-only starter mode. Once enabled, they receive Prototype C
 * pointer/enrichment events and delegate orchestration to a dedicated application service.
 */
@Component
@ConditionalOnProperty(prefix = "watchdog.kafka", name = "enabled", havingValue = "true")
public class TicketEventConsumer {

    private final KafkaEventParser kafkaEventParser;
    private final TicketOrchestrationService ticketOrchestrationService;

    public TicketEventConsumer(
            KafkaEventParser kafkaEventParser,
            TicketOrchestrationService ticketOrchestrationService) {
        this.kafkaEventParser = kafkaEventParser;
        this.ticketOrchestrationService = ticketOrchestrationService;
    }

    /**
     * Handles pointer events produced by the watcher service.
     */
    @KafkaListener(topics = "${watchdog.kafka.topics.pointer-events}", groupId = "${watchdog.kafka.consumer-group-id}")
    public void consumePointerEvent(String payload) {
        ticketOrchestrationService.handlePointerEvent(kafkaEventParser.parsePointerEvent(payload));
    }

    /**
     * Handles enrichment results produced by the NLP service.
     */
    @KafkaListener(topics = "${watchdog.kafka.topics.enrichment-events}", groupId = "${watchdog.kafka.consumer-group-id}")
    public void consumeEnrichmentEvent(String payload) {
        ticketOrchestrationService.handleEnrichmentEvent(kafkaEventParser.parseEnrichmentEvent(payload));
    }
}
