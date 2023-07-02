package types

type PlaceBetRouletteInput struct {
	Coin    string `json:"coin" validate:"required,oneof=ct t zero"`
	RoundID uint64 `json:"round_id" validate:"required,gt=0"`
	Amount  uint32 `json:"amount" validate:"required,gte=1"`
	Token   string `json:"token" validate:"required"`
}
