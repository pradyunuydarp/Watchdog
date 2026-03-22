package com.watchdog.core;

import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.EnableKafka;

@SpringBootApplication
@ConfigurationPropertiesScan
@EnableKafka
public class WatchdogCoreApplication {

    public static void main(String[] args) {
        SpringApplication.run(WatchdogCoreApplication.class, args);
    }
}
