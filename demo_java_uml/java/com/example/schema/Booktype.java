package com.example.schema;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Book information
 * Generated from XSD schema
 */
public class Booktype {
    private String title;
    private List<Authortype> author;
    private Isbntype isbn;
    private int publishedyear;
    private Categorytype category;
    private BigDecimal price;
    private String description;
    private boolean instock;
    private Id bookid;
    private int edition;

    public Booktype() {
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public List<Authortype> getAuthor() {
        return author;
    }

    public void setAuthor(List<Authortype> author) {
        this.author = author;
    }

    public Isbntype getIsbn() {
        return isbn;
    }

    public void setIsbn(Isbntype isbn) {
        this.isbn = isbn;
    }

    public int getPublishedyear() {
        return publishedyear;
    }

    public void setPublishedyear(int publishedyear) {
        this.publishedyear = publishedyear;
    }

    public Categorytype getCategory() {
        return category;
    }

    public void setCategory(Categorytype category) {
        this.category = category;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public void setPrice(BigDecimal price) {
        this.price = price;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public boolean getInstock() {
        return instock;
    }

    public void setInstock(boolean instock) {
        this.instock = instock;
    }

    public Id getBookid() {
        return bookid;
    }

    public void setBookid(Id bookid) {
        this.bookid = bookid;
    }

    public int getEdition() {
        return edition;
    }

    public void setEdition(int edition) {
        this.edition = edition;
    }

}