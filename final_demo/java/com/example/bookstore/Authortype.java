package com.example.bookstore;

/**
 * Author information
 * Generated from XSD schema
 */
public class Authortype {
    private String firstname;
    private String lastname;
    private int birthyear;
    private String biography;
    private Id authorid;

    public Authortype() {
    }

    public String getFirstname() {
        return firstname;
    }

    public void setFirstname(String firstname) {
        this.firstname = firstname;
    }

    public String getLastname() {
        return lastname;
    }

    public void setLastname(String lastname) {
        this.lastname = lastname;
    }

    public int getBirthyear() {
        return birthyear;
    }

    public void setBirthyear(int birthyear) {
        this.birthyear = birthyear;
    }

    public String getBiography() {
        return biography;
    }

    public void setBiography(String biography) {
        this.biography = biography;
    }

    public Id getAuthorid() {
        return authorid;
    }

    public void setAuthorid(Id authorid) {
        this.authorid = authorid;
    }

}