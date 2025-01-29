package main

import (
	"fmt"
	"strings"
)

type Students struct {
	Name string
	Grades []int
}

func main() {
	students := []Students {
		{Name: "John", Grades: []int{3,4,2,5,5,5}},
		{Name: "Marry", Grades: []int{3,2,2,2,2,5}},
		{Name: "Harry", Grades: []int{3,4,4,4,5,5}},
		{Name: "Rose", Grades: []int{5,5,5,5,5,5}},
	}

	fmt.Print(students.filterTopStudents())

}





