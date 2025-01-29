package main

import (
	"fmt"
	"strings"
)

type Student struct {
	Name string
	Grades []int
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

func filterTopStudents(students []Student) []string {
	var topStudents []string

	for _, student := range students {
		if student.findAvgGrade() >= 4.5 {
			topStudents = append(topStudents, student.Name)
		}
	}
	return topStudents

}

func main() {
	students := []Student {
		{Name: "John", Grades: []int{3,4,2,5,5,5}},
		{Name: "Marry", Grades: []int{3,2,2,2,2,5}},
		{Name: "Harry", Grades: []int{3,4,4,4,5,5}},
		{Name: "Rose", Grades: []int{5,5,5,5,5,5}},
	}

	fmt.Print(students.filterTopStudents())

}





