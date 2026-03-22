package com.watchdog.core.security;

import static org.assertj.core.api.Assertions.assertThat;

import com.watchdog.core.config.WatchdogSecurityProperties;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;

/**
 * Verifies the converter's handling of nested Supabase role claims.
 */
class SupabaseJwtAuthenticationConverterTest {

    @Test
    void convertMapsNestedAppMetadataRolesIntoSpringAuthorities() {
        WatchdogSecurityProperties properties = new WatchdogSecurityProperties(
                WatchdogSecurityProperties.SecurityMode.SUPABASE,
                "ignored",
                new WatchdogSecurityProperties.SupabaseJwtProperties(
                        "http://localhost:54321/auth/v1",
                        "",
                        "secret",
                        "app_metadata.roles",
                        "authenticated"));

        SupabaseJwtAuthenticationConverter converter = new SupabaseJwtAuthenticationConverter(properties);

        Jwt jwt = new Jwt(
                "token",
                Instant.now(),
                Instant.now().plusSeconds(600),
                Map.of("alg", "HS256"),
                Map.of(
                        "sub", "user-123",
                        "email", "operator@example.com",
                        "app_metadata", Map.of("roles", List.of("operator", "admin"))));

        JwtAuthenticationToken authentication = (JwtAuthenticationToken) converter.convert(jwt);

        assertThat(authentication.getName()).isEqualTo("operator@example.com");
        assertThat(authentication.getAuthorities())
                .extracting(Object::toString)
                .contains("ROLE_OPERATOR", "ROLE_ADMIN", "ROLE_AUTHENTICATED");
    }
}
