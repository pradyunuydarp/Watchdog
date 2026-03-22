package com.watchdog.core.security;

import com.watchdog.core.config.WatchdogSecurityProperties;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.springframework.core.convert.converter.Converter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Component;

/**
 * Converts Supabase JWT claims into Spring Security authorities.
 *
 * <p>Supabase commonly nests role information under {@code app_metadata.roles}, so the converter walks a
 * configurable claim path instead of assuming a single flat claim name.
 */
@Component
public class SupabaseJwtAuthenticationConverter implements Converter<Jwt, AbstractAuthenticationToken> {

    private final WatchdogSecurityProperties securityProperties;

    public SupabaseJwtAuthenticationConverter(WatchdogSecurityProperties securityProperties) {
        this.securityProperties = securityProperties;
    }

    @Override
    public AbstractAuthenticationToken convert(Jwt jwt) {
        Collection<GrantedAuthority> authorities = new ArrayList<>();
        authorities.add(new SimpleGrantedAuthority("ROLE_AUTHENTICATED"));

        for (String role : resolveRoles(jwt)) {
            authorities.add(new SimpleGrantedAuthority("ROLE_" + role.toUpperCase().replace('-', '_')));
        }

        String principalName = jwt.getClaimAsString("email");
        if (principalName == null || principalName.isBlank()) {
            principalName = jwt.getSubject();
        }

        return new JwtAuthenticationToken(jwt, authorities, principalName);
    }

    /**
     * Reads a possibly nested roles claim using dotted-path syntax.
     */
    @SuppressWarnings("unchecked")
    private List<String> resolveRoles(Jwt jwt) {
        Object current = jwt.getClaims();
        String claimPath = securityProperties.supabase().roleClaimPath();

        if (claimPath == null || claimPath.isBlank()) {
            return List.of();
        }

        for (String segment : claimPath.split("\\.")) {
            if (!(current instanceof Map<?, ?> currentMap)) {
                return List.of();
            }
            current = currentMap.get(segment);
            if (current == null) {
                return List.of();
            }
        }

        if (current instanceof Collection<?> values) {
            return values.stream()
                    .filter(Objects::nonNull)
                    .map(Object::toString)
                    .toList();
        }

        if (current instanceof String value && !value.isBlank()) {
            return List.of(value);
        }

        return List.of();
    }
}
