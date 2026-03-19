package com.nuydarp.lil.landon_hotel.data.entity;

import jakarta.persistence.*;
import jdk.jfr.DataAmount;
import lombok.Data;
import lombok.ToString;

@Entity

@Table(name="rooms")
@Data
@ToString

public class Room {
    @Id
    @Column(name="room_id")
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;
    @Column(name="name")
    private String name;
    @Column(name="room_number", unique = true)
    private String roomNumber;
    @Column(name="bed_info")
    private String bedInfo;
}
