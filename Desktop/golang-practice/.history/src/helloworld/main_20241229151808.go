package main

import (
	"fmt"
	"io/ioutil"
	"log"
)

func reverseString(input string) string {
	runes := []rune(input)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i] 
	}
	return string(runes)
}

func main() {
	filename := "file.txt"
	originalSentence := "Хакер в pеках!"

	err := ioutil.WriteFile(filename, []byte(originalSentence), 0644)
	if err != nil {
		log.Fatal("Error writing:", err)
		return
	}
	fmt.Println("Sentence written.")

	content, err := ioutil.ReadFile(filename)
	if err != nil {
		log.Fatal("Error reading:", err)
		return
	}
	fmt.Printf("Original sentence:%v", string(content))

	reversed := reverseString(string(content))
	fmt.Println("Reversed sentence:", reversed)
}

