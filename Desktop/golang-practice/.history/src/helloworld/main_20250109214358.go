package main

import "fmt"

func main() {
	slice := make([]int, 10)
	for i := 0; i < 10; i++ {
		slice = append(slice, i)
		fmt.Println("Actual slice:", slice)
	}
	fmt.Println("Final slice:", slice)
}
