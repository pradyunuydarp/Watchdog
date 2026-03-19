package com.nuydarp.lil.landon_hotel;

import com.nuydarp.lil.landon_hotel.data.entity.Room;
import com.nuydarp.lil.landon_hotel.data.repository.RoomRepository;
import lombok.NonNull;
import org.springframework.boot.CommandLineRunner;

import java.util.List;
import java.util.Optional;

public class CLRunner implements CommandLineRunner {
    private final RoomRepository roomRepository;
    public CLRunner(RoomRepository roomRepository) {
        this.roomRepository = roomRepository;
    }

    @Override
    public void run(String @NonNull ... args) throws Exception {
        List<Room> rooms = this.roomRepository.findAll();
        Optional<Room> room = this.roomRepository.findByRoomNumberIgnoreCase("p1");
        System.out.println(room);
        rooms.forEach(System.out::println);
    }
}
