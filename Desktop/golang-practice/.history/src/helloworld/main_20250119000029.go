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

func loadClients(c *map[int]string) {
	clientsBase[1] = "Alex"
	clientsBase[2] = "Sam"
}
