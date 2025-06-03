package main

import (
	"fmt"
)

func main() {
	clientsMap := make(map[int]string)
	loadClients(clientsMap)

	fmt.Println("Enter your id to log in:")
	fmt.Print("> ")

	var clientId int
	fmt.Scanln(&clientId)
	_, exists := clientsMap[clientId]
	if exists {
		fmt.Printf("Great, the name of user with id %d is %v", clientId, clientsMap[clientId])
	} else {
		fmt.Println("The id not exists or user not find")
	}

}


