package com.watchdog.core.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.authentication.HttpStatusEntryPoint;
import org.springframework.web.filter.OncePerRequestFilter;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http, PlaceholderJwtAuthenticationFilter placeholderJwtAuthenticationFilter)
            throws Exception {
        return http
                .csrf(csrf -> csrf.disable())
                .httpBasic(httpBasic -> httpBasic.disable())
                .formLogin(formLogin -> formLogin.disable())
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .exceptionHandling(exceptionHandling -> exceptionHandling.authenticationEntryPoint(
                        new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED)))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/v1/health").permitAll()
                        .requestMatchers("/error").permitAll()
                        .anyRequest().authenticated())
                .addFilterBefore(placeholderJwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
                .build();
    }

    @Bean
    public PlaceholderJwtAuthenticationFilter placeholderJwtAuthenticationFilter(
            @Value("${watchdog.security.placeholder-token:dev-placeholder-token}") String placeholderToken) {
        return new PlaceholderJwtAuthenticationFilter(placeholderToken);
    }

    /**
     * Starter-only JWT hook.
     *
     * Replace this token check with real JWT validation, key discovery, issuer/audience enforcement,
     * and claim-to-authority mapping before exposing the service to a gateway or external client.
     */
    static final class PlaceholderJwtAuthenticationFilter extends OncePerRequestFilter {

        private final String placeholderToken;

        private PlaceholderJwtAuthenticationFilter(String placeholderToken) {
            this.placeholderToken = placeholderToken;
        }

        @Override
        protected boolean shouldNotFilter(HttpServletRequest request) {
            return "/api/v1/health".equals(request.getRequestURI());
        }

        @Override
        protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
                throws ServletException, IOException {
            if (SecurityContextHolder.getContext().getAuthentication() == null) {
                String authorization = request.getHeader(HttpHeaders.AUTHORIZATION);
                if (authorization != null && authorization.startsWith("Bearer ")) {
                    String token = authorization.substring("Bearer ".length()).trim();
                    if (placeholderToken.equals(token)) {
                        SecurityContextHolder.getContext().setAuthentication(
                                new UsernamePasswordAuthenticationToken(
                                        "watchdog-dev",
                                        token,
                                        List.of(new SimpleGrantedAuthority("ROLE_OPERATOR"))));
                    }
                }
            }

            filterChain.doFilter(request, response);
        }
    }
}
