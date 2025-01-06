// api/client.go
package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"
	"water-vending/models"
)

// Client menangani semua komunikasi dengan backend
type Client struct {
	config     models.APIConfig
	httpClient *http.Client
}

// NewClient membuat instance baru dari API Client
func NewClient(config models.APIConfig) *Client {
	return &Client{
		config: config,
		httpClient: &http.Client{
			Timeout: time.Duration(config.Timeout) * time.Second,
		},
	}
}

// makeRequest melakukan HTTP request dengan mekanisme retry
func (c *Client) makeRequest(method, endpoint string, data interface{}) ([]byte, error) {
	url := fmt.Sprintf("%s/api/%s", c.config.BaseURL, endpoint)
	
	var jsonData []byte
	var err error
	if data != nil {
		jsonData, err = json.Marshal(data)
		if err != nil {
			return nil, fmt.Errorf("error marshaling data: %v", err)
		}
	}

	for attempt := 0; attempt < c.config.RetryAttempts; attempt++ {
		var req *http.Request
		if data != nil {
			req, err = http.NewRequest(method, url, bytes.NewBuffer(jsonData))
		} else {
			req, err = http.NewRequest(method, url, nil)
		}
		if err != nil {
			return nil, err
		}

		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Accept", "application/json")

		resp, err := c.httpClient.Do(req)
		if err != nil {
			log.Printf("Request failed (attempt %d/%d): %v", 
				attempt+1, c.config.RetryAttempts, err)
			if attempt < c.config.RetryAttempts-1 {
				time.Sleep(time.Duration(c.config.RetryDelay) * time.Second)
				continue
			}
			return nil, err
		}
		defer resp.Body.Close()

		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			return nil, err
		}

		if resp.StatusCode >= 200 && resp.StatusCode < 300 {
			return body, nil
		}

		log.Printf("Request failed with status %d (attempt %d/%d)", 
			resp.StatusCode, attempt+1, c.config.RetryAttempts)
		
		if attempt < c.config.RetryAttempts-1 {
			time.Sleep(time.Duration(c.config.RetryDelay) * time.Second)
			continue
		}
	}

	return nil, fmt.Errorf("request failed after %d attempts", c.config.RetryAttempts)
}

// RecordQuality mencatat data kualitas air
func (c *Client) RecordQuality(qualityData map[string]float64) error {
	endpoint := fmt.Sprintf("machines/%s/record_quality/", c.config.MachineID)
	_, err := c.makeRequest("POST", endpoint,