answer_type_feedback_base = {
    # "normal_answer": {
    #    "code":100,
    #    "type": "普通回答",
    #    "msg": "系统检索到的相关知识后由大模型生成的一般性答案。"
    # },
    "high_quality_answer": {
        "code": 101,
        "detect_flag": True,
        "type": "高质量回答",
        "msg": "系统搜索到的知识与问题相关度高于阈值，有较大的概率直接完成回答。"
    },
    "sensitive_information": {
        "code": 102,
        "detect_flag": True,
         "type": "涉敏问题",
         "msg": "系统识别到问题涉及敏感词，系统将回答问题涉及敏感信息，系统无法回答。"
    },
    "recall_missing": {
        "code": 103,
        "detect_flag": True,
         "type": "系统不知道",
         "msg": "系统搜索到的知识与问题无关，被全部过滤，系统将回答不知道。"
    },
    "query_not_understand": {
        "code": 104,
        "detect_flag": True,
         "type": "回答置信度低",
         "msg": "大模型生成的答案与问题相关度低于阈值，系统将回答不知道。"
    },
    "duplicate_generation": {
        "code": 105,
        "detect_flag": True,
         "type": "生成重复性内容",
         "msg": "系统动态检测输出内容，识别生成的重复性内容。"
    },
    # "without_permission": {
    #    "code":106,
    #    "type": "知识无权限",
    #    "msg": "系统已经识别到该知识，但由于标签或者过期时间的访问限制，系统将回答用户无权访问该知识。"
    # },
    "similar_answer": {
        "code": 107,
        "detect_flag": True,
        "type": "相似内容回答",
        "msg": "系统可成功识别您的问题，但是并未找到可直接回答您问题的知识，因此引用了相似内容供您参考。"
    }

}