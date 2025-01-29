package main

import (
	"fmt"
	"log"
)

type Student struct {
	Login string
	Name     string
	Surname  string
	Password string
	Grades   []int
}

type Teacher struct {
	Login    string
	Password string
}

var allStudents = []Student{
	{Login: "joer123", Name: "Jeremy", Surname: "Scott", Password: "123", Grades: []int{}},
	{Login: "davy7", Name: "David", Surname: "Lin", Password: "321", Grades: []int{}},
}

func main() {
	fmt.Print("How do you want to log in?\n1. As Teacher\t 2. As Student\t 3. Exit\n")
	var choice string
	fmt.Scan(&choice)

	switch choice {
	case "3":
		log.Fatal("Exiting...")
	case "1":
		authTeacher()
		showStudentsList()

	case "2":
		if student := authStudent(); student != nil {
			handleStudentMenu(student)
		}
	}

}

func authStudent() *Student {
	fmt.Println("Type your Login:")
	var slogin string
	fmt.Scan(&slogin)

	fmt.Print("Type your Password:\n")
	var spassword string
	fmt.Scan(&spassword)

	for i := range allStudents {
		if allStudents[i].Login == slogin {
			if allStudents[i].Password == spassword {
				fmt.Printf("Welcome back, %s %s\n", allStudents[i].Name, allStudents[i].Surname)
				return &allStudents[i] 
			}
			log.Fatal("Wrong password")
		}
	}

	log.Fatal("Student not found")
	return nil
}

func handleStudentMenu(student *Student) {
	for {
		fmt.Print("\n1. View grades\n2. Exit\nChoose option: ")
		var choice string
		fmt.Scan(&choice)

		switch choice {
		case "1":
			showGradesList(student)
		case "2":
			return
		default:
			fmt.Println("Invalid choice")
		}
	}
}

func authTeacher() {
	teacher := []Teacher{
		{Login: "Delayla", Password: "T123"},
		{Login: "Margaret", Password: "T123"},
	}

	fmt.Print("Type your Login:\n")
		var login string
		fmt.Scan(&login)

		fmt.Print("Type your Password:\n")
		var password string
		fmt.Scan(&password)

		var foundTeacher *Teacher
		for i := range teacher {
			if teacher[i].Login == login {
				foundTeacher = &teacher[i]
				break
			}

		}

		if foundTeacher == nil {
			log.Fatal("Teacher not found")
		}

		if foundTeacher.Password != password {
			log.Fatal("Wrong password")
		}

		fmt.Printf("Welcome back, %s\n", foundTeacher.Login)
}

func showStudentsList() {
	fmt.Println("\nStudents list:")

	for i, student := range allStudents {
		fmt.Printf("%d. %s %s (Login: %s)\n", i+1, student.Name, student.Surname, student.Login)
	}
	fmt.Print("Enter student number to add grade:\n")
	var studentNum int
	_,err := fmt.Scan(&studentNum)
	if err != nil || studentNum < 1 || studentNum > len(allStudents) {
		log.Fatal("No students with this number")
	}

	selectedStudent := &allStudents[studentNum-1]
	fmt.Printf("Selected student: %s %s\n", selectedStudent.Name, selectedStudent.Surname)
	fmt.Print("Enter grade to add(2-5):\n")

	var grade int
	fmt.Scan(&grade)
	if grade < 2 || grade > 5 {
		log.Fatal("Invalid value")
	}

	selectedStudent.Grades = append(selectedStudent.Grades, grade)
	fmt.Println("Grade succesfully added!")
}

func showGradesList(student *Student) {
	if len(student.Grades) == 0 {
		fmt.Println("No grades yet")
	} else {

		fmt.Println("\nYour grades:")

		for _, grades := range student.Grades {
			fmt.Printf("%d\n", grades)
		}
	}
}