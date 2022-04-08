
import requests
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import random
import base64
import json
import os


class EncryptText:
    def __init__(self):
        self.character = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        self.iv = '0102030405060708'
        self.public_key = '010001'
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b' \
                       '5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417' \
                       '629ec4ee341f56135fccf695280104e0312ecbda92557c93' \
                       '870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b' \
                       '424d813cfe4875d3e82047b97ddef52741d546b8e289dc69' \
                       '35b3ece0462db0a22b8e7'
        self.nonce = '0CoJUm6Qyw8W8jud'
    def create16RandomBytes(self):
        """
        # 产生16位随机字符, 对应函数a
        :return:
        """
        generate_string = random.sample(self.character, 16)
        generated_string = ''.join(generate_string)
        return generated_string

    def AESEncrypt(self, clear_text, key):
        """
        AES加密, 对应函数b
        :param clear_text: 需要加密的数据
        :return:
        """
        # 数据填充
        clear_text = pad(data_to_pad=clear_text.encode(), block_size=AES.block_size)
        key = key.encode()
        iv = self.iv.encode()
        aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
        cipher_text = aes.encrypt(plaintext=clear_text)
        # 字节串转为字符串
        cipher_texts = base64.b64encode(cipher_text).decode()
        return cipher_texts

    def RSAEncrypt(self, i, e, n):
        """
        RSA加密, 对应函数c
        :param i:
        :return:
        """
        # num = pow(x, y) % z
        # 加密C=M^e mod n
        num = pow(int(i[::-1].encode().hex(), 16), int(e, 16), int(n, 16))
        result = format(num, 'x')
        return result

    def resultEncrypt(self, input_text):
        """
        对应函数d
        :param input_text:
        :return:
        """
        i = self.create16RandomBytes()
        encText = self.AESEncrypt(input_text, self.nonce)
        encText = self.AESEncrypt(encText, i)
        encSecKey = self.RSAEncrypt(i, self.public_key, self.modulus)
        from_data = {
            'params': encText,
            'encSecKey': encSecKey
        }
        return from_data


test = EncryptText()
id = 1901371647
# test = r'{"logs":"[{\"action\":\"sysaction\",\"json\":{\"dataType\":\"cdnCompare\",\"cdnType\":\"NetEase\",\"loadeddataTime\":16408,\"resourceType\":\"audiom4a\",\"resourceId\":167882,\"resourceUrl\":\"https://m801.music.126.net/20220407201734/e6d59ee8c939ff12ac734ff0ad2da8e2/jdyyaac/obj/w5rDlsOJwrLDjj7CmsOj/12826551878/df3f/2f9c/605a/eaef091c62096953856277e8dd94595d.m4a\",\"xySupport\":true,\"error\":false,\"errorType\":\"\",\"ua\":\"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0\"}}]","csrf_token":""}'
lyric = '{"id":"1901371647","lv":-1,"tv":-1,"csrf_token":""}'
meida = '{"ids":"[%s]","level":"standard","encodeType":"aac","csrf_token":""}'%id
comment = '{"rid":"R_SO_4_%s","threadId":"R_SO_4_%s","pageNo":"1","pageSize":"20","cursor":"-1","offset":"0","orderType":"1","csrf_token":""}' %(id ,id)

data = test.resultEncrypt(meida)
response = requests.post(url='https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token=',data=data)

print(response.text)
"""
encText: "/r23t39rQMJ79cD99RtWCn3Lr12IlKgBo4HwzrLWzaUE4mfYqq4g8+wOcvzL2lwgUqQNMgdKgR9+QUPneKX3VE2Kt1RXd/pMjkOjIv3PMTjktP4YROqtnGqHWVd8ZWMZ2wOMJtiHA21VFObLZyHnrQ=="
encSecKey: "4f50ce14f6408be1d2e6e6a40d0556d2d4c9338b3ad783cbd5e5cbf4da75b713e62e85e7355a29a7fa393be3eb22723667dddb783b043547b93ba86f623370f36e7b2bb9b8df3b2d039e70e619d942002f6b11667b44d184d28db9e98ade1c12e3c38b5cf61cd77ae99590f7c3187295e2dec53fc97cdf1e86b4fd2511aa7067"
params: I7JWtWOBU2Y/CN4ep6XNvkLBRjvcnZH83UD7sUvfgmPFDNLCUJqitc1xjjymfBE0RDi0eg7kqJGew3cOqqNeXCpoGZfK/QNBhNpyIljuJ98zLoskrTVH+NoV3ccWvkB4vnyZKrFgmCuwV7I0NmgkQw==
"""

