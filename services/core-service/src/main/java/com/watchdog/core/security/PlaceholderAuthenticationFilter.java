package com.watchdog.core.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import org.springframework.http.HttpHeaders;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * Development-only bearer token filter.
 *
 * <p>This filter exists to keep the service easy to boot before Supabase is fully wired everywhere.
 * It should not be the long-term production path.
 */
public final class PlaceholderAuthenticationFilter extends OncePerRequestFilter {

    private final String placeholderToken;

    public PlaceholderAuthenticationFilter(String placeholderToken) {
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
