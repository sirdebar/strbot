package main

import (
	"fmt"
	"math/rand"
)

func main() {
	clientsMap := make(map[int]string)
	loadClients(clientsMap)

	fmt.Println("Enter your id to log in:")
	fmt.Print(">")

	var clientId int
	fmt.Scanln(&clientId)
	value, exists := clientsMap[clientId]
	if exists {
		fmt.Printf("Great, the name of user  ")
	}

}

func loadClients(cm map[int]string) map[int]string {
	cm[1] = "Alex"
	cm[2] = "Sam"
	return cm
}
