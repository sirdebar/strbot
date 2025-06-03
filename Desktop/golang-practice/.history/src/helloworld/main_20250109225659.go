package main

import (
	"fmt"
)

func main() {
	arr := [5]int{1,2,3,4,5}
	slice := arr[54]
	newSlice := append(slice, 6)
	fmt.Println(newSlice)
}
