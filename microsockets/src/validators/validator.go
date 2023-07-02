package validators

import (
	"fmt"
	"reflect"
	"strings"
	"unicode"

	"github.com/go-playground/validator"
)

type CustomValidator struct {
	validator *validator.Validate
}

type ValidationError struct {
	Namespace string `json:"namespace,omitempty"`
	Field     string `json:"field,omitempty"`
	Error     string `json:"error,omitempty"`
}

func (cv *CustomValidator) Validate(i interface{}) error {
	if err := cv.validator.Struct(i); err != nil {
		var errs []ValidationError
		for _, err := range err.(validator.ValidationErrors) {
			errs = append(errs, ValidationError{
				Namespace: err.Namespace(),
				Field:     err.Field(),
				Error:     fmt.Sprintf("%s - %s", err.Type(), err.Tag()),
			})
		}
		return fmt.Errorf("%v", errs)
	}
	return nil

}

func NewValidator() *CustomValidator {
	v := validator.New()
	v.RegisterTagNameFunc(func(fld reflect.StructField) string {
		name := strings.SplitN(fld.Tag.Get("json"), ",", 2)[0]
		if name == "-" {
			return ""
		}
		return name
	})
	return &CustomValidator{validator: v}
}

func firstCharUpper(fl validator.FieldLevel) bool {
	// get the value of the field
	name := fl.Field().String()
	// check if the first character is uppercase
	if !unicode.IsUpper([]rune(name)[0]) {
		// if it's not change it to uppercase
		fl.Field().SetString(strings.Title(name))
	}
	return true
}
