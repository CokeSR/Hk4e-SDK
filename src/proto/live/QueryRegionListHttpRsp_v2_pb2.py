# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: QueryRegionListHttpRsp_v2.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import src.proto.live.RegionSimpleInfo_v2_pb2 as RegionSimpleInfo__v2__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fQueryRegionListHttpRsp_v2.proto\x12\nproto.live\x1a\x19RegionSimpleInfo_v2.proto\"\xbe\x01\n\x19QueryRegionListHttpRsp_v2\x12\x0f\n\x07retcode\x18\x01 \x01(\x05\x12\x34\n\x0bregion_list\x18\x02 \x03(\x0b\x32\x1f.proto.live.RegionSimpleInfo_v2\x12\x19\n\x11\x63lient_secret_key\x18\x05 \x01(\x0c\x12&\n\x1e\x63lient_custom_config_encrypted\x18\x06 \x01(\x0c\x12\x17\n\x0f\x65nable_login_pc\x18\x07 \x01(\x08\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'QueryRegionListHttpRsp_v2_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_QUERYREGIONLISTHTTPRSP_V2']._serialized_start=75
  _globals['_QUERYREGIONLISTHTTPRSP_V2']._serialized_end=265
# @@protoc_insertion_point(module_scope)