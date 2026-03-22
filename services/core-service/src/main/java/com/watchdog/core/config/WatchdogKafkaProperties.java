package com.watchdog.core.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Kafka configuration owned by the core service.
 *
 * <p>Only a narrow subset of Kafka settings is modeled here because the immediate goal is to make the
 * topic contracts and consumer wiring explicit. More advanced settings can be added as the runtime
 * characteristics become clearer.
 */
@ConfigurationProperties(prefix = "watchdog.kafka")
public record WatchdogKafkaProperties(
        boolean enabled,
        String bootstrapServers,
        String consumerGroupId,
        Topics topics) {

    /**
     * Topic names used by the Prototype C event flow.
     */
    public record Topics(
            String pointerEvents,
            String enrichmentEvents,
            String deadLetterEvents) {
    }
}
