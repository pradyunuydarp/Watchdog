package com.watchdog.core.web;

import com.watchdog.core.service.TicketNotFoundException;
import java.net.URI;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(TicketNotFoundException.class)
    ProblemDetail handleTicketNotFound(TicketNotFoundException exception) {
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, exception.getMessage());
        problemDetail.setType(URI.create("https://watchdog.local/problems/ticket-not-found"));
        problemDetail.setTitle("Ticket not found");
        return problemDetail;
    }

    @ExceptionHandler(IllegalArgumentException.class)
    ProblemDetail handleIllegalArgument(IllegalArgumentException exception) {
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, exception.getMessage());
        problemDetail.setType(URI.create("https://watchdog.local/problems/bad-request"));
        problemDetail.setTitle("Bad request");
        return problemDetail;
    }
}
