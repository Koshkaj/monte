package core

import (
	"log"
	"time"

	pbCoinflip "gitlab.com/montecsgo/microsockets/grpc/coinflip"
	pbRoulette "gitlab.com/montecsgo/microsockets/grpc/roulette"
	"google.golang.org/grpc"
)

type GRPC struct {
	conn     *grpc.ClientConn
	CoinFlip pbCoinflip.CoinflipClient
	Roulette pbRoulette.RouletteClient
}

func NewGRPC(address string) *GRPC {
	// Loops until connection is found, because we depend on it
	var conn *grpc.ClientConn
	var err error
	for conn == nil {
		conn, err = grpc.Dial(address, grpc.WithInsecure())
		if err != nil {
			log.Printf("Failed to connect: %v", err)
			time.Sleep(time.Second * 5)
		}
	}
	return &GRPC{
		conn:     conn,
		CoinFlip: pbCoinflip.NewCoinflipClient(conn),
		Roulette: pbRoulette.NewRouletteClient(conn),
	}
}

func (g *GRPC) Close() error {
	return g.conn.Close()
}
