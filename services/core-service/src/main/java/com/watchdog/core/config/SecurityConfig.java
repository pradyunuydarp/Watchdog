package com.watchdog.core.config;

import com.watchdog.core.security.PlaceholderAuthenticationFilter;
import com.watchdog.core.security.SupabaseJwtAuthenticationConverter;
import java.nio.charset.StandardCharsets;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtDecoders;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.authentication.HttpStatusEntryPoint;

/**
 * Central security configuration for the core service.
 *
 * <p>The service currently supports two operating modes:
 *
 * <ul>
 *     <li>{@code PLACEHOLDER}: a local-development shortcut that accepts a single configured bearer token.</li>
 *     <li>{@code SUPABASE}: validates JWTs using either a shared secret, a JWK set URI, or an issuer URI.</li>
 * </ul>
 *
 * <p>This class is deliberately explicit because authentication is one of the first areas that gets
 * revisited when a system moves from a scaffold into a real environment. Keeping the branching logic
 * here makes that transition easier to audit and evolve.
 */
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http,
            WatchdogSecurityProperties securityProperties,
            PlaceholderAuthenticationFilter placeholderAuthenticationFilter,
            SupabaseJwtAuthenticationConverter supabaseJwtAuthenticationConverter)
            throws Exception {
        HttpSecurity configured = http
                .csrf(csrf -> csrf.disable())
                .httpBasic(httpBasic -> httpBasic.disable())
                .formLogin(formLogin -> formLogin.disable())
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .exceptionHandling(exceptionHandling -> exceptionHandling.authenticationEntryPoint(
                        new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED)))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/v1/health").permitAll()
                        .requestMatchers("/error").permitAll()
                        .anyRequest().authenticated());

        if (securityProperties.mode() == WatchdogSecurityProperties.SecurityMode.PLACEHOLDER) {
            configured.addFilterBefore(placeholderAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
        } else {
            configured.oauth2ResourceServer(oauth2 -> oauth2
                    .jwt(jwt -> jwt.jwtAuthenticationConverter(supabaseJwtAuthenticationConverter)));
        }

        return configured.build();
    }

    @Bean
    public PlaceholderAuthenticationFilter placeholderAuthenticationFilter(WatchdogSecurityProperties securityProperties) {
        return new PlaceholderAuthenticationFilter(securityProperties.placeholderToken());
    }

    /**
     * Creates the JWT decoder used in Supabase mode.
     *
     * <p>The method supports three common development/production setups:
     *
     * <ol>
     *     <li>Local Supabase using an HS256 shared secret.</li>
     *     <li>A fixed JWK set endpoint.</li>
     *     <li>Issuer-based discovery for fully managed deployments.</li>
     * </ol>
     */
    @Bean
    public JwtDecoder jwtDecoder(WatchdogSecurityProperties securityProperties) {
        WatchdogSecurityProperties.SupabaseJwtProperties supabase = securityProperties.supabase();

        if (securityProperties.mode() == WatchdogSecurityProperties.SecurityMode.PLACEHOLDER) {
            return token -> {
                throw new IllegalStateException("JwtDecoder should not be used while placeholder security mode is active.");
            };
        }

        if (supabase.sharedSecret() != null && !supabase.sharedSecret().isBlank()) {
            return NimbusJwtDecoder.withSecretKey(
                            new SecretKeySpec(supabase.sharedSecret().getBytes(StandardCharsets.UTF_8), "HmacSHA256"))
                    .macAlgorithm(MacAlgorithm.HS256)
                    .build();
        }

        if (supabase.jwkSetUri() != null && !supabase.jwkSetUri().isBlank()) {
            return NimbusJwtDecoder.withJwkSetUri(supabase.jwkSetUri()).build();
        }

        if (supabase.issuerUri() != null && !supabase.issuerUri().isBlank()) {
            return JwtDecoders.fromIssuerLocation(supabase.issuerUri());
        }

        throw new IllegalStateException(
                "Supabase security mode requires watchdog.security.supabase.shared-secret, "
                        + "watchdog.security.supabase.jwk-set-uri, or watchdog.security.supabase.issuer-uri.");
    }
}
