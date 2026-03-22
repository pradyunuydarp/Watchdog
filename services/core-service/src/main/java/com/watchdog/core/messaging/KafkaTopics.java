package com.watchdog.core.messaging;

import com.watchdog.core.config.WatchdogKafkaProperties;
import org.springframework.stereotype.Component;

/**
 * Small wrapper around configured topic names.
 *
 * <p>Using a dedicated component keeps topic lookup centralized and prevents string duplication across
 * listeners, dead-letter handling, and eventual producers.
 */
@Component
public class KafkaTopics {

    private final WatchdogKafkaProperties kafkaProperties;

    public KafkaTopics(WatchdogKafkaProperties kafkaProperties) {
        this.kafkaProperties = kafkaProperties;
    }

    public String pointerEvents() {
        return kafkaProperties.topics().pointerEvents();
    }

    public String enrichmentEvents() {
        return kafkaProperties.topics().enrichmentEvents();
    }

    public String deadLetterEvents() {
        return kafkaProperties.topics().deadLetterEvents();
    }
}
