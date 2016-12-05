package main

import (
	"os"

	"github.com/elastic/beats/libbeat/beat"

	"github.com/awormuth/amazonbeat/beater"
)

func main() {
	err := beat.Run("amazonbeat", "", beater.New)
	if err != nil {
		os.Exit(1)
	}
}
