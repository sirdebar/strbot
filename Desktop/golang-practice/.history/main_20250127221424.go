package main

import (
	"fmt"

)

type Student struct {
	Name string
	Grades []int
}

func (s Student) findAvgGrade() float64 {
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
=
}





