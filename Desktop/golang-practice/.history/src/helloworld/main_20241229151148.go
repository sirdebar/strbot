package main

import (
	"fmt"
	"os"
	"io/ioutil"
	"log"
)



func main() {
	filename := "file.txt"
	originalSentence := "Хакер в pеках!"

	err := ioutil.WriteFile(filename, []byte(originalSentence), 0644)
	if err != nil {
		log.Fatal("Error writing:", err)
		return
	}
	log.Default("")
}

