package main

import (
    "encoding/json"
    "fmt"
)

type Person struct {
    ID        int
    FirstName string `json:"name"`
    LastName  string
    Address   string `json:"-"`
}

type Employee struct {
    Person
    ManagerID int
}


func main() {

}