# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: coinflip.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x63oinflip.proto\x12\x08\x63oinflip\"N\n\x10StandardResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x11\n\x04\x64\x61ta\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\r\n\x05\x65rror\x18\x03 \x01(\tB\x07\n\x05_data\"D\n\x11\x43reateGameRequest\x12\x12\n\nbet_amount\x18\x01 \x01(\r\x12\x0c\n\x04side\x18\x02 \x01(\r\x12\r\n\x05token\x18\x03 \x01(\t\"9\n\x16\x41\x63\x63\x65ptChallengeRequest\x12\x10\n\x08round_id\x18\x01 \x01(\x04\x12\r\n\x05token\x18\x02 \x01(\t\"4\n\x11\x43\x61ncelGameRequest\x12\x10\n\x08round_id\x18\x01 \x01(\x04\x12\r\n\x05token\x18\x02 \x01(\t2\xe9\x01\n\x08\x43oinflip\x12\x45\n\nCreateGame\x12\x1b.coinflip.CreateGameRequest\x1a\x1a.coinflip.StandardResponse\x12O\n\x0f\x41\x63\x63\x65ptChallenge\x12 .coinflip.AcceptChallengeRequest\x1a\x1a.coinflip.StandardResponse\x12\x45\n\nCancelGame\x12\x1b.coinflip.CancelGameRequest\x1a\x1a.coinflip.StandardResponseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'coinflip_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _STANDARDRESPONSE._serialized_start=28
  _STANDARDRESPONSE._serialized_end=106
  _CREATEGAMEREQUEST._serialized_start=108
  _CREATEGAMEREQUEST._serialized_end=176
  _ACCEPTCHALLENGEREQUEST._serialized_start=178
  _ACCEPTCHALLENGEREQUEST._serialized_end=235
  _CANCELGAMEREQUEST._serialized_start=237
  _CANCELGAMEREQUEST._serialized_end=289
  _COINFLIP._serialized_start=292
  _COINFLIP._serialized_end=525
# @@protoc_insertion_point(module_scope)