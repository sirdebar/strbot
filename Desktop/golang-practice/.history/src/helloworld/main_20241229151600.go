package main

import (
	"fmt"
	"os"
	"io/ioutil"
	"log"
)

func reverseString(content) {

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

	reversed := 
}

