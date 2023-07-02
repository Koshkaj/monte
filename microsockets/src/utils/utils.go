package utils

import "encoding/json"

func Remarshal(i any, j any) error {
	var err error
	byteData, err := json.Marshal(i)
	err = json.Unmarshal(byteData, j)

	return err

}
