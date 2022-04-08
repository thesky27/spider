import base64
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
class eneryctAES():
    character = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    iv = '0102030405060708'
    public_key = '010001'
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b' \
                       '5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417' \
                       '629ec4ee341f56135fccf695280104e0312ecbda92557c93' \
                       '870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b' \
                       '424d813cfe4875d3e82047b97ddef52741d546b8e289dc69' \
                       '35b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'

    lyric = '{"id":"%s","lv":-1,"tv":-1,"csrf_token":""}'
    meida = '{"ids":"[%s]","level":"standard","encodeType":"aac","csrf_token":""}'
    comment = '{"rid":"R_SO_4_%s","threadId":"R_SO_4_%s","pageNo":"1","pageSize":"20","cursor":"-1","offset":"0","orderType":"1","csrf_token":""}'

    comment_url = 'https://music.163.com/weapi/comment/resource/comments/get?csrf_token='
    meida_url = 'https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token='
    lyric_url = 'https://music.163.com/weapi/song/lyric?csrf_token='

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
