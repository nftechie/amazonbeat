package beater

import (
	"fmt"
	"time"
	"os"
	"os/exec"
	"path/filepath"
	"encoding/json"
	"io/ioutil"

	"github.com/elastic/beats/libbeat/beat"
	"github.com/elastic/beats/libbeat/common"
	"github.com/elastic/beats/libbeat/logp"
	"github.com/elastic/beats/libbeat/publisher"

	"github.com/awormuth/amazonbeat/config"
)

type Amazonbeat struct {
	done   chan struct{}
	config config.Config
	client publisher.Client
}

type ProductData struct {
	Name string `json:"product"`
	SalePrice string `json:"salePrice"`
	OriginalPrice string `json:"originalPrice"`
	URL string `json:"url"`
	NumReviews string `json:"numReviews"`
	Rating string `json:"rating"`
}

// Creates beater
func New(b *beat.Beat, cfg *common.Config) (beat.Beater, error) {
	config := config.DefaultConfig
	if err := cfg.Unpack(&config); err != nil {
		return nil, fmt.Errorf("Error reading config file: %v", err)
	}

	bt := &Amazonbeat{
		done: make(chan struct{}),
		config: config,
	}
	return bt, nil
}

func (bt *Amazonbeat) readAmazonData(asin string) (ProductData, error) {
	productData := ProductData{}

	// Get filepath for currently running script.
	dir, err := filepath.Abs(filepath.Dir(os.Args[0]))
	if err != nil { 
		return productData, err 
	}

	// Execute python script that pulls amazon product data.
	cmd := exec.Command("python", dir + "/readAmazonData.py", asin)
	err = cmd.Run()
	if err != nil { 
		return productData, err 
	}

	// Read data.json file into ProductData struct.
	raw, err := ioutil.ReadFile(dir + "/data.json")
	if err != nil {
		return productData, err 
	}

	err = json.Unmarshal(raw, &productData)
	if err != nil {
		return productData, err
	}

    return productData, nil
}

func (bt *Amazonbeat) Run(b *beat.Beat) error {
	logp.Info("amazonbeat is running! Hit CTRL-C to stop it.")

	bt.client = b.Publisher.Connect()
	ticker := time.NewTicker(bt.config.Period)
	for {
		select {
		case <-bt.done:
			return nil
		case <-ticker.C:
		}

		now := time.Now()
		productData, err := bt.readAmazonData(bt.config.ASIN)
		if err != nil {
			fmt.Println(err)
			return nil
		}

		event := common.MapStr{
			"@timestamp":    common.Time(now),
			"type":          b.Name,
			"product":       productData.Name,
			"saleprice":     productData.SalePrice,
			"originalprice": productData.OriginalPrice,
			"url":           productData.URL,
			"numreviews":    productData.NumReviews,
			"rating":        productData.Rating,
		}
		fmt.Println(event)

		// TODO: Properly export this data to ElasticSearch.
		// bt.client.PublishEvent(event)
		// logp.Info("Event sent")

		// BUG: When the above code executes, elasticsearch throws the following error:
		// org.elasticsearch.index.mapper.MapperParsingException: failed to parse [numreviews]
		// Caused by: java.lang.NumberFormatException: For input string: "2,511"
		// at java.lang.NumberFormatException.forInputString(NumberFormatException.java:65) ~[?:1.8.0_111]
	}
}

func (bt *Amazonbeat) Stop() {
	bt.client.Close()
	close(bt.done)
}
