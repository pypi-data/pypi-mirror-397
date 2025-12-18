import json
import hashlib

import lark_oapi as lark
from lark_oapi.api.im.v1 import *

from feishu_tools import setting


class FeishuServer:
    def __init__(self, app_id: str = setting.FEISHU_APP_ID, app_secret: str = setting.FEISHU_APP_SECRET):
        # 创建client
        self.__client__ = lark.Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()

    def send_message(self, receive_id: str, content: str, receive_id_type: str = 'chat_id', msg_type: str = 'text'):
        """
        send_message 的 Docstring
        参考文档：https://open.feishu.cn/document/server-docs/im-v1/message/create

        :param self: 说明
        :param receive_id: 说明
        :type receive_id: str
        :param content: 说明
        :type content: str
        :param receive_id_type: 说明
        :type receive_id_type: str
        :param msg_type: 说明
        :type msg_type: str
        """
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type(receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(receive_id)
                          .msg_type(msg_type)
                          .content(content)
                          # 每次调用前请更换
                          .uuid(hashlib.md5(f"{receive_id},{receive_id_type},{msg_type},{content}".encode("utf-8")).hexdigest())
                          .build()) \
            .build()

        # 发起请求
        response: CreateMessageResponse = self.__client__.im.v1.message.create(
            request)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    def send_template_card(self, receive_id: str, card_id: str, card_version: str, receive_id_type: str = 'chat_id', variable: dict = {}):
        """
        发送卡片消息

        发送消息参考：https://open.feishu.cn/document/server-docs/im-v1/message/create
        飞书卡片参考：https://open.feishu.cn/cardkit

        :param receive_id: 接收者ID
        :param card_id: 卡片ID
        :param card_version: 卡片版本
        :param receive_id_type: 接收者类型
        :param variable: 卡片变量
        """
        card_body = {
            "type": "template",
            "data": {
                    "template_id": card_id,
                    "template_version_name": card_version,
                    "template_variable": variable
            }
        }
        self.send_message(receive_id, json.dumps(card_body),
                          receive_id_type, msg_type='interactive')

    def get_chat_list(self, page_token: str = None):
        """
        获取 access_token 所代表的用户或者机器人所在的群列表。
        参考文档：https://open.feishu.cn/document/server-docs/group/chat/list

        :param self: 说明
        :param page_token: 说明
        :type page_token: str
        """
        # 构造请求对象
        request: ListChatRequest = ListChatRequest.builder() \
            .user_id_type("open_id") \
            .sort_type("ByCreateTimeAsc") \
            .page_size(100) \
            .build()
        if page_token:
            request.page_token = page_token

        # 发起请求
        response: ListChatResponse = self.__client__.im.v1.chat.list(request)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.im.v1.chat.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return []

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data


if __name__ == '__main__':
    feishu = FeishuServer()
    chat_list = feishu.get_chat_list()
    for chat in chat_list.items:
        feishu.send_message(chat.chat_id, json.dumps(
            {"text": "Hello from FeishuServer!"}))
