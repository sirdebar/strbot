package main

import (
	"fmt"
	"math/rand"
)

func main() {
	clientsMap := make(map[int]string)
	loadClients(clientsMap)

}

func loadClients(cm map[int]string) map[int]string {
	cm[1] = "Alex"
	cm[2] = "Sam"
	return cm
}
