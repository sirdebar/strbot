package main

import (
	"fmt"
	"math/rand"
)

func main() {
	slice := []int{}
	for i := 0; i < 20; i++ {
		index := rand.Intn(20)
		slice = append(slice, index)
	}

	fmt.Println("Generated slice:", slice)

	for _, value := range slice {
		if value % 2 == 0
	}
}
