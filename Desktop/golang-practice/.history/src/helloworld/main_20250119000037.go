package main

import (
	"fmt"
	"math/rand"
)

func main() {
	clientsMap := make(map[int]string)
	clientsBase := &clientsMap
	loadClients(clientsBase)


}

func loadClients(cb *map[int]string) {
	cb[1] = "Alex"
	cb[2] = "Sam"
}
