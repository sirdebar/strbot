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

	average := students.findAvgGrade()

	res 
	fmt.Print(res)

}

func (s Students) findAvgGrade() float64 {
	sum := 0

	for _,grade := range s.Grades {
		sum += grade
	}

	if len(s.Grades) == 0 {
		return 0.0
	}

	return float64(sum) / float64(len(s.Grades))
}



