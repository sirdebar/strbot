package main

import (
	"fmt"
)

func main() {

type employee struct {
	Name string
	Id int
}
 e := employee{Id: 1}

fmt.Printf("Employee Name: %v, Id: %v", e.Name, e.Id)


}




