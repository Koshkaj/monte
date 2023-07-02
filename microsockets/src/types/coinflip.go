package types

type CoinflipCreateGameInput struct {
	BetAmount     uint32 `json:"bet_amount" validate:"required,gte=1"`
	Side          uint32 `json:"side" validate:"required,gt=0,lt=3"`
	SecurityToken string `json:"security_token" validate:"required"`
}

type CoinflipAcceptChallengeInput struct {
	RoundID       uint64 `json:"round_id" validate:"required"`
	SecurityToken string `json:"security_token" validate:"required"`
}

type CoinflipCancelGameInput struct {
	RoundID       uint64 `json:"round_id" validate:"required"`
	SecurityToken string `json:"security_token" validate:"required"`
}
