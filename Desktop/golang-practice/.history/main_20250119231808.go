package main

import (
	"fmt"
)

func main() {

type employee struct {
	Name string
	Id int
}
 e := employee{Name: "John"}

fmt.Printf("Employee Name: %v, Id: %v", e.Name, e.Id)


}




