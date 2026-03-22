package com.watchdog.core.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Externalized security configuration for the core service.
 *
 * <p>The finalized architecture uses Supabase as the auth provider, but local development still benefits
 * from a placeholder mode that avoids requiring the full auth stack during early scaffolding.
 */
@ConfigurationProperties(prefix = "watchdog.security")
public record WatchdogSecurityProperties(
        SecurityMode mode,
        String placeholderToken,
        SupabaseJwtProperties supabase) {

    /**
     * Supported security modes for the starter.
     */
    public enum SecurityMode {
        PLACEHOLDER,
        SUPABASE
    }

    /**
     * Supabase-specific JWT verification settings.
     */
    public record SupabaseJwtProperties(
            String issuerUri,
            String jwkSetUri,
            String sharedSecret,
            String roleClaimPath,
            String expectedAudience) {
    }
}
