package main

import "fmt"

type Student struct {
    Name   string
    Grades []int
}

func (s Student) AverageGrade() float64 {
    sum := 0
    for _, grade := range s.Grades {
        sum += grade
    }
    if len(s.Grades) == 0 {
        return 0.0
    }
    return float64(sum) / float64(len(s.Grades))
}

func filterTopStudents(students []Student) []string {
    var topStudents []string
    for _, s := range students {
        if s.AverageGrade() >= 4.5 {
            topStudents = append(topStudents, s.Name)
        }
    }
    return topStudents
}

func main() {
    students := []Student{
        {Name: "Alice", Grades: []int{5, 5, 5}},
        {Name: "Bob", Grades: []int{3, 4, 4}},
    }
    
    fmt.Println(filterTopStudents(students)) // [Alice]
}