package com.watchdog.core.persistence;

import com.watchdog.core.domain.Ticket;
import com.watchdog.core.repository.TicketRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

/**
 * PostgreSQL-backed implementation of the application repository abstraction.
 *
 * <p>The adapter pattern keeps JPA details out of the service layer and makes it straightforward to swap
 * persistence strategies per Spring profile.
 */
@Component
@Profile("postgres")
public class JpaTicketRepositoryAdapter implements TicketRepository {

    private final SpringDataTicketRepository springDataTicketRepository;
    private final TicketPersistenceMapper ticketPersistenceMapper;

    public JpaTicketRepositoryAdapter(
            SpringDataTicketRepository springDataTicketRepository,
            TicketPersistenceMapper ticketPersistenceMapper) {
        this.springDataTicketRepository = springDataTicketRepository;
        this.ticketPersistenceMapper = ticketPersistenceMapper;
    }

    @Override
    public Ticket save(Ticket ticket) {
        TicketEntity entity = ticketPersistenceMapper.toEntity(ticket);
        TicketEntity saved = springDataTicketRepository.save(entity);
        return ticketPersistenceMapper.toDomain(saved);
    }

    @Override
    public Optional<Ticket> findById(UUID id) {
        return springDataTicketRepository.findById(id).map(ticketPersistenceMapper::toDomain);
    }

    @Override
    public List<Ticket> findAll() {
        return springDataTicketRepository.findAll().stream()
                .map(ticketPersistenceMapper::toDomain)
                .sorted((left, right) -> right.getCreatedAt().compareTo(left.getCreatedAt()))
                .toList();
    }
}
