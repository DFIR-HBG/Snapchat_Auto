# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Snapchat.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='Snapchat.proto',
  package='',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x0eSnapchat.proto\"H\n\x04root\x12\n\n\x02id\x18\x01 \x02(\x04\x12\x19\n\x07\x43ontent\x18\x04 \x02(\x0b\x32\x08.content\x12\x19\n\ntimestamps\x18\x06 \x01(\x0b\x32\x05.time\"%\n\x04time\x12\x0f\n\x07\x63reated\x18\x01 \x02(\x04\x12\x0c\n\x04read\x18\x02 \x01(\x04\"A\n\x07\x63ontent\x12\x17\n\x04\x63hat\x18\x04 \x01(\x0b\x32\t.content2\x12\x1d\n\nstartMedia\x18\x05 \x01(\x0b\x32\t.content2\"Z\n\x08\x63ontent2\x12\x1a\n\x0b\x63hatMessage\x18\x02 \x01(\x0b\x32\x05.text\x12\x17\n\x07unknown\x18\x01 \x01(\x0b\x32\x06.fill1\x12\x19\n\tmediatext\x18\x07 \x01(\x0b\x32\x06.fill1\"<\n\x05\x66ill1\x12\x17\n\x07unknown\x18\x03 \x01(\x0b\x32\x06.fill2\x12\x1a\n\nmediatext2\x18\x0b \x01(\x0b\x32\x06.media\" \n\x05\x66ill2\x12\x17\n\x07unknown\x18\x02 \x01(\x0b\x32\x06.media\"0\n\x05media\x12\x0f\n\x07\x63\x61\x63heId\x18\x02 \x01(\t\x12\x16\n\x0emediatextFinal\x18\x01 \x01(\t\"\x17\n\x04text\x12\x0f\n\x07message\x18\x01 \x01(\t')
)




_ROOT = _descriptor.Descriptor(
  name='root',
  full_name='root',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='root.id', index=0,
      number=1, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='Content', full_name='root.Content', index=1,
      number=4, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamps', full_name='root.timestamps', index=2,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=90,
)


_TIME = _descriptor.Descriptor(
  name='time',
  full_name='time',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='created', full_name='time.created', index=0,
      number=1, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='read', full_name='time.read', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=92,
  serialized_end=129,
)


_CONTENT = _descriptor.Descriptor(
  name='content',
  full_name='content',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='chat', full_name='content.chat', index=0,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='startMedia', full_name='content.startMedia', index=1,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=131,
  serialized_end=196,
)


_CONTENT2 = _descriptor.Descriptor(
  name='content2',
  full_name='content2',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='chatMessage', full_name='content2.chatMessage', index=0,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='unknown', full_name='content2.unknown', index=1,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='mediatext', full_name='content2.mediatext', index=2,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=198,
  serialized_end=288,
)


_FILL1 = _descriptor.Descriptor(
  name='fill1',
  full_name='fill1',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='unknown', full_name='fill1.unknown', index=0,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='mediatext2', full_name='fill1.mediatext2', index=1,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=290,
  serialized_end=350,
)


_FILL2 = _descriptor.Descriptor(
  name='fill2',
  full_name='fill2',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='unknown', full_name='fill2.unknown', index=0,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=352,
  serialized_end=384,
)


_MEDIA = _descriptor.Descriptor(
  name='media',
  full_name='media',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cacheId', full_name='media.cacheId', index=0,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='mediatextFinal', full_name='media.mediatextFinal', index=1,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=386,
  serialized_end=434,
)


_TEXT = _descriptor.Descriptor(
  name='text',
  full_name='text',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='text.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=436,
  serialized_end=459,
)

_ROOT.fields_by_name['Content'].message_type = _CONTENT
_ROOT.fields_by_name['timestamps'].message_type = _TIME
_CONTENT.fields_by_name['chat'].message_type = _CONTENT2
_CONTENT.fields_by_name['startMedia'].message_type = _CONTENT2
_CONTENT2.fields_by_name['chatMessage'].message_type = _TEXT
_CONTENT2.fields_by_name['unknown'].message_type = _FILL1
_CONTENT2.fields_by_name['mediatext'].message_type = _FILL1
_FILL1.fields_by_name['unknown'].message_type = _FILL2
_FILL1.fields_by_name['mediatext2'].message_type = _MEDIA
_FILL2.fields_by_name['unknown'].message_type = _MEDIA
DESCRIPTOR.message_types_by_name['root'] = _ROOT
DESCRIPTOR.message_types_by_name['time'] = _TIME
DESCRIPTOR.message_types_by_name['content'] = _CONTENT
DESCRIPTOR.message_types_by_name['content2'] = _CONTENT2
DESCRIPTOR.message_types_by_name['fill1'] = _FILL1
DESCRIPTOR.message_types_by_name['fill2'] = _FILL2
DESCRIPTOR.message_types_by_name['media'] = _MEDIA
DESCRIPTOR.message_types_by_name['text'] = _TEXT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

root = _reflection.GeneratedProtocolMessageType('root', (_message.Message,), {
  'DESCRIPTOR' : _ROOT,
  '__module__' : 'Snapchat_pb2'
  # @@protoc_insertion_point(class_scope:root)
  })
_sym_db.RegisterMessage(root)

time = _reflection.GeneratedProtocolMessageType('time', (_message.Message,), {
  'DESCRIPTOR' : _TIME,
  '__module__' : 'Snapchat_pb2'
  # @@protoc_insertion_point(class_scope:time)
  })
_sym_db.RegisterMessage(time)

content = _reflection.GeneratedProtocolMessageType('content', (_message.Message,), {
  'DESCRIPTOR' : _CONTENT,
  '__module__' : 'Snapchat_pb2'
  # @@protoc_insertion_point(class_scope:content)
  })
_sym_db.RegisterMessage(content)

content2 = _reflection.GeneratedProtocolMessageType('content2', (_message.Message,), {
  'DESCRIPTOR' : _CONTENT2,
  '__module__' : 'Snapchat_pb2'
  # @@protoc_insertion_point(class_scope:content2)
  })
_sym_db.RegisterMessage(content2)

fill1 = _reflection.GeneratedProtocolMessageType('fill1', (_message.Message,), {
  'DESCRIPTOR' : _FILL1,
  '__module__' : 'Snapchat_pb2'
  # @@protoc_insertion_point(class_scope:fill1)
  })
_sym_db.RegisterMessage(fill1)

fill2 = _reflection.GeneratedProtocolMessageType('fill2', (_message.Message,), {
  'DESCRIPTOR' : _FILL2,
  '__module__' : 'Snapchat_pb2'
  # @@protoc_insertion_point(class_scope:fill2)
  })
_sym_db.RegisterMessage(fill2)

media = _reflection.GeneratedProtocolMessageType('media', (_message.Message,), {
  'DESCRIPTOR' : _MEDIA,
  '__module__' : 'Snapchat_pb2'
  # @@protoc_insertion_point(class_scope:media)
  })
_sym_db.RegisterMessage(media)

text = _reflection.GeneratedProtocolMessageType('text', (_message.Message,), {
  'DESCRIPTOR' : _TEXT,
  '__module__' : 'Snapchat_pb2'
  # @@protoc_insertion_point(class_scope:text)
  })
_sym_db.RegisterMessage(text)


# @@protoc_insertion_point(module_scope)
