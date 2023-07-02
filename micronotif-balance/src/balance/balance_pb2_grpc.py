# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import balance_pb2 as balance__pb2


class BalanceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ConfirmBet = channel.unary_unary(
                '/balance.Balance/ConfirmBet',
                request_serializer=balance__pb2.ConfirmBetRequest.SerializeToString,
                response_deserializer=balance__pb2.ConfirmBetResponse.FromString,
                )
        self.CommitBettersBalance = channel.unary_unary(
                '/balance.Balance/CommitBettersBalance',
                request_serializer=balance__pb2.CommitBettersBalanceRequest.SerializeToString,
                response_deserializer=balance__pb2.CommitBettersBalanceResponse.FromString,
                )
        self.ValidateToken = channel.unary_unary(
                '/balance.Balance/ValidateToken',
                request_serializer=balance__pb2.TokenValidateRequest.SerializeToString,
                response_deserializer=balance__pb2.StandardResponse.FromString,
                )
        self.CommitBettersCoinflip = channel.unary_unary(
                '/balance.Balance/CommitBettersCoinflip',
                request_serializer=balance__pb2.CommitBettersCoinflipRequest.SerializeToString,
                response_deserializer=balance__pb2.CommitBettersBalanceResponse.FromString,
                )


class BalanceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ConfirmBet(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CommitBettersBalance(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ValidateToken(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CommitBettersCoinflip(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BalanceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ConfirmBet': grpc.unary_unary_rpc_method_handler(
                    servicer.ConfirmBet,
                    request_deserializer=balance__pb2.ConfirmBetRequest.FromString,
                    response_serializer=balance__pb2.ConfirmBetResponse.SerializeToString,
            ),
            'CommitBettersBalance': grpc.unary_unary_rpc_method_handler(
                    servicer.CommitBettersBalance,
                    request_deserializer=balance__pb2.CommitBettersBalanceRequest.FromString,
                    response_serializer=balance__pb2.CommitBettersBalanceResponse.SerializeToString,
            ),
            'ValidateToken': grpc.unary_unary_rpc_method_handler(
                    servicer.ValidateToken,
                    request_deserializer=balance__pb2.TokenValidateRequest.FromString,
                    response_serializer=balance__pb2.StandardResponse.SerializeToString,
            ),
            'CommitBettersCoinflip': grpc.unary_unary_rpc_method_handler(
                    servicer.CommitBettersCoinflip,
                    request_deserializer=balance__pb2.CommitBettersCoinflipRequest.FromString,
                    response_serializer=balance__pb2.CommitBettersBalanceResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'balance.Balance', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Balance(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ConfirmBet(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/balance.Balance/ConfirmBet',
            balance__pb2.ConfirmBetRequest.SerializeToString,
            balance__pb2.ConfirmBetResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CommitBettersBalance(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/balance.Balance/CommitBettersBalance',
            balance__pb2.CommitBettersBalanceRequest.SerializeToString,
            balance__pb2.CommitBettersBalanceResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ValidateToken(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/balance.Balance/ValidateToken',
            balance__pb2.TokenValidateRequest.SerializeToString,
            balance__pb2.StandardResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CommitBettersCoinflip(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/balance.Balance/CommitBettersCoinflip',
            balance__pb2.CommitBettersCoinflipRequest.SerializeToString,
            balance__pb2.CommitBettersBalanceResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)