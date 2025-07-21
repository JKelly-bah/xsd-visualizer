package com.example.bookstore;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/**
 * Main bookstore container
 * Generated from XSD schema
 */
public class Bookstoretype {
    private String storename;
    private String address;
    private List<Booktype> book;
    private String storeid;
    private LocalDate established;

    public Bookstoretype() {
    }

    public String getStorename() {
        return storename;
    }

    public void setStorename(String storename) {
        this.storename = storename;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public List<Booktype> getBook() {
        return book;
    }

    public void setBook(List<Booktype> book) {
        this.book = book;
    }

    public String getStoreid() {
        return storeid;
    }

    public void setStoreid(String storeid) {
        this.storeid = storeid;
    }

    public LocalDate getEstablished() {
        return established;
    }

    public void setEstablished(LocalDate established) {
        this.established = established;
    }

}