package api

import (
	"fmt"
	"io"
	"net/http"

	"github.com/google/uuid"
	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
	"github.com/redis/go-redis/v9"
	"gitlab.com/montecsgo/microsockets/core"
	"gitlab.com/montecsgo/microsockets/validators"
	"go.uber.org/multierr"
	"golang.org/x/net/context"
)

type Config struct {
	secretKey string
}

func NewConfig() *Config {
	return &Config{
		secretKey: "temporary-secret-key",
	}

}

type Server struct {
	*echo.Echo
	Config *Config
	Redis  *redis.Client
	gRPC   *core.GRPC
}

func (s *Server) addServerConnection(ctx context.Context, connection uuid.UUID, ip string) error {
	tx := s.Redis.TxPipeline()
	tx.Set(ctx, fmt.Sprintf("connection:%v", connection.String()), ip, 0)
	_, err := tx.Exec(ctx)
	if err != nil {
		return err
	}
	return nil
}

func (s *Server) removeServerConnection(ctx context.Context, connection uuid.UUID) error {
	tx := s.Redis.TxPipeline()
	tx.Decr(ctx, "connection_count")
	tx.Del(ctx, fmt.Sprintf("connection:%v", connection.String()))
	_, err := tx.Exec(ctx)
	if err != nil {
		return err
	}
	return nil

}

func (s *Server) isServerConnectionOnline(ctx context.Context, connection uuid.UUID) bool {
	connectionKey := fmt.Sprintf("connection:%v", connection.String())
	_, err := s.Redis.Exists(ctx, connectionKey).Result()
	if err != nil {
		return false
	}
	return true
}

func (s *Server) ShutServerDown(ctx context.Context) error {
	var err error
	resources := []io.Closer{s.gRPC, s.Redis}
	// redis garbage collect before we close
	tx := s.Redis.Pipeline()
	iter := tx.Scan(ctx, 0, "connection:*", 0).Iterator()
	for iter.Next(ctx) {
		tx.Del(ctx, iter.Val())
	}
	tx.Set(ctx, "connection_count", 0, 0)
	_, err = tx.Exec(ctx)
	if err != nil {
		return err
	}
	if cerr := iter.Err(); cerr != nil {
		err = multierr.Append(err, cerr)
	}

	for _, r := range resources {
		if r != nil {
			if cerr := r.Close(); cerr != nil {
				err = multierr.Append(err, cerr)
			}
		}
	}
	if cerr := s.Echo.Shutdown(ctx); cerr != nil {
		err = multierr.Append(err, cerr)
	}
	return err
}

func (s *Server) countServerConnections(ctx context.Context) (int64, error) {
	count, err := s.Redis.PubSubNumSub(ctx, "monte-server").Result()
	if err != nil {
		return 0, err
	}
	return int64(count["monte-server"]), nil
}

func NewServer(e *echo.Echo, c *Config, r *redis.Client, rpc *core.GRPC) *Server {
	return &Server{
		Config: c,
		Echo:   e,
		Redis:  r,
		gRPC:   rpc,
	}
}

func (s *Server) handlePing(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]string{"status": "healthy"})
}

func InitServer() *Server {
	serverConfig := NewConfig()
	e := echo.New()
	e.Validator = validators.NewValidator()
	e.Use(
		middleware.Logger(),
		// middleware.Recover(),
		middleware.RequestID(),
	)
	client := redis.NewClient(
		&redis.Options{
			Addr: "redis_ecp:6379",
			DB:   0,
		},
	)
	grpcConnection := core.NewGRPC("games:50051")

	s := NewServer(e, serverConfig, client, grpcConnection)

	indexGroup := e.Group("/")
	{
		indexGroup.Add("GET", "ws", s.handleRCWebsocket)
		indexGroup.Add("GET", "", s.handlePing)
	}
	return s

}
