package main

import (
	"fmt"
)


func main() {
	arr := [10][10]int{}
	for i := 0; i < 3; i++ {
		for j := 0; j < 5; j++ {
			arr[i][j] = (i +1) * (j + 1)
		}
		fmt.Printf("Row %v: %v", i, arr[i]\n)
	}
}

