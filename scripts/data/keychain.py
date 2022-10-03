################################################################################################
#                                                                                              #
# UFED keychain decrypter                                                                      #
#                                                                                              #
# Copyright Matthieu Regnery 2020                                                              #
#                                                                                              #
# This program is free software: you can redistribute it and/or modify                         #
# it under the terms of the GNU General Public License as published by                         #
# the Free Software Foundation, either version 3 of the License, or                            #
# (at your option) any later version.                                                          #
#                                                                                              #
# This program is distributed in the hope that it will be useful,                              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                #
# GNU General Public License for more details.                                                 #
#                                                                                              #
# You should have received a copy of the GNU General Public License                            #
# along with this program.  If not, see <https://www.gnu.org/licenses/>.                       #
################################################################################################

# !!!!!!!!
#
#  Require ccl_bplist
#  https://github.com/cclgroupltd/ccl-bplist
#
# !!!!!!!!

import pandas
from struct import unpack
import subprocess
import sys
import os
from binascii import hexlify, unhexlify
from scripts.data import ccl_bplist
from io import BytesIO
from Crypto.Cipher import AES
from pyasn1.codec.der.decoder import decode
from base64 import b64encode, b64decode
import plistlib

DEFAULT_UFED_KEYCHAIN = 'backup_keychain_v2.plist'
DEFAULT_GK_KEYCHAIN = 'gk_keychain.plist'

# itemV7 has two main parts:
# 1. secretData containing password or key
# 2. metaData containing key/password name (ie acct)
# decrypt secretData by :
# - unwrapping key 
# - decrypting with AES GCM
# - parsing resulting ASN1 DER
def decrypt_secretData(item):
	bplist = BytesIO(item['ciphertext'])
	plist = ccl_bplist.load(bplist)
	secretDataDeserialized = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
	authCode = secretDataDeserialized['root']['SFAuthenticationCode']
	iv   = secretDataDeserialized['root']['SFInitializationVector']
	ciphertext = secretDataDeserialized['root']['SFCiphertext']

	gcm = AES.new(item['unwrappedKey'][:32], AES.MODE_GCM, iv)
	decrypted = gcm.decrypt_and_verify(ciphertext, authCode)

	der_data = decode(decrypted)[0]
	secret = {}
	for k in der_data:
		if 'Octet' in str(type(k[1])):
			secret[str(k[0])] = bytes(k[1])
		else:
			secret[str(k[0])] = bytes(k[1])
	return secret


# decrypt Metadata by :
# - unwrapping metadata key 
# - decrypting metadata key with AES GCM
# - decrypting metadata with AES GCM
# - parsing resulting ASN1 DER
def decrypt_Metadata(item, unwrapped_metadata_key):
	bplist = BytesIO(item['wrappedKey'])
	plist = ccl_bplist.load(bplist)
	metaDataWrappedKeyDeserialized = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
	authCode = metaDataWrappedKeyDeserialized['root']['SFAuthenticationCode']
	iv   = metaDataWrappedKeyDeserialized['root']['SFInitializationVector']
	ciphertext = metaDataWrappedKeyDeserialized['root']['SFCiphertext']
	gcm = AES.new(unwrapped_metadata_key[:32], AES.MODE_GCM, iv)
	metadata_key = gcm.decrypt_and_verify(ciphertext, authCode)

	bplist = BytesIO(item['ciphertext'])
	plist = ccl_bplist.load(bplist)
	metaDataDeserialized = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
	authCode = metaDataDeserialized['root']['SFAuthenticationCode']
	iv   = metaDataDeserialized['root']['SFInitializationVector']
	ciphertext = metaDataDeserialized['root']['SFCiphertext']

	gcm = AES.new(metadata_key[:32], AES.MODE_GCM, iv)
	decrypted = gcm.decrypt_and_verify(ciphertext, authCode)
	der_data = decode(decrypted)[0]
	meta={}
	for k in der_data:
		if 'Octet' in str(type(k[1])):
			meta[str(k[0])] = bytes(k[1])
		else:
			meta[str(k[0])] = str(k[1])

	return meta

def main(input_keychain, output_keychain):
	#input_keychain = DEFAULT_UFED_KEYCHAIN
	#output_keychain = DEFAULT_GK_KEYCHAIN
	#if len(sys.argv) > 1:
	#	input_keychain = sys.argv[1]
	#if len(sys.argv) > 2:
	#	output_keychain = sys.argv[2]

	if not os.path.exists(input_keychain):
		raise IOError("Can not find input keychain in {}".format(input_keychain))

	with open(input_keychain,'rb') as fp:
		ufed_plist = plistlib.load(fp, fmt=plistlib.FMT_XML)

	metaDataKeys = ufed_plist['classKeyIdxToUnwrappedMetadataClassKey']

	keychainList = []
	for item in ufed_plist['keychainEntries']:
		if 'rawData' in item:
			continue
		res=decrypt_Metadata(item['metadata'], metaDataKeys[str(item['classKeyIdx'])])
		res.update(decrypt_secretData(item['data']))
		keychainList.append(res)

	with open(output_keychain, "wb") as out:
		plistlib.dump(keychainList, out, sort_keys=False )

if __name__ == "__main__":
    main()
