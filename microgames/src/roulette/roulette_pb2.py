# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: roulette.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eroulette.proto\x12\x08roulette\"\x0e\n\x0c\x45mptyRequest\"P\n\x0fPlaceBetRequest\x12\r\n\x05token\x18\x01 \x01(\t\x12\x0c\n\x04\x63oin\x18\x02 \x01(\t\x12\x0e\n\x06\x61mount\x18\x03 \x01(\r\x12\x10\n\x08round_id\x18\x04 \x01(\x04\"N\n\x10StandardResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x11\n\x04\x64\x61ta\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\r\n\x05\x65rror\x18\x03 \x01(\tB\x07\n\x05_data2\x8d\x01\n\x08Roulette\x12\x41\n\x08PlaceBet\x12\x19.roulette.PlaceBetRequest\x1a\x1a.roulette.StandardResponse\x12>\n\x08GetState\x12\x16.roulette.EmptyRequest\x1a\x1a.roulette.StandardResponseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'roulette_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _EMPTYREQUEST._serialized_start=28
  _EMPTYREQUEST._serialized_end=42
  _PLACEBETREQUEST._serialized_start=44
  _PLACEBETREQUEST._serialized_end=124
  _STANDARDRESPONSE._serialized_start=126
  _STANDARDRESPONSE._serialized_end=204
  _ROULETTE._serialized_start=207
  _ROULETTE._serialized_end=348
# @@protoc_insertion_point(module_scope)