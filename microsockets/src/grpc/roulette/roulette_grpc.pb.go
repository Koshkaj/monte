// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.2.0
// - protoc             v4.22.3
// source: src/proto/roulette.proto

package roulette

import (
	context "context"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.32.0 or later.
const _ = grpc.SupportPackageIsVersion7

// RouletteClient is the client API for Roulette service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type RouletteClient interface {
	PlaceBet(ctx context.Context, in *PlaceBetRequest, opts ...grpc.CallOption) (*StandardResponse, error)
	GetState(ctx context.Context, in *EmptyRequest, opts ...grpc.CallOption) (*StandardResponse, error)
}

type rouletteClient struct {
	cc grpc.ClientConnInterface
}

func NewRouletteClient(cc grpc.ClientConnInterface) RouletteClient {
	return &rouletteClient{cc}
}

func (c *rouletteClient) PlaceBet(ctx context.Context, in *PlaceBetRequest, opts ...grpc.CallOption) (*StandardResponse, error) {
	out := new(StandardResponse)
	err := c.cc.Invoke(ctx, "/roulette.Roulette/PlaceBet", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *rouletteClient) GetState(ctx context.Context, in *EmptyRequest, opts ...grpc.CallOption) (*StandardResponse, error) {
	out := new(StandardResponse)
	err := c.cc.Invoke(ctx, "/roulette.Roulette/GetState", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// RouletteServer is the server API for Roulette service.
// All implementations must embed UnimplementedRouletteServer
// for forward compatibility
type RouletteServer interface {
	PlaceBet(context.Context, *PlaceBetRequest) (*StandardResponse, error)
	GetState(context.Context, *EmptyRequest) (*StandardResponse, error)
	mustEmbedUnimplementedRouletteServer()
}

// UnimplementedRouletteServer must be embedded to have forward compatible implementations.
type UnimplementedRouletteServer struct {
}

func (UnimplementedRouletteServer) PlaceBet(context.Context, *PlaceBetRequest) (*StandardResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method PlaceBet not implemented")
}
func (UnimplementedRouletteServer) GetState(context.Context, *EmptyRequest) (*StandardResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetState not implemented")
}
func (UnimplementedRouletteServer) mustEmbedUnimplementedRouletteServer() {}

// UnsafeRouletteServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to RouletteServer will
// result in compilation errors.
type UnsafeRouletteServer interface {
	mustEmbedUnimplementedRouletteServer()
}

func RegisterRouletteServer(s grpc.ServiceRegistrar, srv RouletteServer) {
	s.RegisterService(&Roulette_ServiceDesc, srv)
}

func _Roulette_PlaceBet_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(PlaceBetRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(RouletteServer).PlaceBet(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/roulette.Roulette/PlaceBet",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(RouletteServer).PlaceBet(ctx, req.(*PlaceBetRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Roulette_GetState_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(EmptyRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(RouletteServer).GetState(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/roulette.Roulette/GetState",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(RouletteServer).GetState(ctx, req.(*EmptyRequest))
	}
	return interceptor(ctx, in, info, handler)
}

// Roulette_ServiceDesc is the grpc.ServiceDesc for Roulette service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var Roulette_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "roulette.Roulette",
	HandlerType: (*RouletteServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "PlaceBet",
			Handler:    _Roulette_PlaceBet_Handler,
		},
		{
			MethodName: "GetState",
			Handler:    _Roulette_GetState_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "src/proto/roulette.proto",
}
