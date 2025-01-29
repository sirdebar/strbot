package main

import (
    "encoding/json"
    "fmt"
)

type Person struct {
    ID        int
    FirstName string `json:"name"`
    LastName  string
    Address   string `json:"address,omitempty"`
}

type Employee struct {
    Person
    ManagerID int
}

type Contractor struct {
    Person
    CompanyID int
}

func main() {
type Rectangle struct {
    width  float64
    height float64
}

// Метод Area для структуры Rectangle
func (r Rectangle) Area() float64 {
    return r.width * r.height
}

// Использование:
rect := Rectangle{width: 10, height: 5}
area := rect.Area() // вызываем как метод
}