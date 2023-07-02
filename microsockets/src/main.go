package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"gitlab.com/montecsgo/microsockets/api"
)

func main() {
	s := api.InitServer()
	go func() {
		if err := s.Start(":8080"); err != nil && err != http.ErrServerClosed {
			s.Logger.Fatal("shutting down the server")
		}
	}()
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM, syscall.SIGKILL)
	<-sigChan
	shutdownCtx, shutdownRelease := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownRelease()
	if err := s.ShutServerDown(shutdownCtx); err != nil {
		s.Logger.Fatalf("HTTP shutdown error: %v", err)
	}
	s.Logger.Fatal("Graceful shutdown complete.")

}
